#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Dict, List, Optional, Tuple, Any
import logging
import warnings
import os
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist
warnings.filterwarnings('ignore')

from config_loader import ConfigLoader
from data_loader import DataLoader

class ProjectPortfolioAnalyzer:
    """プロジェクトポートフォリオ分析クラス"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load_config()
        self._setup_logging()
        
        # ポートフォリオ属性の定義（config.yamlから取得）
        self.portfolio_attributes = self.config_loader.get_portfolio_attributes()
        self.logger.info(f"ポートフォリオ属性: {self.portfolio_attributes}")
        
        # 複雑度は別途処理(カテゴリカル)
        self.categorical_attributes = ['complexity']
        
        # スケーラーとクラスタリング結果を保存
        self.scaler = None
        self.scaled_data = None
        self.cluster_results = {}
        
        # 出力ディレクトリの設定
        self.output_directory = "png"
    
    def _setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        クラスタ分析用のデータ準備
        
        Args:
            df (pd.DataFrame): 元のプロジェクトデータ
        
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (数値属性データ, カテゴリカルデータ)
        """
        # ポートフォリオ属性の存在確認
        missing_attributes = [attr for attr in self.portfolio_attributes if attr not in df.columns]
        if missing_attributes:
            raise ValueError(f"必要な属性が不足しています: {missing_attributes}")
        
        # 数値属性の抽出
        numeric_df = df[self.portfolio_attributes].copy()
        
        # 欠損値の処理
        if numeric_df.isnull().any().any():
            self.logger.warning("欠損値を中央値で補完します")
            numeric_df = numeric_df.fillna(numeric_df.median())
        
        # カテゴリカル属性の処理
        categorical_df = pd.DataFrame()
        if 'complexity' in df.columns:
            categorical_df['complexity'] = df['complexity']
            # ダミー変数化
            complexity_dummies = pd.get_dummies(categorical_df['complexity'], prefix='complexity')
            categorical_df = pd.concat([categorical_df, complexity_dummies], axis=1)
        
        self.logger.info(f"準備完了: 数値属性 {numeric_df.shape[1]}個, カテゴリカル属性 {categorical_df.shape[1]}個")
        
        return numeric_df, categorical_df
    
    def normalize_data(self, numeric_df: pd.DataFrame, method: str = 'config_based') -> pd.DataFrame:
        """
        データの正規化
        
        Args:
            numeric_df (pd.DataFrame): 数値属性データ
            method (str): 正規化方法 ('standard', 'minmax', 'config_based')
        
        Returns:
            pd.DataFrame: 正規化済みデータ
        """
        if method == 'config_based':
            # config.yamlの設定を使用した正規化
            normalized_df = self._normalize_with_config(numeric_df)
        elif method == 'standard':
            self.scaler = StandardScaler()
            normalized_df = pd.DataFrame(
                self.scaler.fit_transform(numeric_df),
                columns=numeric_df.columns,
                index=numeric_df.index
            )
        elif method == 'minmax':
            self.scaler = MinMaxScaler()
            normalized_df = pd.DataFrame(
                self.scaler.fit_transform(numeric_df),
                columns=numeric_df.columns,
                index=numeric_df.index
            )
        else:
            raise ValueError(f"未対応の正規化方法: {method}")
        
        self.scaled_data = normalized_df
        self.logger.info(f"データ正規化完了: {method}方式")
        
        return normalized_df
    
    def _normalize_with_config(self, numeric_df: pd.DataFrame) -> pd.DataFrame:
        """
        設定ファイルに基づいた正規化
        
        Args:
            numeric_df (pd.DataFrame): 数値属性データ
        
        Returns:
            pd.DataFrame: 正規化済みデータ
        """
        normalized_df = numeric_df.copy()
        
        # 設定から正規化パラメータを取得
        normalization_config = self.config.get('complexity_calculation', {}).get('normalization', {})
        
        # 各属性の正規化
        if 'duration' in normalized_df.columns and 'duration_max' in normalization_config:
            normalized_df['duration'] = normalized_df['duration'] / normalization_config['duration_max']
        
        if 'stakeholders' in normalized_df.columns and 'stakeholders_max' in normalization_config:
            normalized_df['stakeholders'] = normalized_df['stakeholders'] / normalization_config['stakeholders_max']
        
        if 'budget' in normalized_df.columns and 'budget_max' in normalization_config:
            normalized_df['budget'] = normalized_df['budget'] / normalization_config['budget_max']
        
        # 1-5スケールの属性(strategic_alignment, risk, urgency, importance)
        scale_5_attrs = ['strategic_alignment', 'risk', 'urgency', 'importance']
        for attr in scale_5_attrs:
            if attr in normalized_df.columns:
                normalized_df[attr] = (normalized_df[attr] - 1) / 4  # 0-1スケールに変換
        
        # ROIは個別処理(パーセンテージなので100で割る)
        if 'roi' in normalized_df.columns:
            normalized_df['roi'] = normalized_df['roi'] / 100
        
        self.logger.info("設定ファイルベースの正規化を適用しました")
        
        return normalized_df
    
    def perform_hierarchical_clustering(self, data: pd.DataFrame, 
                                      original_df: pd.DataFrame,
                                      max_display_samples: int = 50) -> Dict:
        """
        階層クラスタリングの実行とデンドログラム生成
        
        Args:
            data (pd.DataFrame): 正規化済みデータ
            original_df (pd.DataFrame): 元のデータ(ラベル用)
            max_display_samples (int): デンドログラムに表示する最大サンプル数
        
        Returns:
            Dict: クラスタリング結果
        """
        # サンプル数が多い場合は一部のみを表示用に使用
        if len(data) > max_display_samples:
            sample_indices = np.random.choice(len(data), max_display_samples, replace=False)
            display_data = data.iloc[sample_indices]
            
            # よりよみやすいラベルを生成
            display_labels = self._generate_readable_labels(original_df.iloc[sample_indices], sample_indices)
            self.logger.info(f"デンドログラム表示用に{max_display_samples}サンプルを選択")
        else:
            display_data = data
            display_labels = self._generate_readable_labels(original_df, range(len(data)))
        
        # 距離行列の計算
        distances = pdist(display_data, metric='euclidean')
        
        # 階層クラスタリングの実行
        linkage_matrix = linkage(distances, method='ward')
        
        # デンドログラムの生成と保存
        self._create_dendrogram(linkage_matrix, display_labels)
        
        results = {
            'method': 'hierarchical',
            'linkage_matrix': linkage_matrix,
            'sample_used_for_dendrogram': len(display_data),
            'total_samples': len(data)
        }
        
        self.cluster_results['hierarchical'] = results
        self.logger.info(f"階層クラスタリング完了: デンドログラム生成(PNGファイル出力)")
        
        return results
    
    def _generate_readable_labels(self, df_subset: pd.DataFrame, indices: range) -> List[str]:
        """
        プロジェクトIDをそのまま使用したラベルを生成
        
        Args:
            df_subset (pd.DataFrame): データのサブセット
            indices (range): インデックス範囲
        
        Returns:
            List[str]: プロジェクトIDのリスト
        """
        labels = []
        
        for i, (idx, row) in enumerate(df_subset.iterrows()):
            # プロジェクトIDがある場合はそれを使用
            if 'project_id' in row and pd.notna(row['project_id']):
                project_id = str(row['project_id'])
            else:
                # フォールバック: インデックスベースのID
                project_id = f"P{idx:03d}"
            
            labels.append(project_id)
        
        return labels
    
    def _create_dendrogram(self, linkage_matrix: np.ndarray, labels: List[str]):
        """
        デンドログラムを生成してPNGファイルに保存
        
        Args:
            linkage_matrix (np.ndarray): リンケージ行列
            labels (List[str]): サンプルラベル
        """
        # 出力ディレクトリの作成
        os.makedirs(self.output_directory, exist_ok=True)
        
        # 図のサイズを調整(サンプル数に応じて)
        n_samples = len(labels)
        fig_width = max(15, n_samples * 0.4)
        fig_height = max(10, n_samples * 0.15)
        
        plt.figure(figsize=(fig_width, fig_height))
        
        # デンドログラムの描画
        dendrogram(
            linkage_matrix,
            labels=labels,
            orientation='top',
            distance_sort='descending',
            show_leaf_counts=True,
            leaf_rotation=90,  # 90度回転でハッシュIDも読みやすく
            leaf_font_size=8
        )
        
        plt.title('Project Portfolio Hierarchical Clustering', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Project IDs', fontsize=12)
        plt.ylabel('Distance', fontsize=12)
        
        # グリッドを追加
        plt.grid(True, alpha=0.3, axis='y')
        
        # レイアウトの調整
        plt.tight_layout()
        
        # PNGファイルとして保存
        dendrogram_path = os.path.join(self.output_directory, 'portfolio_dendrogram.png')
        plt.savefig(dendrogram_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()  # メモリ解放
        
        self.logger.info(f"デンドログラムを保存: {dendrogram_path}")
    
    def save_integrated_data(self, df: pd.DataFrame, 
                            output_dir: str = "data",
                            filename: str = "integrated_projects.csv"):
        """
        統合データをCSVファイルに保存
        
        Args:
            df (pd.DataFrame): 統合データ
            output_dir (str): 出力ディレクトリ
            filename (str): ファイル名
        """
        # 出力ディレクトリの作成
        os.makedirs(output_dir, exist_ok=True)
        
        # ファイルパスの作成
        filepath = os.path.join(output_dir, filename)
        
        # CSV保存
        df.to_csv(filepath, index=False, encoding='utf-8')
        self.logger.info(f"統合データを保存: {filepath} ({len(df)} レコード)")
    
    def run_complete_analysis(self, data_directory: str = "projects", 
                             save_integrated: bool = True):
        """
        完全なポートフォリオ分析の実行
        
        Args:
            data_directory (str): データディレクトリのパス
            save_integrated (bool): 統合データを保存するかどうか
        """
        # データの読み込み
        data_loader = DataLoader(data_directory)
        df = data_loader.load_all_csv_files()
        cleaned_df = data_loader.clean_data(df)
        
        # 統合データの保存(最初の分析でのみ保存)
        if save_integrated:
            self.save_integrated_data(cleaned_df, output_dir="data")
        
        # データの準備
        numeric_df, categorical_df = self.prepare_data(cleaned_df)
        
        # データの正規化
        normalized_df = self.normalize_data(numeric_df)
        
        # 階層クラスタリング
        hierarchical_results = self.perform_hierarchical_clustering(normalized_df, cleaned_df)
        
        self.logger.info("ポートフォリオ分析が完了しました")

# 使用例とテスト用の関数
def test_portfolio_analyzer():
    """ポートフォリオ分析のテスト"""
    try:
        analyzer = ProjectPortfolioAnalyzer()
        analyzer.run_complete_analysis()
        
        print("✅ ポートフォリオ分析が正常に完了しました")
        print(f"✅ 結果ファイルは '{analyzer.output_directory}' フォルダに保存されました")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    test_portfolio_analyzer()
