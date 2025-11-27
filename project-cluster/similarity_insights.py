#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from sklearn.manifold import TSNE
import logging
import os
from typing import List, Tuple, Dict

class SimilarityInsightsGenerator:
    """プロジェクト類似度の洞察生成クラス"""
    
    def __init__(self, output_directory: str = "png", csv_output_directory: str = "data"):
        """
        初期化
        
        Args:
            output_directory (str): 画像出力ディレクトリ
            csv_output_directory (str): CSV出力ディレクトリ
        """
        self.output_directory = output_directory
        self.csv_output_directory = csv_output_directory
        self._setup_logging()
        os.makedirs(self.output_directory, exist_ok=True)
        os.makedirs(self.csv_output_directory, exist_ok=True)
    
    def _setup_logging(self):
        """ログ設定"""
        self.logger = logging.getLogger(__name__)
    
    def calculate_jaccard_similarity_matrix(self, encoded_data: pd.DataFrame) -> np.ndarray:
        """
        Jaccard類似度行列を計算
        
        Args:
            encoded_data (pd.DataFrame): ワンホットエンコード済みデータ
        
        Returns:
            np.ndarray: 類似度行列 (n x n)
        """
        self.logger.info(f"類似度行列の計算開始: {len(encoded_data)} プロジェクト")
        
        # Jaccard距離を計算
        distances = pdist(encoded_data, metric='jaccard')
        
        # 距離を類似度に変換 (類似度 = 1 - 距離)
        similarity_vector = 1 - distances
        
        # 正方行列に変換
        similarity_matrix = squareform(similarity_vector)
        
        # 対角成分を1に設定(自分自身との類似度)
        np.fill_diagonal(similarity_matrix, 1.0)
        
        self.logger.info(f"類似度行列の計算完了: {similarity_matrix.shape}")
        
        return similarity_matrix
    
    def extract_high_similarity_pairs(self, 
                                     similarity_matrix: np.ndarray,
                                     project_labels: List[str],
                                     original_df: pd.DataFrame,
                                     encoded_data: pd.DataFrame,
                                     threshold: float = 0.7) -> pd.DataFrame:
        """
        高類似度プロジェクトペアを抽出
        
        Args:
            similarity_matrix (np.ndarray): 類似度行列
            project_labels (List[str]): プロジェクトラベル
            original_df (pd.DataFrame): 元のデータ
            encoded_data (pd.DataFrame): エンコード済みデータ
            threshold (float): 類似度の閾値
        
        Returns:
            pd.DataFrame: 高類似度ペアのリスト
        """
        self.logger.info(f"高類似度ペアの抽出開始 (閾値: {threshold})")
        
        pairs = []
        n = len(similarity_matrix)
        
        # 上三角行列のみを処理(重複を避けるため)
        for i in range(n):
            for j in range(i + 1, n):
                similarity = similarity_matrix[i, j]
                
                if similarity >= threshold:
                    # 共通属性の特定
                    common_attrs = self._identify_common_attributes(
                        encoded_data.iloc[i],
                        encoded_data.iloc[j]
                    )
                    
                    pairs.append({
                        'project_1': project_labels[i],
                        'project_2': project_labels[j],
                        'similarity': similarity,
                        'common_attributes_count': len(common_attrs),
                        'common_attributes': ', '.join(common_attrs[:5])  # 最大5つまで表示
                    })
        
        # DataFrameに変換して類似度でソート
        pairs_df = pd.DataFrame(pairs)
        
        if len(pairs_df) > 0:
            pairs_df = pairs_df.sort_values('similarity', ascending=False).reset_index(drop=True)
            self.logger.info(f"高類似度ペアを {len(pairs_df)} 組抽出しました")
        else:
            self.logger.warning(f"閾値 {threshold} 以上の類似ペアが見つかりませんでした")
        
        return pairs_df
    
    def _identify_common_attributes(self, vector1: pd.Series, vector2: pd.Series) -> List[str]:
        """
        2つのワンホットエンコードベクトルから共通属性を特定
        
        Args:
            vector1 (pd.Series): プロジェクト1のベクトル
            vector2 (pd.Series): プロジェクト2のベクトル
        
        Returns:
            List[str]: 共通属性のリスト
        """
        common = []
        
        for col in vector1.index:
            if vector1[col] == 1 and vector2[col] == 1:
                common.append(col)
        
        return common
    
    def generate_top_similar_projects(self,
                                     similarity_matrix: np.ndarray,
                                     project_labels: List[str],
                                     top_n: int = 5) -> pd.DataFrame:
        """
        各プロジェクトの最も類似したTOP-Nプロジェクトを生成
        
        Args:
            similarity_matrix (np.ndarray): 類似度行列
            project_labels (List[str]): プロジェクトラベル
            top_n (int): 上位何件を抽出するか
        
        Returns:
            pd.DataFrame: 各プロジェクトのTOP類似プロジェクト
        """
        self.logger.info(f"各プロジェクトのTOP-{top_n}類似プロジェクトを生成中")
        
        results = []
        
        for i, project in enumerate(project_labels):
            # 自分自身を除外して類似度を取得
            similarities = similarity_matrix[i].copy()
            similarities[i] = -1  # 自分自身を除外
            
            # TOP-N のインデックスを取得
            top_indices = np.argsort(similarities)[-top_n:][::-1]
            
            # 結果を構築
            similar_projects = []
            similar_scores = []
            
            for idx in top_indices:
                similar_projects.append(project_labels[idx])
                similar_scores.append(similarities[idx])
            
            results.append({
                'project_id': project,
                'top_1_similar': similar_projects[0] if len(similar_projects) > 0 else '',
                'top_1_score': similar_scores[0] if len(similar_scores) > 0 else 0,
                'top_2_similar': similar_projects[1] if len(similar_projects) > 1 else '',
                'top_2_score': similar_scores[1] if len(similar_scores) > 1 else 0,
                'top_3_similar': similar_projects[2] if len(similar_projects) > 2 else '',
                'top_3_score': similar_scores[2] if len(similar_scores) > 2 else 0,
                'top_4_similar': similar_projects[3] if len(similar_projects) > 3 else '',
                'top_4_score': similar_scores[3] if len(similar_scores) > 3 else 0,
                'top_5_similar': similar_projects[4] if len(similar_projects) > 4 else '',
                'top_5_score': similar_scores[4] if len(similar_scores) > 4 else 0,
            })
        
        results_df = pd.DataFrame(results)
        self.logger.info(f"TOP類似プロジェクトリストを生成完了")
        
        return results_df
    
    def create_tsne_scatter_plot(self,
                                encoded_data: pd.DataFrame,
                                project_labels: List[str],
                                similarity_matrix: np.ndarray,
                                perplexity: int = 30,
                                random_state: int = 42) -> np.ndarray:
        """
        t-SNEによる2次元散布図を生成
        
        Args:
            encoded_data (pd.DataFrame): エンコード済みデータ
            project_labels (List[str]): プロジェクトラベル
            similarity_matrix (np.ndarray): 類似度行列
            perplexity (int): t-SNEのperplexityパラメータ
            random_state (int): 乱数シード
        
        Returns:
            np.ndarray: 2次元座標
        """
        self.logger.info("t-SNEによる次元削減を開始")
        
        # perplexityの調整(データ数が少ない場合)
        n_samples = len(encoded_data)
        perplexity = min(perplexity, n_samples - 1, 30)
        
        # t-SNEの実行
        tsne = TSNE(
            n_components=2,
            perplexity=perplexity,
            random_state=random_state,
            metric='precomputed',
            init='random'
        )
        
        # 距離行列に変換(1 - 類似度)
        distance_matrix = 1 - similarity_matrix
        np.fill_diagonal(distance_matrix, 0)  # 対角成分を0に
        
        # 2次元座標を取得
        coords_2d = tsne.fit_transform(distance_matrix)
        
        self.logger.info("t-SNE次元削減完了")
        
        # 散布図の描画
        self._plot_scatter(coords_2d, project_labels, similarity_matrix)
        
        return coords_2d
    
    def _plot_scatter(self, coords_2d: np.ndarray, 
                     project_labels: List[str],
                     similarity_matrix: np.ndarray):
        """
        散布図を描画して保存
        
        Args:
            coords_2d (np.ndarray): 2次元座標
            project_labels (List[str]): プロジェクトラベル
            similarity_matrix (np.ndarray): 類似度行列
        """
        fig, ax = plt.subplots(figsize=(16, 12))
        
        # 散布図の描画
        scatter = ax.scatter(
            coords_2d[:, 0],
            coords_2d[:, 1],
            c='steelblue',
            s=100,
            alpha=0.6,
            edgecolors='white',
            linewidths=1.5
        )
        
        # 高類似度のペアを線で接続(類似度 > 0.7)
        n = len(coords_2d)
        for i in range(n):
            for j in range(i + 1, n):
                if similarity_matrix[i, j] > 0.7:
                    ax.plot(
                        [coords_2d[i, 0], coords_2d[j, 0]],
                        [coords_2d[i, 1], coords_2d[j, 1]],
                        'r-',
                        alpha=0.3,
                        linewidth=0.5
                    )
        
        # ラベルの追加(サンプル数が少ない場合のみ)
        if len(project_labels) <= 100:
            for i, label in enumerate(project_labels):
                ax.annotate(
                    label,
                    (coords_2d[i, 0], coords_2d[i, 1]),
                    fontsize=6,
                    alpha=0.7,
                    xytext=(5, 5),
                    textcoords='offset points'
                )
        
        ax.set_title(
            'Project Similarity Map (t-SNE)\nRed lines: High similarity pairs (>0.7)',
            fontsize=16,
            fontweight='bold',
            pad=20
        )
        ax.set_xlabel('t-SNE Dimension 1', fontsize=12)
        ax.set_ylabel('t-SNE Dimension 2', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存
        filepath = os.path.join(self.output_directory, 'similarity_scatter_tsne.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        self.logger.info(f"散布図を保存: {filepath}")
    
    def save_similarity_reports(self,
                               high_similarity_pairs: pd.DataFrame,
                               top_similar_projects: pd.DataFrame):
        """
        類似度レポートをCSVファイルに保存
        
        Args:
            high_similarity_pairs (pd.DataFrame): 高類似度ペア
            top_similar_projects (pd.DataFrame): TOP類似プロジェクト
        """
        # 高類似度ペアの保存 (dataフォルダへ)
        if len(high_similarity_pairs) > 0:
            filepath_pairs = os.path.join(self.csv_output_directory, 'high_similarity_pairs.csv')
            high_similarity_pairs.to_csv(filepath_pairs, index=False, encoding='utf-8')
            self.logger.info(f"高類似度ペアを保存: {filepath_pairs} ({len(high_similarity_pairs)} ペア)")
        
        # TOP類似プロジェクトの保存 (dataフォルダへ)
        filepath_top = os.path.join(self.csv_output_directory, 'top_similar_projects.csv')
        top_similar_projects.to_csv(filepath_top, index=False, encoding='utf-8')
        self.logger.info(f"TOP類似プロジェクトを保存: {filepath_top} ({len(top_similar_projects)} プロジェクト)")
    
    def generate_complete_similarity_analysis(self,
                                             encoded_data: pd.DataFrame,
                                             original_df: pd.DataFrame,
                                             similarity_threshold: float = 0.7) -> Dict:
        """
        完全な類似度分析の実行
        
        Args:
            encoded_data (pd.DataFrame): エンコード済みシグナルデータ
            original_df (pd.DataFrame): 元のデータ
            similarity_threshold (float): 高類似度の閾値
        
        Returns:
            Dict: 分析結果
        """
        self.logger.info("=== 類似度分析を開始 ===")
        
        # プロジェクトラベルの生成
        project_labels = self._generate_project_labels(original_df)
        
        # 類似度行列の計算
        similarity_matrix = self.calculate_jaccard_similarity_matrix(encoded_data)
        
        # 高類似度ペアの抽出
        high_similarity_pairs = self.extract_high_similarity_pairs(
            similarity_matrix,
            project_labels,
            original_df,
            encoded_data,
            threshold=similarity_threshold
        )
        
        # 各プロジェクトのTOP類似プロジェクト
        top_similar_projects = self.generate_top_similar_projects(
            similarity_matrix,
            project_labels,
            top_n=5
        )
        
        # t-SNE散布図の生成
        coords_2d = self.create_tsne_scatter_plot(
            encoded_data,
            project_labels,
            similarity_matrix
        )
        
        # レポートの保存
        self.save_similarity_reports(high_similarity_pairs, top_similar_projects)
        
        # 統計情報の出力
        self._log_analysis_summary(similarity_matrix, high_similarity_pairs)
        
        self.logger.info("=== 類似度分析が完了しました ===")
        
        return {
            'similarity_matrix': similarity_matrix,
            'high_similarity_pairs': high_similarity_pairs,
            'top_similar_projects': top_similar_projects,
            'tsne_coordinates': coords_2d
        }
    
    def _generate_project_labels(self, df: pd.DataFrame) -> List[str]:
        """
        プロジェクトラベルを生成
        
        Args:
            df (pd.DataFrame): 元のデータ
        
        Returns:
            List[str]: プロジェクトラベルのリスト
        """
        labels = []
        for idx, row in df.iterrows():
            if 'project_id' in row and pd.notna(row['project_id']):
                labels.append(str(row['project_id']))
            else:
                labels.append(f"P{idx:03d}")
        return labels
    
    def _log_analysis_summary(self, 
                             similarity_matrix: np.ndarray,
                             high_similarity_pairs: pd.DataFrame):
        """
        分析サマリーをログ出力
        
        Args:
            similarity_matrix (np.ndarray): 類似度行列
            high_similarity_pairs (pd.DataFrame): 高類似度ペア
        """
        # 対角成分を除外
        n = len(similarity_matrix)
        mask = ~np.eye(n, dtype=bool)
        similarities = similarity_matrix[mask]
        
        self.logger.info("=" * 50)
        self.logger.info("類似度統計サマリー")
        self.logger.info("=" * 50)
        self.logger.info(f"プロジェクト数: {n}")
        self.logger.info(f"平均類似度: {similarities.mean():.4f}")
        self.logger.info(f"中央値: {np.median(similarities):.4f}")
        self.logger.info(f"最小値: {similarities.min():.4f}")
        self.logger.info(f"最大値: {similarities.max():.4f}")
        self.logger.info(f"標準偏差: {similarities.std():.4f}")
        self.logger.info(f"高類似度ペア(>0.7): {len(high_similarity_pairs)} 組")
        self.logger.info("=" * 50)


# テスト用の関数
def test_similarity_insights():
    """類似度分析のテスト"""
    try:
        # サンプルデータの生成
        np.random.seed(42)
        n_samples = 50
        n_features = 15
        
        # ダミーのワンホットエンコードデータ
        encoded_data = pd.DataFrame(
            np.random.randint(0, 2, size=(n_samples, n_features)),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        
        # ダミーの元データ
        original_df = pd.DataFrame({
            'project_id': [f'PRJ{i:03d}' for i in range(n_samples)]
        })
        
        # 分析実行
        generator = SimilarityInsightsGenerator()
        results = generator.generate_complete_similarity_analysis(
            encoded_data,
            original_df,
            similarity_threshold=0.7
        )
        
        print("✅ 類似度分析が正常に完了しました")
        print(f"✅ 高類似度ペア: {len(results['high_similarity_pairs'])} 組")
        print(f"✅ 出力ファイル:")
        print(f"   - data/high_similarity_pairs.csv")
        print(f"   - data/top_similar_projects.csv")
        print(f"   - png/similarity_scatter_tsne.png")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_similarity_insights()
