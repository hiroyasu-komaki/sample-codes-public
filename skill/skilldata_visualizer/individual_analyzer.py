"""
個人プロファイル分析モジュール（レーダーチャート専用）

個人のスキルセットをレーダーチャートで可視化し、PNG形式で保存
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class IndividualAnalyzer:
    """個人スキルプロファイルのレーダーチャート分析"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = "output"):
        """
        Args:
            df (pd.DataFrame): スキルデータ
            output_dir (str): 出力ディレクトリ
        """
        self.df = df
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 個人リストを取得（ファイル名カラムから）
        if 'ファイル名' in df.columns:
            self.individuals = sorted(df['ファイル名'].unique())
        else:
            print("警告: 'ファイル名'カラムが見つかりません")
            self.individuals = []
    
    def create_radar_chart(self, person_name: str):
        """指定個人のレーダーチャートを作成・保存"""
        
        if person_name not in self.individuals:
            print(f"指定された人物 '{person_name}' が見つかりません")
            print(f"利用可能な人物: {', '.join(self.individuals)}")
            return
        
        self._create_radar_chart(person_name)
        self._create_skills_chart(person_name)
        print(f"{person_name}のレーダーチャートを保存しました")
        print(f"{person_name}のスキル項目チャートを保存しました")
    
    def _create_radar_chart(self, person_name: str):
        """個人のレーダーチャートを作成・保存"""
        
        # 個人データを抽出
        person_data = self.df[self.df['ファイル名'] == person_name].copy()
        
        # 全体データから標準的なカテゴリー順序を決定（アルファベット順で統一）
        all_categories = sorted(self.df['カテゴリー'].unique())
        
        # カテゴリー別の平均スキルレベルを計算
        category_stats = person_data.groupby('カテゴリー')['スキルレベル_数値'].agg([
            'mean', 'count'
        ]).round(2)
        category_stats.columns = ['平均レベル', 'スキル数']
        
        # 統一された順序で並び替え（データがないカテゴリーは0で補完）
        category_stats = category_stats.reindex(all_categories, fill_value=0)
        
        # レーダーチャート作成
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        categories = category_stats.index.tolist()
        values = category_stats['平均レベル'].tolist()
        
        # データを円形にするため最初の値を末尾に追加
        categories_circular = categories + [categories[0]]
        values_circular = values + [values[0]]
        
        # 角度を計算
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles_circular = angles + [angles[0]]
        
        # レーダーチャートをプロット
        ax.plot(angles_circular, values_circular, 'o-', linewidth=3, markersize=8, color='#2E86AB')
        ax.fill(angles_circular, values_circular, alpha=0.25, color='#2E86AB')
        
        # 軸設定
        ax.set_xticks(angles)
        ax.set_xticklabels(categories, fontsize=12)
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=10)
        ax.grid(True)
        
        # タイトル設定
        ax.set_title(f'{person_name} - スキルレベル', fontsize=16, fontweight='bold', pad=30)
        
        # 各カテゴリーの値をテキストで表示
        for angle, value, category in zip(angles, values, categories):
            ax.text(angle, value + 0.3, f'{value:.2f}', 
                   horizontalalignment='center', fontsize=10, fontweight='bold')
        
        # 統計情報をテキストで追加
        total_skills = len(person_data)
        avg_level = person_data['スキルレベル_数値'].mean()
        
        plt.figtext(0.02, 0.02, 
                   f'総スキル数: {total_skills}件 | 全体平均: {avg_level:.2f}',
                   fontsize=10, ha='left')
        
        # ファイル名を作成（sample_001_engineer_focused -> sample_001_engineer_focused.png）
        filename = f"{person_name}.png"
        save_path = self.output_dir / filename
        
        # 保存
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()  # メモリ節約のため閉じる
    
    def _create_skills_chart(self, person_name: str):
        """個人のカテゴリ別スキル項目横棒グラフを作成・保存"""
        
        # 個人データを抽出
        person_data = self.df[self.df['ファイル名'] == person_name].copy()
        
        # カテゴリ別にデータを整理
        categories = sorted(person_data['カテゴリー'].unique())
        
        # カテゴリ数に応じてサブプロット配置を決定
        n_categories = len(categories)
        if n_categories <= 2:
            rows, cols = 1, n_categories
            figsize = (8 * n_categories, 6)
        elif n_categories <= 4:
            rows, cols = 2, 2
            figsize = (16, 12)
        elif n_categories <= 6:
            rows, cols = 2, 3
            figsize = (18, 12)
        else:
            rows, cols = 3, (n_categories + 2) // 3
            figsize = (6 * cols, 6 * rows)
        
        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        
        # axesを1次元配列に変換
        if n_categories == 1:
            axes = [axes]
        elif rows == 1 or cols == 1:
            axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
        else:
            axes = axes.flatten()
        
        fig.suptitle(f'{person_name} - カテゴリ別スキル項目', fontsize=16, fontweight='bold', y=0.98)
        
        for i, category in enumerate(categories):
            ax = axes[i]
            
            # カテゴリ内のスキル項目データを取得
            category_data = person_data[person_data['カテゴリー'] == category].copy()
            
            # スキル項目別に整理（スキルレベル順でソート）
            skill_data = category_data.groupby('スキル項目')['スキルレベル_数値'].mean().sort_values(ascending=True)
            
            # 横棒グラフ作成
            colors = plt.cm.viridis(skill_data.values / 5.0)  # 0-5の範囲で色分け
            bars = ax.barh(range(len(skill_data)), skill_data.values, color=colors)
            
            # 軸設定
            ax.set_yticks(range(len(skill_data)))
            ax.set_yticklabels(skill_data.index, fontsize=9)
            ax.set_xlabel('スキルレベル', fontsize=10)
            ax.set_title(f'{category}', fontsize=12, fontweight='bold')
            ax.set_xlim(0, 5)
            ax.grid(axis='x', alpha=0.3)
            
            # 各バーに数値を表示
            for j, (skill, value) in enumerate(skill_data.items()):
                ax.text(value + 0.1, j, f'{value:.1f}', 
                       va='center', fontsize=8, fontweight='bold')
        
        # 使用されていないサブプロットを非表示
        for i in range(len(categories), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # タイトル用スペース確保
        
        # ファイル名を作成（person_name + "_skills.png"）
        filename = f"{person_name}_skills.png"
        save_path = self.output_dir / filename
        
        # 保存
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()  # メモリ節約のため閉じる
    
    def get_individuals_list(self):
        """利用可能な個人名のリストを取得"""
        return self.individuals.copy()