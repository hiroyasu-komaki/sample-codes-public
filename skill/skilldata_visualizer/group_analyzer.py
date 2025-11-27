"""
集団分析モジュール（組織スキル充足度分析専用）

組織全体のスキル分布を箱ひげ図で可視化し、強み・弱みを特定
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
import math
warnings.filterwarnings('ignore')


class GroupAnalyzer:
    """組織スキル充足度分析"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = "output2"):
        """
        Args:
            df (pd.DataFrame): スキルデータ
            output_dir (str): 出力ディレクトリ
        """
        self.df = df
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 個人別データの準備
        if 'ファイル名' in df.columns:
            self.individuals = sorted(df['ファイル名'].unique())
        else:
            print("警告: 'ファイル名'カラムが見つかりません")
            self.individuals = []
    
    def create_skill_sufficiency_analysis(self):
        """組織スキル充足度分析を実行"""
        
        if len(self.individuals) < 2:
            print("充足度分析には2人以上のデータが必要です")
            return
        
        print(f"\n=== 組織スキル充足度分析 ({len(self.individuals)}名) ===")
        
        # 1. カテゴリー別の箱ひげ図を作成
        self._create_category_boxplot()
        
        # 2. 統合された箱ひげ図を作成
        self._create_combined_boxplot()
        
        # 3. 統計情報を表示
        self._display_sufficiency_stats()
        
        print(f"完了！すべての分析結果を {self.output_dir} に保存しました")
    
    def _create_category_boxplot(self):
        """カテゴリー別スキルレベルの箱ひげ図"""
        
        # 個人別×カテゴリー別の平均スキルレベルを計算
        person_category_data = []
        
        for person in self.individuals:
            person_data = self.df[self.df['ファイル名'] == person]
            category_means = person_data.groupby('カテゴリー')['スキルレベル_数値'].mean()
            
            for category, mean_level in category_means.items():
                person_category_data.append({
                    '個人': person,
                    'カテゴリー': category,
                    '平均スキルレベル': mean_level
                })
        
        plot_data = pd.DataFrame(person_category_data)
        
        # カテゴリーを統一された順序で並び替え
        categories = sorted(plot_data['カテゴリー'].unique())
        plot_data['カテゴリー'] = pd.Categorical(plot_data['カテゴリー'], categories=categories)
        
        # 箱ひげ図作成
        plt.figure(figsize=(14, 8))
        
        box_plot = sns.boxplot(
            data=plot_data,
            x='カテゴリー',
            y='平均スキルレベル',
            palette='Set2'
        )
        
        # 個別データポイントを重ねて表示
        sns.stripplot(
            data=plot_data,
            x='カテゴリー',
            y='平均スキルレベル',
            color='black',
            alpha=0.6,
            size=4,
            jitter=True
        )
        
        plt.title('組織スキル充足度分析 - カテゴリー別分布', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('カテゴリー', fontsize=12, fontweight='bold')
        plt.ylabel('平均スキルレベル', fontsize=12, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 5)
        plt.grid(axis='y', alpha=0.3)
        
        # 統計情報をテキストで追加
        total_people = len(self.individuals)
        overall_mean = plot_data['平均スキルレベル'].mean()
        
        plt.figtext(0.02, 0.02, 
                   f'分析対象: {total_people}名 | 全体平均: {overall_mean:.2f}',
                   fontsize=10, ha='left')
        
        # 保存
        save_path = self.output_dir / "organization_skill_sufficiency_by_category.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"カテゴリー別箱ひげ図を保存: {save_path}")
    
        """カテゴリー別およびスキル項目別の統合箱ひげ図"""
        
        categories = sorted(self.df['カテゴリー'].unique())
        valid_categories = []
        
        # 有効なカテゴリーを事前チェック
        for category in categories:
            category_data = self.df[self.df['カテゴリー'] == category]
            skill_items = sorted(category_data['スキル項目'].unique())
            
            # スキル項目が2個以上あるカテゴリーのみ対象
            if len(skill_items) >= 2:
                valid_categories.append(category)
        
        if not valid_categories:
            print("箱ひげ図を作成できるカテゴリーがありません（各カテゴリーに2個以上のスキル項目が必要）")
            return
        
        # サブプロットの配置を計算
        n_categories = len(valid_categories)
        cols = 2  # 2列固定
        rows = math.ceil(n_categories / cols)
        
        # 全体のフィギュアサイズを計算
        fig_width = 20
        fig_height = max(8, rows * 6)
        
        fig, axes = plt.subplots(rows, cols, figsize=(fig_width, fig_height))
        
        # axesを1次元配列に変換（単一サブプロットの場合の対応）
        if n_categories == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes.flatten()
        else:
            axes = axes.flatten()
        
        for idx, category in enumerate(valid_categories):
            ax = axes[idx]
            category_data = self.df[self.df['カテゴリー'] == category]
            skill_items = sorted(category_data['スキル項目'].unique())
            
            # スキル項目別のデータを収集
            skill_item_data = []
            
            for skill_item in skill_items:
                skill_data = category_data[category_data['スキル項目'] == skill_item]
                skill_levels = skill_data['スキルレベル_数値'].tolist()
                
                # データポイントが少なすぎる場合はスキップ
                if len(skill_levels) < 2:
                    continue
                
                for level in skill_levels:
                    skill_item_data.append({
                        'スキル項目': skill_item,
                        'スキルレベル': level
                    })
            
            if not skill_item_data:
                ax.text(0.5, 0.5, f'{category}\n(データ不足)', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, bbox=dict(boxstyle="round", facecolor='lightgray'))
                ax.set_xticks([])
                ax.set_yticks([])
                continue
            
            plot_data = pd.DataFrame(skill_item_data)
            
            # スキル項目を統一された順序で並び替え
            valid_skill_items = sorted(plot_data['スキル項目'].unique())
            plot_data['スキル項目'] = pd.Categorical(
                plot_data['スキル項目'], 
                categories=valid_skill_items
            )
            
            # 箱ひげ図作成
            box_plot = sns.boxplot(
                data=plot_data,
                x='スキル項目',
                y='スキルレベル',
                palette='Set3',
                ax=ax
            )
            
            # 個別データポイントを重ねて表示
            sns.stripplot(
                data=plot_data,
                x='スキル項目',
                y='スキルレベル',
                color='black',
                alpha=0.6,
                size=3,
                jitter=True,
                ax=ax
            )
            
            ax.set_title(f'{category}', fontsize=14, fontweight='bold', pad=15)
            ax.set_xlabel('スキル項目', fontsize=10, fontweight='bold')
            ax.set_ylabel('スキルレベル', fontsize=10, fontweight='bold')
            ax.tick_params(axis='x', rotation=45, labelsize=8)
            ax.set_ylim(0, 5)
            ax.grid(axis='y', alpha=0.3)
            
            # 統計情報をテキストで追加
            category_mean = plot_data['スキルレベル'].mean()
            total_data_points = len(plot_data)
            unique_skills = len(valid_skill_items)
            
            ax.text(0.02, 0.98, 
                   f'平均: {category_mean:.2f} | 項目: {unique_skills}個 | データ: {total_data_points}個',
                   transform=ax.transAxes, fontsize=8, ha='left', va='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        # 使用しないサブプロットを非表示
        for idx in range(n_categories, len(axes)):
            axes[idx].set_visible(False)
        
        # 全体のタイトルと調整
        fig.suptitle('組織スキル充足度分析 - カテゴリー・スキル項目別分布', 
                     fontsize=18, fontweight='bold', y=0.98)
        
        # 全体の統計情報を下部に追加
        total_people = len(self.individuals)
        overall_mean = self.df['スキルレベル_数値'].mean()
        total_categories = len(valid_categories)
        
        fig.text(0.5, 0.02, 
                f'分析対象: {total_people}名 | 全体平均: {overall_mean:.2f} | 対象カテゴリー: {total_categories}個',
                fontsize=12, ha='center', weight='bold')
        
        # レイアウト調整
        plt.tight_layout()
        plt.subplots_adjust(top=0.94, bottom=0.08)
        
        # 保存
        save_path = self.output_dir / "organization_skill_sufficiency_by_skill.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"統合箱ひげ図を保存: {save_path}")
    
    def _display_sufficiency_stats(self):
        """組織スキル充足度の統計情報を表示"""
        
        print(f"\n=== 組織スキル充足度統計 ===")
        
        # カテゴリー別の統計を計算
        category_stats = []
        
        for category in sorted(self.df['カテゴリー'].unique()):
            category_data = self.df[self.df['カテゴリー'] == category]
            
            # 個人別平均を計算
            person_averages = []
            for person in self.individuals:
                person_data = category_data[category_data['ファイル名'] == person]
                if not person_data.empty:
                    avg = person_data['スキルレベル_数値'].mean()
                    person_averages.append(avg)
            
            if person_averages:
                stats = {
                    'カテゴリー': category,
                    '組織平均': np.mean(person_averages),
                    '標準偏差': np.std(person_averages),
                    '最高値': np.max(person_averages),
                    '最低値': np.min(person_averages),
                    '中央値': np.median(person_averages),
                    'データ人数': len(person_averages)
                }
                category_stats.append(stats)
        
        # 統計をデータフレームに変換して表示
        stats_df = pd.DataFrame(category_stats)
        stats_df = stats_df.sort_values('組織平均', ascending=False)
        
        print(f"\nカテゴリー別組織スキル統計（平均レベル順）:")
        print("="*80)
        for _, row in stats_df.iterrows():
            print(f"{row['カテゴリー']:<20} | "
                  f"平均: {row['組織平均']:.2f} | "
                  f"標準偏差: {row['標準偏差']:.2f} | "
                  f"範囲: {row['最低値']:.2f}-{row['最高値']:.2f} | "
                  f"対象: {row['データ人数']}名")
        
        # 強み・弱みの特定
        print(f"\n=== 組織の強み・弱み分析 ===")
        
        overall_mean = stats_df['組織平均'].mean()
        
        strengths = stats_df[stats_df['組織平均'] >= overall_mean + 0.2]  # 全体平均+0.2以上
        weaknesses = stats_df[stats_df['組織平均'] <= overall_mean - 0.2]  # 全体平均-0.2以下
        
        print(f"全体平均スキルレベル: {overall_mean:.2f}")
        
        if not strengths.empty:
            print(f"\n【強みカテゴリー】(平均{overall_mean + 0.2:.2f}以上):")
            for _, row in strengths.iterrows():
                print(f"  • {row['カテゴリー']}: {row['組織平均']:.2f}")
        
        if not weaknesses.empty:
            print(f"\n【弱みカテゴリー】(平均{overall_mean - 0.2:.2f}以下):")
            for _, row in weaknesses.iterrows():
                print(f"  • {row['カテゴリー']}: {row['組織平均']:.2f}")
        
        # バラツキ分析
        high_variance = stats_df[stats_df['標準偏差'] >= 0.5]  # 標準偏差0.5以上
        
        if not high_variance.empty:
            print(f"\n【スキルバラツキの大きいカテゴリー】(標準偏差0.5以上):")
            for _, row in high_variance.iterrows():
                print(f"  • {row['カテゴリー']}: 標準偏差{row['標準偏差']:.2f} "
                      f"(レンジ: {row['最低値']:.2f}-{row['最高値']:.2f})")
    
    def get_organization_summary(self):
        """組織概要情報を取得"""
        
        summary = {
            'total_people': len(self.individuals),
            'total_skills': len(self.df),
            'categories': sorted(self.df['カテゴリー'].unique()),
            'overall_average': self.df['スキルレベル_数値'].mean()
        }
        
        return summary