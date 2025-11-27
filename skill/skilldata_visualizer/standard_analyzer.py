"""
スキル標準分析モジュール

スキル標準データのレーダーチャート可視化を担当
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class StandardAnalyzer:
    """スキル標準のレーダーチャート分析"""
    
    def __init__(self, output_dir: str = "output"):
        """
        Args:
            output_dir (str): 出力ディレクトリ
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def create_skill_standard_radar(self, standard_csv_path: str = "input/skill_standard.csv"):
        """スキル標準のレーダーチャートを作成（全ロール一覧表示）"""
        
        try:
            # スキル標準データを読み込み
            standard_df = pd.read_csv(standard_csv_path, encoding='utf-8')
            print(f"スキル標準データ読み込み: {standard_df.shape[0]}行 × {standard_df.shape[1]}列")
            
        except FileNotFoundError:
            print(f"エラー: ファイル '{standard_csv_path}' が見つかりません")
            return
        except Exception as e:
            print(f"エラー: スキル標準データの読み込みに失敗: {e}")
            return
        
        # ロール列の存在確認
        if 'ロール' not in standard_df.columns:
            print("エラー: 'ロール'カラムが見つかりません")
            print(f"利用可能なカラム: {list(standard_df.columns)}")
            return
        
        # 必要なカラムの存在確認
        required_columns = ['カテゴリー', 'スキルレベル_数値']
        missing_columns = [col for col in required_columns if col not in standard_df.columns]
        if missing_columns:
            print(f"エラー: 必要なカラムが不足: {missing_columns}")
            return
        
        # ロール一覧を取得
        roles = sorted(standard_df['ロール'].unique())
        print(f"対象ロール数: {len(roles)}個")
        for role in roles:
            print(f"  • {role}")
        
        # 全体データから統一されたカテゴリー順序を取得
        all_categories = sorted(standard_df['カテゴリー'].unique())
        
        # サブプロットの配置を計算
        n_roles = len(roles)
        cols = 3  # 3列固定
        rows = (n_roles + cols - 1) // cols  # 必要な行数を計算
        
        # フィギュアサイズを調整（高さを増やして余白を確保）
        fig_height = max(6, 5 * rows + 2)  # 最小6、基本5×行数+2の余白
        
        # レーダーチャート作成
        fig, axes = plt.subplots(rows, cols, figsize=(15, fig_height), 
                                subplot_kw=dict(projection='polar'))
        
        # axesを1次元配列に変換（複数行の場合の処理）
        if rows == 1:
            axes = [axes] if cols == 1 else axes
        else:
            axes = axes.flatten()
        
        # タイトルを上部に配置（yの位置を調整）
        title_y_position = 0.98 if rows == 1 else 0.96
        fig.suptitle('スキル標準 - ロール別レーダーチャート', 
                     fontsize=18, fontweight='bold', y=title_y_position)
        
        for i, role in enumerate(roles):
            ax = axes[i]
            
            # ロール別データを抽出
            role_data = standard_df[standard_df['ロール'] == role].copy()
            
            # カテゴリー別の平均スキルレベルを計算
            category_stats = role_data.groupby('カテゴリー')['スキルレベル_数値'].mean().round(2)
            
            # 統一された順序で並び替え（データがないカテゴリーは0で補完）
            category_stats = category_stats.reindex(all_categories, fill_value=0)
            
            categories = category_stats.index.tolist()
            values = category_stats.tolist()
            
            # データを円形にするため最初の値を末尾に追加
            categories_circular = categories + [categories[0]]
            values_circular = values + [values[0]]
            
            # 角度を計算
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles_circular = angles + [angles[0]]
            
            # レーダーチャートをプロット
            ax.plot(angles_circular, values_circular, 'o-', linewidth=2, markersize=6)
            ax.fill(angles_circular, values_circular, alpha=0.25)
            
            # 軸設定
            ax.set_xticks(angles)
            ax.set_xticklabels(categories, fontsize=9)
            ax.set_ylim(0, 5)
            ax.set_yticks([1, 2, 3, 4, 5])
            ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=8)
            ax.grid(True)
            
            # タイトル設定（padを調整して余白を確保）
            ax.set_title(f'{role}', fontsize=12, fontweight='bold', pad=25)
            
            # 各カテゴリーの値をテキストで表示
            for angle, value in zip(angles, values):
                if value > 0:  # 0の場合は表示しない
                    ax.text(angle, value + 0.2, f'{value:.1f}', 
                           horizontalalignment='center', fontsize=8, fontweight='bold')
        
        # 使用されていないサブプロットを非表示
        for i in range(len(roles), len(axes)):
            axes[i].set_visible(False)
        
        # レイアウト調整（上部と下部の余白を調整）
        top_margin = 0.92 if rows == 1 else 0.90
        plt.tight_layout()
        plt.subplots_adjust(top=top_margin, bottom=0.05, hspace=0.3, wspace=0.2)
        
        # ファイル名を作成
        filename = "skill_standard_radar_all.png"
        save_path = self.output_dir / filename
        
        # 保存
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"スキル標準レーダーチャートを保存しました: {save_path}")