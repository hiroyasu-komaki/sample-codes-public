#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
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
from similarity_insights import SimilarityInsightsGenerator  # 変更

class ProjectSignalAnalyzer:
    """プロジェクトシグナル分析クラス"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load_config()
        self._setup_logging()
        
        # シグナル属性の定義（config.yamlから取得）
        self.signal_attributes = self.config_loader.get_signal_attributes()
        self.logger.info(f"シグナル属性: {self.signal_attributes}")
        
        # クラスタリング結果を保存
        self.cluster_results = {}
        
        # 出力ディレクトリの設定
        self.output_directory = "png"
        
        # 類似度分析ジェネレーターの初期化
        self.insights_generator = SimilarityInsightsGenerator(self.output_directory)
    
    def _setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def prepare_signal_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        シグナル属性データの準備
        
        Args:
            df (pd.DataFrame): 元のプロジェクトデータ
        
        Returns:
            pd.DataFrame: エンコード済みシグナルデータ
        """
        # シグナル属性の存在確認
        missing_attributes = [attr for attr in self.signal_attributes if attr not in df.columns]
        if missing_attributes:
            raise ValueError(f"必要なシグナル属性が不足しています: {missing_attributes}")
        
        # シグナル属性の抽出
        signal_df = df[self.signal_attributes].copy()
        
        # カテゴリカルデータのワンホットエンコーディング
        encoded_df = pd.get_dummies(signal_df, prefix=self.signal_attributes, drop_first=False)
        
        self.logger.info(f"シグナルデータ準備完了: {len(self.signal_attributes)}属性 → {encoded_df.shape[1]}次元")
        
        return encoded_df
    
    def perform_hierarchical_clustering(self, data: pd.DataFrame, 
                                      original_df: pd.DataFrame,
                                      max_display_samples: int = 50) -> Dict:
        """
        階層クラスタリングの実行とデンドログラム生成
        
        Args:
            data (pd.DataFrame): エンコード済みシグナルデータ
            original_df (pd.DataFrame): 元のデータ(ラベル用)
            max_display_samples (int): デンドログラムに表示する最大サンプル数
        
        Returns:
            Dict: クラスタリング結果
        """
        # サンプル数が多い場合は一部のみを表示用に使用
        if len(data) > max_display_samples:
            sample_indices = np.random.choice(len(data), max_display_samples, replace=False)
            display_data = data.iloc[sample_indices]
            
            # プロジェクトIDをそのまま使用
            display_labels = self._generate_project_id_labels(original_df.iloc[sample_indices])
            self.logger.info(f"シグナル デンドログラム表示用に{max_display_samples}サンプルを選択")
        else:
            display_data = data
            display_labels = self._generate_project_id_labels(original_df)
        
        # 距離行列の計算(シグナルデータにはJaccard距離を使用)
        distances = pdist(display_data, metric='jaccard')
        
        # 階層クラスタリングの実行
        linkage_matrix = linkage(distances, method='average')  # シグナルデータには average linkage
        
        # デンドログラムの生成と保存
        self._create_signal_dendrogram(linkage_matrix, display_labels)
        
        results = {
            'method': 'hierarchical',
            'linkage_matrix': linkage_matrix,
            'sample_used_for_dendrogram': len(display_data),
            'total_samples': len(data)
        }
        
        self.cluster_results['hierarchical'] = results
        self.logger.info(f"シグナル 階層クラスタリング完了: デンドログラム生成(PNGファイル出力)")
        
        return results
    
    def generate_similarity_insights(self, encoded_data: pd.DataFrame, 
                                     original_df: pd.DataFrame,
                                     similarity_threshold: float = 0.7):
        """
        類似度分析の生成
        
        Args:
            encoded_data (pd.DataFrame): エンコード済みシグナルデータ
            original_df (pd.DataFrame): 元のデータ
            similarity_threshold (float): 高類似度の閾値
        """
        self.logger.info("類似度分析を開始")
        
        # 類似度分析の実行
        results = self.insights_generator.generate_complete_similarity_analysis(
            encoded_data,
            original_df,
            similarity_threshold=similarity_threshold
        )
        
        self.logger.info("類似度分析が完了")
        
        return results
    
    def _generate_project_id_labels(self, df_subset: pd.DataFrame) -> List[str]:
        """
        プロジェクトIDをそのまま使用したラベルを生成
        
        Args:
            df_subset (pd.DataFrame): データのサブセット
        
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
    
    def _create_signal_dendrogram(self, linkage_matrix: np.ndarray, labels: List[str]):
        """
        シグナル分析用デンドログラムを生成してPNGファイルに保存
        
        Args:
            linkage_matrix (np.ndarray): リンケージ行列
            labels (List[str]): サンプルラベル
        """
        # 出力ディレクトリの作成
        os.makedirs(self.output_directory, exist_ok=True)
        
        # 図のサイズを調整(サンプル数に応じて)
        n_samples = len(labels)
        fig_width = max(12, n_samples * 0.3)
        fig_height = max(8, n_samples * 0.1)
        
        plt.figure(figsize=(fig_width, fig_height))
        
        # デンドログラムの描画
        dendrogram(
            linkage_matrix,
            labels=labels,
            orientation='top',
            distance_sort='descending',
            show_leaf_counts=True,
            leaf_rotation=90,
            leaf_font_size=8
        )
        
        plt.title('Signal Clustering Dendrogram\n(Signal Attributes Analysis)', 
                 fontsize=14, fontweight='bold')
        plt.xlabel('Project IDs', fontsize=12)
        plt.ylabel('Jaccard Distance', fontsize=12)
        
        # グリッドを追加
        plt.grid(True, alpha=0.3)
        
        # レイアウトの調整
        plt.tight_layout()
        
        # PNGファイルとして保存
        dendrogram_path = os.path.join(self.output_directory, 'signal_dendrogram.png')
        plt.savefig(dendrogram_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()  # メモリ解放
        
        self.logger.info(f"シグナル デンドログラムを保存: {dendrogram_path}")
    
    def save_integrated_data(self, df: pd.DataFrame, filename: str = "integrated_projects.csv"):
        """
        統合データをCSVファイルに保存
        
        Args:
            df (pd.DataFrame): 統合データ
            filename (str): ファイル名
        """
        # 出力ディレクトリの作成
        os.makedirs(self.output_directory, exist_ok=True)
        
        # ファイルパスの作成
        filepath = os.path.join(self.output_directory, filename)
        
        # CSV保存
        df.to_csv(filepath, index=False, encoding='utf-8')
        self.logger.info(f"シグナル統合データを保存: {filepath} ({len(df)} レコード)")
    
    def run_complete_signal_analysis(self, data_directory: str = "projects"):
        """
        完全なシグナル分析の実行
        
        Args:
            data_directory (str): データディレクトリのパス
        """
        # データの読み込み
        data_loader = DataLoader(data_directory)
        df = data_loader.load_all_csv_files()
        cleaned_df = data_loader.clean_data(df)
        
        # シグナルデータの準備
        signal_data = self.prepare_signal_data(cleaned_df)
        
        # 階層クラスタリング（デンドログラム生成）
        hierarchical_results = self.perform_hierarchical_clustering(signal_data, cleaned_df)
        
        # 類似度分析の生成（追加）
        similarity_results = self.generate_similarity_insights(
            signal_data, 
            cleaned_df,
            similarity_threshold=0.7
        )
        
        self.logger.info("シグナル分析が完了しました")
        self.logger.info(f"出力ファイル:")
        self.logger.info(f"  - {self.output_directory}/signal_dendrogram.png")
        self.logger.info(f"  - {self.output_directory}/similarity_scatter_tsne.png")
        self.logger.info(f"  - {self.output_directory}/high_similarity_pairs.csv")
        self.logger.info(f"  - {self.output_directory}/top_similar_projects.csv")

# 使用例とテスト用の関数
def test_signal_analyzer():
    """シグナル分析のテスト"""
    try:
        analyzer = ProjectSignalAnalyzer()
        analyzer.run_complete_signal_analysis()
        
        print("✅ シグナル分析が正常に完了しました")
        print(f"✅ 結果ファイルは '{analyzer.output_directory}' フォルダに保存されました")
        print(f"   - signal_dendrogram.png: デンドログラム")
        print(f"   - similarity_scatter_tsne.png: t-SNE散布図")
        print(f"   - high_similarity_pairs.csv: 高類似度ペアリスト")
        print(f"   - top_similar_projects.csv: 各プロジェクトのTOP5類似プロジェクト")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_signal_analyzer()