"""
レポート生成モジュール

分析結果を可視化し、各種フォーマットでレポートを生成します。
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import yaml
import json
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from matplotlib import font_manager

# 日本語フォントの設定を確実に行う
def setup_japanese_font():
    """日本語フォントを設定"""
    # 利用可能なフォントを確認
    available_fonts = [f.name for f in font_manager.fontManager.ttflist]
    
    # 優先順位付きフォントリスト
    preferred_fonts = [
        'Hiragino Kaku Gothic ProN',  # Mac標準
        'Hiragino Sans',              # Mac (新しいバージョン)
        'Yu Gothic',                  # Windows
        'Meiryo',                     # Windows
        'IPAexGothic',                # Linux
        'IPAPGothic',                 # Linux
        'Noto Sans CJK JP',           # Linux
        'Takao Gothic',               # Linux
        'DejaVu Sans'                 # フォールバック
    ]
    
    # 利用可能なフォントを選択
    selected_font = None
    for font in preferred_fonts:
        if font in available_fonts:
            selected_font = font
            break
    
    if selected_font:
        matplotlib.rcParams['font.sans-serif'] = [selected_font]
    else:
        # デフォルトのフォールバック
        matplotlib.rcParams['font.sans-serif'] = preferred_fonts
    
    matplotlib.rcParams['axes.unicode_minus'] = False
    
    # デバッグ用: 使用されるフォントを確認
    # print(f"使用フォント: {matplotlib.rcParams['font.sans-serif'][0]}")

# フォント設定を実行
setup_japanese_font()


class SurveyReportGenerator:
    """アンケート分析レポート生成クラス"""
    
    def __init__(self, 
                 analysis_results: Dict[str, Any],
                 config_file: str = 'config/config.yaml'):
        """
        初期化
        
        Args:
            analysis_results: DataAnalyserの分析結果
            config_file: 設定ファイルのパス
        """
        self.analysis_results = analysis_results
        
        # 設定ファイルの読み込み
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # グラフスタイルの設定
        self._setup_plot_style()
    
    # ==========================================
    # 1. エグゼクティブサマリー
    # ==========================================
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """
        エグゼクティブサマリーの生成（標準化前と標準化後）
        
        内容:
        - 調査概要
        - 総合満足度
        - 満足度分布
        - 最優先改善項目（Top 3）- 標準化前と標準化後
        - 維持・強化項目（Top 3）- 標準化前と標準化後
        
        Returns:
            サマリーデータ
        """
        summary = {}
        
        # 総合満足度
        if 'overall_satisfaction' in self.analysis_results:
            overall = self.analysis_results['overall_satisfaction']
            if 'direct' in overall and overall['direct']:
                summary['overall_satisfaction'] = {
                    'value': overall['direct']['value'],
                    'method': overall['direct']['method']
                }
        
        # 満足度分布
        if 'basic_statistics' in self.analysis_results:
            basic_stats = self.analysis_results['basic_statistics']
            if 'satisfaction_distribution' in basic_stats:
                dist = basic_stats['satisfaction_distribution']
                if 'overall_satisfaction' in dist:
                    overall_dist = dist['overall_satisfaction']
                    summary['satisfaction_distribution'] = {
                        'satisfied': overall_dist.get('satisfied', {}),
                        'dissatisfied': overall_dist.get('dissatisfied', {})
                    }
        
        # IPA分析から最優先改善項目と維持項目を抽出（標準化前と標準化後）
        if 'ipa_analysis' in self.analysis_results:
            ipa_results = self.analysis_results['ipa_analysis']
            
            # 標準化前のIPA分析
            if 'original' in ipa_results and 'items' in ipa_results['original']:
                ipa = ipa_results['original']
                priority_items = []
                maintain_items = []
                
                for item, data in ipa['items'].items():
                    if data['quadrant'] == 'Ⅱ':
                        priority_items.append({
                            'name': item,
                            'satisfaction': data['satisfaction'],
                            'importance': data['importance'],
                            'gap': data['gap'],
                            'priority': data.get('priority')
                        })
                    elif data['quadrant'] == 'Ⅰ':
                        maintain_items.append({
                            'name': item,
                            'satisfaction': data['satisfaction'],
                            'importance': data['importance']
                        })
                
                # 優先順位でソート
                priority_items.sort(key=lambda x: x.get('priority', 999))
                
                # 満足度でソート（維持項目）
                maintain_items.sort(key=lambda x: x['satisfaction'], reverse=True)
                
                summary['priority_improvements_original'] = priority_items[:3]
                summary['maintain_strengths_original'] = maintain_items[:3]
            
            # 標準化後のIPA分析
            if 'rescaled' in ipa_results and 'items' in ipa_results['rescaled']:
                ipa = ipa_results['rescaled']
                priority_items = []
                maintain_items = []
                
                for item, data in ipa['items'].items():
                    if data['quadrant'] == 'Ⅱ':
                        priority_items.append({
                            'name': item,
                            'satisfaction': data['satisfaction'],
                            'importance': data['importance'],
                            'gap': data['gap'],
                            'priority': data.get('priority')
                        })
                    elif data['quadrant'] == 'Ⅰ':
                        maintain_items.append({
                            'name': item,
                            'satisfaction': data['satisfaction'],
                            'importance': data['importance']
                        })
                
                # 優先順位でソート
                priority_items.sort(key=lambda x: x.get('priority', 999))
                
                # 満足度でソート（維持項目）
                maintain_items.sort(key=lambda x: x['satisfaction'], reverse=True)
                
                summary['priority_improvements_rescaled'] = priority_items[:3]
                summary['maintain_strengths_rescaled'] = maintain_items[:3]
        
        return summary
    
    # ==========================================
    # 2. グラフ生成
    # ==========================================
    
    def plot_satisfaction_distribution(self,
                                      item: str,
                                      output_path: Optional[str] = None) -> str:
        """
        満足度分布の棒グラフ
        
        グラフ仕様:
        - 縦棒グラフ
        - X軸: 評価値（1: 非常に不満 ～ 5: 非常に満足）
        - Y軸: 件数または割合（%）
        - 色分け: 1-2（赤）、3（黄）、4-5（緑）
        - 平均値を縦線で表示
        
        Args:
            item: 分析対象項目
            output_path: 保存先パス
        
        Returns:
            保存先パス
        """
        if output_path is None:
            output_path = f'graphs/satisfaction_distribution_{item}.png'
        
        # 分布データの取得
        dist_data = self.analysis_results.get('basic_statistics', {}).get(
            'satisfaction_distribution', {}).get(item)
        
        if not dist_data:
            print(f"警告: {item}の分布データが見つかりません")
            return ""
        
        # データの準備
        values = [1, 2, 3, 4, 5]
        counts = [dist_data.get(str(v), {}).get('count', 0) for v in values]
        percentages = [dist_data.get(str(v), {}).get('percentage', 0) for v in values]
        
        # 色の設定
        colors = ['#d9534f', '#d9534f', '#f0ad4e', '#5cb85c', '#5cb85c']
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(values, counts, color=colors, alpha=0.7, edgecolor='black')
        
        # ラベル
        ax.set_xlabel('評価値', fontsize=12)
        ax.set_ylabel('件数', fontsize=12)
        ax.set_title(f'{item} の満足度分布', fontsize=14, fontweight='bold')
        ax.set_xticks(values)
        ax.set_xticklabels(['非常に不満', '不満', '普通', '満足', '非常に満足'])
        
        # 棒の上にパーセンテージを表示
        for i, (bar, pct) in enumerate(zip(bars, percentages)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{pct:.1f}%',
                   ha='center', va='bottom', fontsize=10)
        
        # 平均値の線
        stats_all = self.analysis_results.get('basic_statistics', {}).get(
            'descriptive_stats', {})
        # 標準化前データを使用
        stats_original = stats_all.get('original', stats_all)
        stats = stats_original.get(item)
        
        if stats and 'mean' in stats:
            mean_val = stats['mean']
            ax.axvline(mean_val, color='blue', linestyle='--', linewidth=2,
                      label=f'平均値: {mean_val:.2f}')
            ax.legend()
        
        plt.tight_layout()
        
        # 保存
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_satisfaction_ranking(self,
                                 items: List[str] = None,
                                 output_path: Optional[str] = None) -> str:
        """
        満足度ランキングの箱ひげ図（標準化前データを使用）
        
        グラフ仕様:
        - 箱ひげ図
        - 満足度で降順ソート
        - データ分布を可視化
        
        Args:
            items: 比較対象項目のリスト
            output_path: 保存先パス
        
        Returns:
            保存先パス
        """
        if output_path is None:
            output_path = 'graphs/satisfaction_ranking.png'
        
        # 記述統計の取得（新しい構造に対応）
        desc_stats_all = self.analysis_results.get('basic_statistics', {}).get(
            'descriptive_stats', {})
        
        # 標準化前データを使用
        desc_stats = desc_stats_all.get('original', desc_stats_all)
        
        if items is None:
            # 全ての満足度項目
            items = [k for k in desc_stats.keys() if 'importance' not in k and 'rescaled' not in k]
        
        # データの準備（平均値でソート）
        data = []
        for item in items:
            if item in desc_stats:
                stats = desc_stats[item]
                data.append({
                    'item': item,
                    'mean': stats['mean'],
                    'median': stats['median'],
                    'q1': stats['q1'],
                    'q3': stats['q3'],
                    'min': stats['min'],
                    'max': stats['max']
                })
        
        if not data:
            print("警告: 満足度データが見つかりません")
            return ""
        
        # データフレーム化してソート（昇順: 下から上に描画されるため）
        df = pd.DataFrame(data)
        df = df.sort_values('mean', ascending=True)  # 昇順ソート（グラフでは上が高くなる）
        
        # 箱ひげ図用のデータを準備
        boxplot_data = []
        for _, row in df.iterrows():
            box_data = {
                'whislo': row['min'],
                'q1': row['q1'],
                'med': row['median'],
                'q3': row['q3'],
                'whishi': row['max'],
                'mean': row['mean'],  # 平均値を追加
                'fliers': []
            }
            boxplot_data.append(box_data)
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(10, max(6, len(df) * 0.5)))
        
        y_pos = list(range(1, len(df) + 1))
        
        # 横向きの箱ひげ図
        bp = ax.bxp(boxplot_data, positions=y_pos, vert=False,
                   patch_artist=True,
                   showmeans=True,
                   meanprops=dict(marker='D', markerfacecolor='red', 
                                markeredgecolor='red', markersize=6),
                   boxprops=dict(facecolor='lightblue', edgecolor='black', linewidth=1.5),
                   medianprops=dict(color='darkblue', linewidth=2),
                   whiskerprops=dict(color='black', linewidth=1.5),
                   capprops=dict(color='black', linewidth=1.5))
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(df['item'], fontsize=10)
        ax.set_xlabel('満足度', fontsize=12, fontweight='bold')
        ax.set_title('満足度ランキング（箱ひげ図）', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0.5, 5.5)
        
        # グリッド
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # 平均値を数値で表示
        for i, (pos, mean) in enumerate(zip(y_pos, df['mean'])):
            ax.text(mean + 0.15, pos, f'{mean:.2f}',
                   ha='left', va='center', fontsize=9, fontweight='bold')
        
        # 凡例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='lightblue', edgecolor='black', label='四分位範囲(Q1-Q3)'),
            plt.Line2D([0], [0], color='darkblue', linewidth=2, label='中央値'),
            plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='red', 
                      markersize=6, label='平均値')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
        
        plt.tight_layout()
        
        # 保存
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_correlation_heatmap(self,
                                correlation_matrix: pd.DataFrame = None,
                                output_path: Optional[str] = None) -> str:
        """
        相関行列のヒートマップ
        
        グラフ仕様:
        - 色の濃淡で相関の強さを表現
        - カラーマップ: -1（青）～ 0（白）～ +1（赤）
        - 各セルに相関係数を表示
        
        Args:
            correlation_matrix: 相関行列
            output_path: 保存先パス
        
        Returns:
            保存先パス
        """
        if output_path is None:
            output_path = 'graphs/correlation_heatmap.png'
        
        # 相関行列の取得
        if correlation_matrix is None:
            corr_data = self.analysis_results.get('correlation_analysis', {}).get(
                'correlation_matrix')
            if corr_data:
                correlation_matrix = pd.DataFrame(corr_data)
        
        if correlation_matrix is None or correlation_matrix.empty:
            print("警告: 相関行列データが見つかりません")
            return ""
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(12, 10))
        
        sns.heatmap(correlation_matrix, 
                   annot=True, 
                   fmt='.2f',
                   cmap='RdBu_r',
                   center=0,
                   vmin=-1, 
                   vmax=1,
                   square=True,
                   linewidths=0.5,
                   cbar_kws={'label': '相関係数'},
                   ax=ax)
        
        ax.set_title('満足度項目間の相関行列', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # 保存
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_attribute_comparison(self,
                                  attribute_name: str,
                                  attribute_analysis: Dict[str, Any] = None,
                                  output_path: Optional[str] = None,
                                  use_rescaled: bool = False) -> str:
        """
        属性別比較の箱ひげ図（標準化前または標準化後）
        
        グラフ仕様:
        - 箱ひげ図
        - 各グループのデータ分布を表示
        - 中央値、四分位数、外れ値を可視化
        
        Args:
            attribute_name: 属性名
            attribute_analysis: 属性別分析結果
            output_path: 保存先パス
            use_rescaled: 標準化後データを使用するか
        
        Returns:
            保存先パス
        """
        if output_path is None:
            suffix = '_rescaled' if use_rescaled else '_original'
            output_path = f'graphs/attribute_comparison_{attribute_name}{suffix}.png'
        
        # 属性別分析データの取得
        if attribute_analysis is None:
            attr_data_all = self.analysis_results.get('attribute_analysis', {})
            # 標準化前/後のデータを選択
            if use_rescaled:
                attr_data = attr_data_all.get('rescaled', {})
            else:
                attr_data = attr_data_all.get('original', attr_data_all)
            
            attribute_analysis = attr_data.get(f'by_{attribute_name}')
        
        if not attribute_analysis or 'groups' not in attribute_analysis:
            print(f"警告: {attribute_name}の属性別分析データが見つかりません")
            return ""
        
        groups_data = attribute_analysis['groups']
        
        # 生データの取得
        raw_data = attribute_analysis.get('raw_data', {})
        
        if raw_data:
            # 生データがある場合：本格的な箱ひげ図
            # グループを満足度の高い順（平均値降順）に並べ替え
            groups = sorted(groups_data.keys(), 
                          key=lambda g: groups_data[g]['mean'], 
                          reverse=True)
            data_list = [raw_data[g] for g in groups]
            
            # グラフ作成
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 箱ひげ図の描画
            bp = ax.boxplot(data_list, labels=groups,
                           patch_artist=True,
                           showmeans=True,
                           meanprops=dict(marker='D', markerfacecolor='red', 
                                        markeredgecolor='red', markersize=8))
            
            # 箱の色を設定
            for patch in bp['boxes']:
                patch.set_facecolor('lightblue')
                patch.set_edgecolor('black')
                patch.set_linewidth(1.5)
            
            # 中央値の線を強調
            for median in bp['medians']:
                median.set_color('darkblue')
                median.set_linewidth(2)
            
            # ヒゲの線
            for whisker in bp['whiskers']:
                whisker.set_color('black')
                whisker.set_linewidth(1.5)
            
            # キャップの線
            for cap in bp['caps']:
                cap.set_color('black')
                cap.set_linewidth(1.5)
            
        else:
            # 生データがない場合：統計量から近似的に作成
            # グループを満足度の高い順（平均値降順）に並べ替え
            groups = sorted(groups_data.keys(), 
                          key=lambda g: groups_data[g]['mean'], 
                          reverse=True)
            means = [groups_data[g]['mean'] for g in groups]
            stds = [groups_data[g]['std'] for g in groups]
            
            # グラフ作成
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 統計量から箱ひげ図風のデータを作成
            boxplot_data = []
            for g in groups:
                mean = groups_data[g]['mean']
                std = groups_data[g]['std']
                # 正規分布を仮定
                box_data = {
                    'whislo': max(1, mean - 2 * std),
                    'q1': mean - 0.675 * std,
                    'med': mean,
                    'q3': mean + 0.675 * std,
                    'whishi': min(5, mean + 2 * std),
                    'fliers': []
                }
                boxplot_data.append(box_data)
            
            # 箱ひげ図の描画
            x_pos = list(range(1, len(groups) + 1))
            bp = ax.bxp(boxplot_data, positions=x_pos,
                       patch_artist=True,
                       boxprops=dict(facecolor='lightblue', edgecolor='black', linewidth=1.5),
                       medianprops=dict(color='darkblue', linewidth=2),
                       whiskerprops=dict(color='black', linewidth=1.5),
                       capprops=dict(color='black', linewidth=1.5))
            
            ax.set_xticks(x_pos)
        
        # 共通設定
        ax.set_xticklabels(groups, rotation=45, ha='right', fontsize=11)
        ax.set_ylabel('満足度', fontsize=12, fontweight='bold')
        
        # タイトルに標準化前/後を明記
        title_suffix = '（標準化後）' if use_rescaled else '（標準化前）'
        ax.set_title(f'{attribute_name}別の満足度分布{title_suffix}', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Y軸範囲を調整（標準化後は自動調整）
        if use_rescaled:
            # 標準化後データの範囲を取得
            if raw_data:
                all_values = [val for vals in raw_data.values() for val in vals]
                y_min = max(0.5, min(all_values) - 0.5)
                y_max = min(5.5, max(all_values) + 0.5)
            else:
                means = [groups_data[g]['mean'] for g in groups]
                stds = [groups_data[g]['std'] for g in groups]
                y_min = max(0.5, min(means) - max(stds) - 0.5)
                y_max = min(5.5, max(means) + max(stds) + 0.5)
            ax.set_ylim(y_min, y_max)
        else:
            ax.set_ylim(0.5, 5.5)
        
        # グリッド
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # 凡例を追加
        if raw_data:
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='lightblue', edgecolor='black', label='四分位範囲(Q1-Q3)'),
                plt.Line2D([0], [0], color='darkblue', linewidth=2, label='中央値'),
                plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='red', 
                          markersize=8, label='平均値')
            ]
            ax.legend(handles=legend_elements, loc='upper right', fontsize=9)
        
        plt.tight_layout()
        
        # 保存
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_ipa_matrix(self,
                       ipa_results: Dict[str, Any] = None,
                       output_path: Optional[str] = None,
                       use_rescaled: bool = False) -> str:
        """
        IPA分析のマトリックス図（標準化前または標準化後）
        
        グラフ構成:
        - X軸: 満足度
        - Y軸: 重要度
        - 4象限を色分け
        - 各項目をプロット（ラベル付き）
        - 中央線: 満足度・重要度の中央値
        - 象限ラベル: Ⅰ〜Ⅳ
        - 色分け:
            * Ⅰ（維持）: 青
            * Ⅱ（最優先改善）: 赤
            * Ⅲ（改善検討）: 黄
            * Ⅳ（過剰品質）: 緑
        
        Args:
            ipa_results: IPA分析結果
            output_path: 保存先パス
            use_rescaled: 標準化後データを使用するか
        
        Returns:
            保存先パス
        """
        if output_path is None:
            suffix = '_rescaled' if use_rescaled else ''
            output_path = f'graphs/ipa_matrix{suffix}.png'
        
        # IPA分析結果の取得
        if ipa_results is None:
            ipa_all = self.analysis_results.get('ipa_analysis', {})
            if use_rescaled:
                ipa_results = ipa_all.get('rescaled')
            else:
                ipa_results = ipa_all.get('original')
        
        if not ipa_results or 'items' not in ipa_results:
            print(f"警告: IPA分析データが見つかりません (use_rescaled={use_rescaled})")
            return ""
        
        # 中央値の取得
        settings = ipa_results.get('settings', {})
        sat_median = settings.get('satisfaction_median', 3.0)
        imp_median = settings.get('importance_median', 3.0)
        
        # データの準備
        items_data = ipa_results['items']
        
        # 象限ごとに色を設定
        quadrant_colors = {
            'Ⅰ': '#5cb85c',  # 緑（維持）
            'Ⅱ': '#d9534f',  # 赤（最優先改善）
            'Ⅲ': '#f0ad4e',  # 黄（改善検討）
            'Ⅳ': '#5bc0de'   # 青（過剰品質）
        }
        
        # グラフ作成
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 軸の範囲を決定（標準化後の場合は自動調整）
        if use_rescaled:
            # 標準化後データの範囲を取得
            all_sat = [d['satisfaction'] for d in items_data.values()]
            all_imp = [d['importance'] for d in items_data.values()]
            sat_min, sat_max = min(all_sat), max(all_sat)
            imp_min, imp_max = min(all_imp), max(all_imp)
            margin = 0.5
            x_min, x_max = sat_min - margin, sat_max + margin
            y_min, y_max = imp_min - margin, imp_max + margin
        else:
            x_min, x_max = 0.5, 5.5
            y_min, y_max = 0.5, 5.5
        
        # 象限の背景色
        ax.axhspan(imp_median, y_max, sat_median, x_max, alpha=0.1, color='green')    # Ⅰ
        ax.axhspan(imp_median, y_max, x_min, sat_median, alpha=0.1, color='red')      # Ⅱ
        ax.axhspan(y_min, imp_median, x_min, sat_median, alpha=0.1, color='yellow')   # Ⅲ
        ax.axhspan(y_min, imp_median, sat_median, x_max, alpha=0.1, color='blue')     # Ⅳ
        
        # 中央線
        ax.axvline(sat_median, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.axhline(imp_median, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
        
        # 各項目をプロット
        for item, data in items_data.items():
            satisfaction = data['satisfaction']
            importance = data['importance']
            quadrant = data['quadrant']
            
            color = quadrant_colors.get(quadrant, 'gray')
            
            ax.scatter(satisfaction, importance, s=200, 
                      color=color, alpha=0.7, edgecolor='black', linewidth=1.5)
            
            # ラベル（_rescaledを削除して表示）
            display_label = item.replace('_rescaled', '')
            ax.annotate(display_label, (satisfaction, importance),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, fontweight='bold')
        
        # 象限ラベル
        ax.text(sat_median + (x_max - sat_median)/2, imp_median + (y_max - imp_median)/2,
               'Ⅰ 維持エリア', ha='center', va='center',
               fontsize=12, fontweight='bold', alpha=0.5)
        ax.text((sat_median + x_min)/2, imp_median + (y_max - imp_median)/2,
               'Ⅱ 最優先改善', ha='center', va='center',
               fontsize=12, fontweight='bold', alpha=0.5)
        ax.text((sat_median + x_min)/2, (imp_median + y_min)/2,
               'Ⅲ 改善検討', ha='center', va='center',
               fontsize=12, fontweight='bold', alpha=0.5)
        ax.text(sat_median + (x_max - sat_median)/2, (imp_median + y_min)/2,
               'Ⅳ 過剰品質', ha='center', va='center',
               fontsize=12, fontweight='bold', alpha=0.5)
        
        title_suffix = '（標準化後）' if use_rescaled else '（標準化前）'
        ax.set_xlabel('満足度', fontsize=12)
        ax.set_ylabel('重要度', fontsize=12)
        ax.set_title(f'IPA分析マトリックス{title_suffix}', fontsize=14, fontweight='bold')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_ylim(0.5, 5.5)
        
        # グリッド
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        # 保存
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_all_graphs(self, output_dir: str = 'out/reports/graphs') -> Dict[str, str]:
        """
        全グラフの一括生成（標準化前と標準化後の両方）
        
        生成グラフ:
        - 満足度分布
        - 満足度ランキング
        - 相関ヒートマップ（標準化前と標準化後）
        - 属性別比較（複数）
        - IPAマトリックス（標準化前と標準化後）
        
        Args:
            output_dir: 出力先ディレクトリ
        
        Returns:
            生成されたグラフファイルのパス辞書
        """
        print("\nグラフ生成中...")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # 1. 総合満足度の分布
        print("  - 満足度分布グラフ...")
        path = self.plot_satisfaction_distribution(
            'overall_satisfaction',
            f'{output_dir}/satisfaction_distribution.png'
        )
        if path:
            generated_files['satisfaction_distribution'] = path
        
        # 2. 満足度ランキング
        print("  - 満足度ランキング...")
        path = self.plot_satisfaction_ranking(
            output_path=f'{output_dir}/satisfaction_ranking.png'
        )
        if path:
            generated_files['satisfaction_ranking'] = path
        
        # 3. 相関ヒートマップ（標準化前）
        print("  - 相関ヒートマップ（標準化前）...")
        corr_data_original = self.analysis_results.get('correlation_analysis', {}).get('original', {}).get('correlation_matrix')
        if corr_data_original:
            correlation_matrix_original = pd.DataFrame(corr_data_original)
            path = self.plot_correlation_heatmap(
                correlation_matrix=correlation_matrix_original,
                output_path=f'{output_dir}/correlation_heatmap_original.png'
            )
            if path:
                generated_files['correlation_heatmap_original'] = path
        
        # 相関ヒートマップ（標準化後）
        print("  - 相関ヒートマップ（標準化後）...")
        corr_data_rescaled = self.analysis_results.get('correlation_analysis', {}).get('rescaled', {}).get('correlation_matrix')
        if corr_data_rescaled:
            correlation_matrix_rescaled = pd.DataFrame(corr_data_rescaled)
            path = self.plot_correlation_heatmap(
                correlation_matrix=correlation_matrix_rescaled,
                output_path=f'{output_dir}/correlation_heatmap_rescaled.png'
            )
            if path:
                generated_files['correlation_heatmap_rescaled'] = path
        
        # 4. 属性別比較（標準化前と標準化後）
        print("  - 属性別比較グラフ（標準化前と標準化後）...")
        attr_analysis_all = self.analysis_results.get('attribute_analysis', {})
        
        # 標準化前の属性別グラフ
        attr_analysis_original = attr_analysis_all.get('original', attr_analysis_all)
        for attr_key in attr_analysis_original.keys():
            attr_name = attr_key.replace('by_', '')
            path = self.plot_attribute_comparison(
                attr_name,
                output_path=f'{output_dir}/attribute_comparison_{attr_name}_original.png',
                use_rescaled=False
            )
            if path:
                generated_files[f'attribute_{attr_name}_original'] = path
        
        # 標準化後の属性別グラフ
        attr_analysis_rescaled = attr_analysis_all.get('rescaled', {})
        for attr_key in attr_analysis_rescaled.keys():
            attr_name = attr_key.replace('by_', '')
            path = self.plot_attribute_comparison(
                attr_name,
                output_path=f'{output_dir}/attribute_comparison_{attr_name}_rescaled.png',
                use_rescaled=True
            )
            if path:
                generated_files[f'attribute_{attr_name}_rescaled'] = path
        
        # 5. IPAマトリックス（標準化前）
        print("  - IPAマトリックス（標準化前）...")
        path = self.plot_ipa_matrix(
            output_path=f'{output_dir}/ipa_matrix_original.png',
            use_rescaled=False
        )
        if path:
            generated_files['ipa_matrix_original'] = path
        
        # IPAマトリックス（標準化後）
        print("  - IPAマトリックス（標準化後）...")
        path = self.plot_ipa_matrix(
            output_path=f'{output_dir}/ipa_matrix_rescaled.png',
            use_rescaled=True
        )
        if path:
            generated_files['ipa_matrix_rescaled'] = path
        
        print(f"グラフ生成完了: {len(generated_files)}個のグラフを生成")
        
        return generated_files
    
    # ==========================================
    # 3. テキストレポート生成
    # ==========================================
    
    def generate_text_report(self, output_path: str) -> None:
        """
        テキスト形式の詳細レポート生成
        
        構成:
        1. エグゼクティブサマリー
        2. 調査概要
        3. 基本分析結果
        4. 詳細分析結果
        5. 改善提言
        
        Args:
            output_path: 出力先パス（.txt形式）
        """
        # エグゼクティブサマリーの生成
        summary = self.generate_executive_summary()
        
        lines = []
        lines.append("="*70)
        lines.append("IT部門サービス満足度調査 詳細レポート")
        lines.append("="*70)
        lines.append("")
        
        # 生成日時
        lines.append(f"生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append("")
        
        # 1. エグゼクティブサマリー
        lines.append("-"*70)
        lines.append("1. エグゼクティブサマリー")
        lines.append("-"*70)
        lines.append("")
        
        # 総合満足度
        if 'overall_satisfaction' in summary:
            overall = summary['overall_satisfaction']
            lines.append(f"総合満足度: {overall['value']:.2f}点（5点満点）")
            lines.append(f"測定方法: {overall['method']}")
            lines.append("")
        
        # 満足度分布
        if 'satisfaction_distribution' in summary:
            dist = summary['satisfaction_distribution']
            if 'satisfied' in dist:
                lines.append(f"満足以上（4-5点）: {dist['satisfied']['percentage']:.1f}%")
            if 'dissatisfied' in dist:
                lines.append(f"不満以下（1-2点）: {dist['dissatisfied']['percentage']:.1f}%")
            lines.append("")
        
        # 最優先改善項目
        if 'priority_improvements' in summary and summary['priority_improvements']:
            lines.append("【最優先改善項目】")
            for i, item in enumerate(summary['priority_improvements'], 1):
                lines.append(f"{i}. {item['name']}")
                lines.append(f"   満足度: {item['satisfaction']:.2f}, "
                           f"重要度: {item['importance']:.2f}, "
                           f"ギャップ: {item['gap']:.2f}")
            lines.append("")
        
        # 維持・強化項目
        if 'maintain_strengths' in summary and summary['maintain_strengths']:
            lines.append("【維持・強化項目】")
            for i, item in enumerate(summary['maintain_strengths'], 1):
                lines.append(f"{i}. {item['name']}")
                lines.append(f"   満足度: {item['satisfaction']:.2f}, "
                           f"重要度: {item['importance']:.2f}")
            lines.append("")
        
        # 2. 基本統計
        lines.append("-"*70)
        lines.append("2. 基本統計")
        lines.append("-"*70)
        lines.append("")
        
        desc_stats = self.analysis_results.get('basic_statistics', {}).get(
            'descriptive_stats', {})
        
        if desc_stats:
            lines.append(f"{'項目':<30} {'平均':<8} {'標準偏差':<8} {'有効数':<8}")
            lines.append("-"*70)
            for item, stats in desc_stats.items():
                if 'importance' not in item:  # 満足度項目のみ
                    lines.append(f"{item:<30} {stats['mean']:<8.2f} "
                               f"{stats['std']:<8.2f} {stats['valid_count']:<8}")
            lines.append("")
        
        # 3. 相関分析
        lines.append("-"*70)
        lines.append("3. 相関分析（総合満足度との相関）")
        lines.append("-"*70)
        lines.append("")
        
        corr_analysis = self.analysis_results.get('correlation_analysis', {}).get(
            'with_overall_satisfaction', {})
        
        if corr_analysis:
            # 相関係数でソート
            sorted_corr = sorted(corr_analysis.items(), 
                               key=lambda x: abs(x[1].get('correlation', 0)), 
                               reverse=True)
            
            lines.append(f"{'項目':<30} {'相関係数':<10} {'有意性':<10}")
            lines.append("-"*70)
            for item, data in sorted_corr:
                corr = data['correlation']
                sig = "***" if data.get('significant', False) else ""
                lines.append(f"{item:<30} {corr:<10.3f} {sig:<10}")
            lines.append("")
            lines.append("***: p < 0.05（有意）")
            lines.append("")
        
        # 4. IPA分析まとめ
        lines.append("-"*70)
        lines.append("4. IPA分析まとめ")
        lines.append("-"*70)
        lines.append("")
        
        ipa_results = self.analysis_results.get('ipa_analysis', {})
        if 'summary' in ipa_results:
            summary_data = ipa_results['summary']
            
            for quadrant, quadrant_name in [
                ('Ⅱ', '最優先改善エリア'),
                ('Ⅰ', '維持エリア'),
                ('Ⅲ', '改善検討エリア'),
                ('Ⅳ', '過剰品質エリア')
            ]:
                items = summary_data.get(quadrant, [])
                lines.append(f"【{quadrant_name}】")
                if items:
                    for item in items:
                        lines.append(f"  - {item}")
                else:
                    lines.append("  （該当なし）")
                lines.append("")
        
        # ファイルに書き込み
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"テキストレポート生成完了: {output_path}")
    
    def generate_markdown_report(self, output_path: str, graphs_dir: str = None) -> None:
        """
        Markdown形式のレポート生成
        
        構成:
        - テキストレポートと同様
        - Markdown記法で整形
        - 表形式のデータ表示
        - グラフ画像の埋め込み
        
        Args:
            output_path: 出力先パス（.md形式）
            graphs_dir: グラフディレクトリ（相対パス）
        """
        # エグゼクティブサマリーの生成
        summary = self.generate_executive_summary()
        
        # グラフディレクトリの設定
        if graphs_dir is None:
            graphs_dir = 'graphs'
        
        lines = []
        lines.append("# IT部門サービス満足度調査 詳細レポート")
        lines.append("")
        lines.append(f"**生成日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 目次
        lines.append("## 目次")
        lines.append("")
        lines.append("1. [エグゼクティブサマリー](#1-エグゼクティブサマリー)")
        lines.append("2. [基本統計](#2-基本統計)")
        lines.append("3. [相関分析](#3-相関分析)")
        lines.append("4. [属性別分析](#4-属性別分析)")
        lines.append("5. [IPA分析](#5-ipa分析)")
        lines.append("6. [グラフ](#6-グラフ)")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 1. エグゼクティブサマリー
        lines.append("## 1. エグゼクティブサマリー")
        lines.append("")
        
        # 総合満足度
        if 'overall_satisfaction' in summary:
            overall = summary['overall_satisfaction']
            lines.append(f"### 総合満足度: **{overall['value']:.2f}点**（5点満点）")
            lines.append("")
        
        # 満足度分布
        if 'satisfaction_distribution' in summary:
            dist = summary['satisfaction_distribution']
            lines.append("### 満足度分布")
            lines.append("")
            if 'satisfied' in dist:
                lines.append(f"- 満足以上（4-5点）: **{dist['satisfied']['percentage']:.1f}%**")
            if 'dissatisfied' in dist:
                lines.append(f"- 不満以下（1-2点）: **{dist['dissatisfied']['percentage']:.1f}%**")
            lines.append("")
        
        # 満足度分布グラフ
        lines.append("### 満足度分布グラフ")
        lines.append("")
        lines.append(f"![満足度分布]({graphs_dir}/satisfaction_distribution.png)")
        lines.append("")
        
        # 最優先改善項目
        if 'priority_improvements_original' in summary and summary['priority_improvements_original']:
            lines.append("### 最優先改善項目")
            lines.append("")
            lines.append("| 順位 | 項目 | 満足度 | 重要度 | ギャップ |")
            lines.append("|------|------|--------|--------|----------|")
            for i, item in enumerate(summary['priority_improvements_original'], 1):
                lines.append(f"| {i} | {item['name']} | {item['satisfaction']:.2f} | "
                           f"{item['importance']:.2f} | {item['gap']:.2f} |")
            lines.append("")
        
        # 維持・強化項目
        if 'maintain_strengths_original' in summary and summary['maintain_strengths_original']:
            lines.append("### 維持・強化項目")
            lines.append("")
            lines.append("| 順位 | 項目 | 満足度 | 重要度 |")
            lines.append("|------|------|--------|--------|")
            for i, item in enumerate(summary['maintain_strengths_original'], 1):
                lines.append(f"| {i} | {item['name']} | {item['satisfaction']:.2f} | "
                           f"{item['importance']:.2f} |")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # 2. 基本統計
        lines.append("## 2. 基本統計")
        lines.append("")
        
        desc_stats_all = self.analysis_results.get('basic_statistics', {}).get(
            'descriptive_stats', {})
        
        # 標準化前データを使用
        desc_stats = desc_stats_all.get('original', desc_stats_all)
        
        if desc_stats:
            lines.append("| 項目 | 平均 | 中央値 | 標準偏差 | 有効回答数 |")
            lines.append("|------|------|--------|----------|-----------|")
            for item, stats in desc_stats.items():
                if 'importance' not in item and 'rescaled' not in item:
                    lines.append(f"| {item} | {stats['mean']:.2f} | {stats['median']:.2f} | "
                               f"{stats['std']:.2f} | {stats['valid_count']} |")
            lines.append("")
        
        # 満足度ランキンググラフ
        lines.append("### 満足度ランキング")
        lines.append("")
        lines.append(f"![満足度ランキング]({graphs_dir}/satisfaction_ranking.png)")
        lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # 3. 相関分析
        lines.append("## 3. 相関分析")
        lines.append("")
        
        corr_analysis_all = self.analysis_results.get('correlation_analysis', {})
        corr_analysis_original = corr_analysis_all.get('original', corr_analysis_all)
        corr_analysis = corr_analysis_original.get('with_overall_satisfaction', {})
        
        if corr_analysis:
            sorted_corr = sorted(corr_analysis.items(),
                               key=lambda x: abs(x[1].get('correlation', 0)),
                               reverse=True)
            
            lines.append("### 総合満足度との相関")
            lines.append("")
            lines.append("| 項目 | 相関係数 | 有意性 |")
            lines.append("|------|----------|--------|")
            for item, data in sorted_corr:
                corr = data['correlation']
                sig = "***" if data.get('significant', False) else ""
                lines.append(f"| {item} | {corr:.3f} | {sig} |")
            lines.append("")
            lines.append("***: p < 0.05（有意）")
            lines.append("")
        
        # 相関ヒートマップ（標準化前のみ表示）
        lines.append("### 相関ヒートマップ")
        lines.append("")
        lines.append(f"![相関ヒートマップ]({graphs_dir}/correlation_heatmap_original.png)")
        lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # 4. 属性別分析
        lines.append("## 4. 属性別分析")
        lines.append("")
        
        attr_analysis_all = self.analysis_results.get('attribute_analysis', {})
        
        # 標準化前の属性別分析のみ表示
        attr_analysis_original = attr_analysis_all.get('original', attr_analysis_all)
        
        if attr_analysis_original:
            for attr_key in attr_analysis_original.keys():
                attr_name = attr_key.replace('by_', '')
                attr_data = attr_analysis_original[attr_key]
                
                if 'groups' in attr_data:
                    lines.append(f"### {attr_name}別の満足度")
                    lines.append("")
                    
                    # 統計表
                    groups_data = attr_data['groups']
                    lines.append("| グループ | 平均 | 標準偏差 | 人数 |")
                    lines.append("|----------|------|----------|------|")
                    for group, stats in groups_data.items():
                        lines.append(f"| {group} | {stats['mean']:.2f} | "
                                   f"{stats['std']:.2f} | {stats['n']} |")
                    lines.append("")
                    
                    # グラフ（標準化前のみ）
                    lines.append(f"![{attr_name}別比較]({graphs_dir}/attribute_comparison_{attr_name}_original.png)")
                    lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # 5. IPA分析
        lines.append("## 5. IPA分析")
        lines.append("")
        
        ipa_results_all = self.analysis_results.get('ipa_analysis', {})
        
        # 標準化前のIPA分析のみ表示
        ipa_results_original = ipa_results_all.get('original', ipa_results_all)
        if 'summary' in ipa_results_original:
            summary_data = ipa_results_original['summary']
            
            for quadrant, quadrant_name in [
                ('Ⅱ', '最優先改善エリア'),
                ('Ⅰ', '維持エリア'),
                ('Ⅲ', '改善検討エリア'),
                ('Ⅳ', '過剰品質エリア')
            ]:
                items = summary_data.get(quadrant, [])
                lines.append(f"### {quadrant_name}")
                lines.append("")
                if items:
                    for item in items:
                        lines.append(f"- {item}")
                else:
                    lines.append("（該当なし）")
                lines.append("")
        
        # IPAマトリックス（標準化前のみ）
        lines.append("### IPAマトリックス")
        lines.append("")
        lines.append(f"![IPAマトリックス]({graphs_dir}/ipa_matrix_original.png)")
        lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # 6. グラフ一覧
        lines.append("## 6. グラフ")
        lines.append("")
        lines.append("### 生成されたグラフ一覧")
        lines.append("")
        lines.append(f"1. [満足度分布]({graphs_dir}/satisfaction_distribution.png)")
        lines.append(f"2. [満足度ランキング]({graphs_dir}/satisfaction_ranking.png)")
        lines.append(f"3. [相関ヒートマップ]({graphs_dir}/correlation_heatmap_original.png)")
        
        # 属性別グラフ（標準化前のみ表示）
        graph_num = 4
        if attr_analysis_original:
            for attr_key in attr_analysis_original.keys():
                attr_name = attr_key.replace('by_', '')
                lines.append(f"{graph_num}. [{attr_name}別比較]({graphs_dir}/attribute_comparison_{attr_name}_original.png)")
                graph_num += 1
        
        lines.append(f"{graph_num}. [IPAマトリックス]({graphs_dir}/ipa_matrix_original.png)")
        lines.append("")
        
        # ファイルに書き込み
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"Markdownレポート生成完了: {output_path}")
    
    # ==========================================
    # 4. HTMLレポート生成
    # ==========================================
    
    def generate_html_report(self, output_path: str) -> None:
        """
        HTML形式のインタラクティブレポート生成
        
        内容:
        - Bootstrap CSSでスタイリング
        - グラフを画像として埋め込み
        - 表形式のデータ表示
        - 目次とナビゲーション
        - レスポンシブデザイン
        
        Args:
            output_path: 出力先パス（.html形式）
        """
        # エグゼクティブサマリーの生成
        summary = self.generate_executive_summary()
        
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang='ja'>")
        html.append("<head>")
        html.append("    <meta charset='UTF-8'>")
        html.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html.append("    <title>IT部門サービス満足度調査レポート</title>")
        html.append("    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css' rel='stylesheet'>")
        html.append("    <style>")
        html.append("        body { padding: 20px; }")
        html.append("        .metric { font-size: 2em; font-weight: bold; color: #0066cc; }")
        html.append("        .section { margin-top: 30px; }")
        html.append("        .graph-container { margin: 20px 0; }")
        html.append("        .graph-container img { max-width: 100%; height: auto; }")
        html.append("    </style>")
        html.append("</head>")
        html.append("<body>")
        
        # ヘッダー
        html.append("    <div class='container'>")
        html.append("        <h1 class='text-center'>IT部門サービス満足度調査レポート</h1>")
        html.append(f"        <p class='text-center text-muted'>生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>")
        html.append("        <hr>")
        
        # エグゼクティブサマリー
        html.append("        <div class='section'>")
        html.append("            <h2>エグゼクティブサマリー</h2>")
        
        if 'overall_satisfaction' in summary:
            overall = summary['overall_satisfaction']
            html.append("            <div class='alert alert-info'>")
            html.append(f"                <h3>総合満足度</h3>")
            html.append(f"                <p class='metric'>{overall['value']:.2f}点</p>")
            html.append(f"                <p>（5点満点、測定方法: {overall['method']}）</p>")
            html.append("            </div>")
        
        # 最優先改善項目
        if 'priority_improvements' in summary and summary['priority_improvements']:
            html.append("            <h3>最優先改善項目</h3>")
            html.append("            <table class='table table-striped'>")
            html.append("                <thead><tr><th>順位</th><th>項目</th><th>満足度</th><th>重要度</th><th>ギャップ</th></tr></thead>")
            html.append("                <tbody>")
            for i, item in enumerate(summary['priority_improvements'], 1):
                html.append(f"                <tr><td>{i}</td><td>{item['name']}</td>")
                html.append(f"                    <td>{item['satisfaction']:.2f}</td>")
                html.append(f"                    <td>{item['importance']:.2f}</td>")
                html.append(f"                    <td>{item['gap']:.2f}</td></tr>")
            html.append("                </tbody>")
            html.append("            </table>")
        
        html.append("        </div>")
        
        # グラフセクション（存在する場合）
        html.append("        <div class='section'>")
        html.append("            <h2>グラフ</h2>")
        html.append("            <p>グラフは別途生成されたPNGファイルをご参照ください。</p>")
        html.append("        </div>")
        
        # フッター
        html.append("    </div>")
        html.append("    <script src='https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js'></script>")
        html.append("</body>")
        html.append("</html>")
        
        # ファイルに書き込み
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html))
        
        print(f"HTMLレポート生成完了: {output_path}")
    
    # ==========================================
    # 5. PDFレポート生成
    # ==========================================
    
    def generate_pdf_report(self, output_path: str) -> None:
        """
        PDF形式のレポート生成
        
        内容:
        - エグゼクティブサマリー
        - グラフを含む詳細レポート
        - 表形式のデータ
        
        Args:
            output_path: 出力先パス（.pdf形式）
        """
        # PDFレポート生成は複雑なため、現時点ではMarkdownレポートへの参照を記載
        print("注意: PDF生成にはreportlabなどの追加ライブラリが必要です。")
        print("      代わりにMarkdownレポートを生成してください。")
    
    # ==========================================
    # 6. レポート生成パイプライン
    # ==========================================
    
    def generate_all_reports(self, output_dir: str = 'reports') -> Dict[str, str]:
        """
        全形式のレポート一括生成
        
        生成ファイル:
        - detailed_report.md
        - graphs/*.png (各種グラフ)
        
        Args:
            output_dir: 出力先ディレクトリ
        
        Returns:
            生成されたファイルのパス辞書
        """
        print("\nレポート生成開始...")
        print(f"出力ディレクトリ: {output_dir}")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        try:
            # 1. グラフ生成
            print("\n1. グラフ生成を開始...")
            graphs_dir = f'{output_dir}/graphs'
            print(f"   グラフ出力先: {graphs_dir}")
            graph_files = self.plot_all_graphs(graphs_dir)
            print(f"   生成されたグラフ: {len(graph_files)}個")
            generated_files.update(graph_files)
            
            # 2. Markdownレポート
            print("\n2. Markdownレポート生成...")
            md_path = f'{output_dir}/detailed_report.md'
            print(f"   出力先: {md_path}")
            self.generate_markdown_report(md_path, graphs_dir='graphs')
            generated_files['markdown_report'] = md_path
            print(f"   ✓ Markdownレポート生成完了")
            
            print(f"\n✓ レポート生成完了: {len(generated_files)}個のファイルを生成")
            
        except Exception as e:
            print(f"\n✗ エラー: レポート生成中に問題が発生しました")
            print(f"   エラー内容: {e}")
            print(f"   エラー種類: {type(e).__name__}")
            import traceback
            print("\n詳細なスタックトレース:")
            traceback.print_exc()
        
        print(f"\n最終的に生成されたファイル数: {len(generated_files)}")
        return generated_files
    
    # ==========================================
    # 7. ヘルパーメソッド
    # ==========================================
    
    def _setup_plot_style(self) -> None:
        """
        グラフのスタイル設定
        
        設定内容:
        - フォント設定（日本語対応）
        - カラーパレット
        - 図のサイズ
        - DPI設定
        """
        # スタイル設定
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("deep")
        
        # 日本語フォントを再設定（スタイル適用後に上書きされる可能性があるため）
        setup_japanese_font()
        
        # デフォルトの図のサイズ
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.dpi'] = 300
        
        # フォントサイズの設定
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
    
    def _format_number(self, value: float, decimal_places: int = 2) -> str:
        """
        数値のフォーマット
        
        Args:
            value: 数値
            decimal_places: 小数点以下の桁数
        
        Returns:
            フォーマット済み文字列
        """
        return f"{value:.{decimal_places}f}"
    
    def _create_summary_table(self, data: Dict[str, Any]) -> str:
        """
        サマリー表の生成
        
        Args:
            data: 表示するデータ
        
        Returns:
            表形式の文字列
        """
        # 簡易的なテーブル生成
        lines = []
        for key, value in data.items():
            lines.append(f"{key}: {value}")
        return '\n'.join(lines)


if __name__ == "__main__":
    # 使用例
    
    # 分析結果の読み込み
    with open('out/analysis_results.json', 'r', encoding='utf-8') as f:
        analysis_results = json.load(f)
    
    # レポート生成器の初期化
    generator = SurveyReportGenerator(
        analysis_results=analysis_results,
        config_file='config/config.yaml'
    )
    
    # 全レポート生成
    generated_files = generator.generate_all_reports(output_dir='out/reports')
    
    print("レポート生成完了")
    print("生成されたファイル:")
    for file_type, filepath in generated_files.items():
        print(f"  - {file_type}: {filepath}")