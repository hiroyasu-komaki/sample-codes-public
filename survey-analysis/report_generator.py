"""
分析レポート生成モジュール
分析結果をテキストファイルとして出力
"""

from typing import Dict
import json
from datetime import datetime


class ReportGenerator:
    """分析レポート生成クラス"""
    
    def __init__(self, analysis_results: Dict):
        """
        初期化
        
        Args:
            analysis_results: 分析結果の辞書
        """
        self.results = analysis_results
    
    def generate_full_report(self, output_file: str = 'analysis_report.txt'):
        """
        完全な分析レポートを生成
        
        Args:
            output_file: 出力ファイル名
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            # ヘッダー
            f.write(self._generate_header())
            
            # 1. データ品質レポート
            f.write(self._generate_data_quality_section())
            
            # 2. 基本統計レポート
            f.write(self._generate_descriptive_section())
            
            # 3. 相関分析レポート
            f.write(self._generate_correlation_section())
            
            # 4. 属性別分析レポート
            f.write(self._generate_attribute_section())
            
            # 5. IPA分析レポート
            f.write(self._generate_ipa_section())
            
            # 6. 回帰分析レポート
            f.write(self._generate_regression_section())
            
            # 7. 改善優先順位レポート
            f.write(self._generate_priority_section())
            
            # 8. 推奨アクション
            f.write(self._generate_recommendations())
            
            # フッター
            f.write(self._generate_footer())
    
    def _generate_header(self) -> str:
        """ヘッダー生成"""
        lines = []
        lines.append("="*80)
        lines.append("IT部門サービス満足度アンケート")
        lines.append("データ分析レポート")
        lines.append("="*80)
        lines.append(f"\n生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append("\n" + "-"*80 + "\n")
        return "\n".join(lines)
    
    def _generate_data_quality_section(self) -> str:
        """データ品質セクション生成"""
        if 'cleaning' not in self.results:
            return ""
        
        cleaning = self.results['cleaning']
        lines = []
        
        lines.append("\n■ 1. データ品質評価")
        lines.append("="*80)
        
        lines.append(f"\n【サンプル情報】")
        lines.append(f"元のサンプル数: {cleaning['original_count']:,}件")
        lines.append(f"分析対象サンプル数: {cleaning['cleaned_count']:,}件")
        
        if cleaning['original_count'] > cleaning['cleaned_count']:
            removed = cleaning['original_count'] - cleaning['cleaned_count']
            removed_rate = removed / cleaning['original_count'] * 100
            lines.append(f"除外されたサンプル: {removed}件 ({removed_rate:.1f}%)")
        
        lines.append(f"\n【欠損値率】")
        if cleaning['missing_rates']:
            for item, rate in cleaning['missing_rates'].items():
                status = "良好" if rate < 5 else "要注意" if rate < 15 else "問題あり"
                lines.append(f"{item:<25} {rate:>6.1f}%  [{status}]")
        else:
            lines.append("欠損値なし")
        
        lines.append(f"\n【代表性の確認】")
        if cleaning['representativeness']:
            for attr_name, dist in cleaning['representativeness'].items():
                lines.append(f"\n{attr_name}別分布:")
                for category, percentage in dist.items():
                    lines.append(f"  {category:<20} {percentage:>6.1f}%")
        
        lines.append("\n" + "-"*80 + "\n")
        return "\n".join(lines)
    
    def _generate_descriptive_section(self) -> str:
        """基本統計セクション生成"""
        if 'descriptive' not in self.results:
            return ""
        
        lines = []
        lines.append("\n■ 2. 基本統計（記述統計）")
        lines.append("="*80)
        
        lines.append("\n【満足度評価】（5点満点: 5=非常に満足 ～ 1=非常に不満）")
        lines.append("-"*80)
        lines.append(f"{'項目':<25} {'平均':<7} {'標準偏差':<8} {'95%信頼区間':<20} {'満足以上%'}")
        lines.append("-"*80)
        
        for item, stats in self.results['descriptive'].items():
            ci_text = f"{stats['95%信頼区間下限']:.2f}～{stats['95%信頼区間上限']:.2f}"
            lines.append(
                f"{item:<25} "
                f"{stats['平均値']:<7.2f} "
                f"{stats['標準偏差']:<8.2f} "
                f"{ci_text:<20} "
                f"{stats['満足以上の割合']:>6.1f}%"
            )
        
        lines.append("-"*80)
        
        # 満足度分布の詳細
        lines.append("\n【満足度分布の詳細】")
        for item, stats in self.results['descriptive'].items():
            lines.append(f"\n{item}:")
            if 'distribution' in stats or '分布' in stats:
                dist = stats.get('分布', stats.get('distribution', {}))
                for rating, percent in sorted(dist.items()):
                    bar_length = int(percent / 2)
                    bar = "■" * bar_length
                    lines.append(f"  {rating}点: {percent:>5.1f}% {bar}")
        
        lines.append("\n" + "-"*80 + "\n")
        return "\n".join(lines)
    
    def _generate_correlation_section(self) -> str:
        """相関分析セクション生成"""
        if 'correlation' not in self.results or not self.results['correlation']:
            return ""
        
        lines = []
        lines.append("\n■ 3. 相関分析")
        lines.append("="*80)
        
        lines.append("\n【総合満足度と各項目の相関】")
        lines.append("-"*80)
        lines.append(f"{'項目':<30} {'相関係数':<12} {'p値':<10} {'有意性'}")
        lines.append("-"*80)
        
        # 相関係数の大きさでソート
        sorted_corr = sorted(
            self.results['correlation'].items(),
            key=lambda x: abs(x[1]['相関係数']),
            reverse=True
        )
        
        for item, corr_data in sorted_corr:
            lines.append(
                f"{item:<30} "
                f"{corr_data['相関係数']:<12.3f} "
                f"{corr_data['p値']:<10.4f} "
                f"{corr_data['有意性']}"
            )
        
        lines.append("-"*80)
        
        # 解釈ガイド
        lines.append("\n【相関係数の解釈】")
        lines.append("  |r| >= 0.7  : 強い相関")
        lines.append("  0.4 <= |r| < 0.7 : 中程度の相関")
        lines.append("  0.2 <= |r| < 0.4 : 弱い相関")
        lines.append("  |r| < 0.2  : ほぼ相関なし")
        
        lines.append("\n" + "-"*80 + "\n")
        return "\n".join(lines)
    
    def _generate_attribute_section(self) -> str:
        """属性別分析セクション生成"""
        if 'attribute' not in self.results or not self.results['attribute']:
            return ""
        
        lines = []
        lines.append("\n■ 4. 属性別分析")
        lines.append("="*80)
        
        for attr_name, attr_data in self.results['attribute'].items():
            lines.append(f"\n【{attr_name}別満足度】")
            lines.append("-"*80)
            
            if '総合満足度' in attr_data:
                lines.append(f"{'カテゴリ':<20} {'平均値':<10} {'標準偏差':<10} {'サンプル数'}")
                lines.append("-"*80)
                
                for category, stats in attr_data['総合満足度'].items():
                    lines.append(
                        f"{category:<20} "
                        f"{stats['平均値']:<10.2f} "
                        f"{stats['標準偏差']:<10.2f} "
                        f"{stats['サンプル数']:>8}件"
                    )
            
            if 'ANOVA' in attr_data:
                anova = attr_data['ANOVA']
                lines.append(f"\n分散分析（ANOVA）結果:")
                lines.append(f"  F値: {anova['F値']:.3f}")
                lines.append(f"  p値: {anova['p値']:.4f}")
                lines.append(f"  統計的有意差: {anova['有意差']}")
            
            lines.append("")
        
        lines.append("-"*80 + "\n")
        return "\n".join(lines)
    
    def _generate_ipa_section(self) -> str:
        """IPA分析セクション生成"""
        if 'ipa' not in self.results or not self.results['ipa']:
            return ""
        
        lines = []
        lines.append("\n■ 5. IPA分析（重要度-満足度分析）")
        lines.append("="*80)
        
        lines.append("\n【各項目の位置づけ】")
        lines.append("-"*80)
        lines.append(f"{'項目':<30} {'満足度':<10} {'重要度':<10} {'象限'}")
        lines.append("-"*80)
        
        for item, ipa_data in self.results['ipa'].items():
            lines.append(
                f"{item:<30} "
                f"{ipa_data['満足度']:<10.2f} "
                f"{ipa_data['重要度']:<10.2f} "
                f"{ipa_data['象限']}"
            )
        
        lines.append("-"*80)
        
        # 象限の説明
        lines.append("\n【象限の解釈】")
        lines.append("  第1象限（最優先改善エリア）: 重要度高・満足度低 → 最優先で改善")
        lines.append("  第2象限（維持エリア）      : 重要度高・満足度高 → 現状維持")
        lines.append("  第3象限（改善検討エリア）  : 重要度低・満足度低 → 状況に応じて改善")
        lines.append("  第4象限（過剰品質エリア）  : 重要度低・満足度高 → リソース配分見直し")
        
        lines.append("\n" + "-"*80 + "\n")
        return "\n".join(lines)
    
    def _generate_regression_section(self) -> str:
        """回帰分析セクション生成"""
        if 'regression' not in self.results or not self.results['regression']:
            return ""
        
        lines = []
        lines.append("\n■ 6. 回帰分析")
        lines.append("="*80)
        
        lines.append("\n【総合満足度への影響度分析】")
        lines.append("-"*80)
        
        if '係数' in self.results['regression']:
            lines.append(f"{'項目':<30} {'標準化係数':<15} {'影響度ランク'}")
            lines.append("-"*80)
            
            # ランクでソート
            sorted_items = sorted(
                self.results['regression']['係数'].items(),
                key=lambda x: x[1]['影響度ランク']
            )
            
            for item, coef_data in sorted_items:
                lines.append(
                    f"{item:<30} "
                    f"{coef_data['標準化係数']:<15.3f} "
                    f"{coef_data['影響度ランク']}位"
                )
            
            lines.append("-"*80)
            lines.append(f"\nサンプル数: {self.results['regression']['サンプル数']}件")
        
        lines.append("\n【解釈】")
        lines.append("標準化係数が大きいほど、総合満足度への影響が大きいことを示します。")
        
        lines.append("\n" + "-"*80 + "\n")
        return "\n".join(lines)
    
    def _generate_priority_section(self) -> str:
        """改善優先順位セクション生成"""
        if 'priority' not in self.results:
            return ""
        
        lines = []
        lines.append("\n■ 7. 改善優先順位")
        lines.append("="*80)
        
        priority = self.results['priority']
        
        if priority['最優先改善項目']:
            lines.append("\n【最優先改善項目】")
            lines.append("※ 重要度が高く満足度が低い項目（早急な対応が必要）")
            lines.append("-"*80)
            
            for i, item in enumerate(priority['最優先改善項目'], 1):
                lines.append(f"\n{i}. {item['項目']}")
                lines.append(f"   満足度: {item['満足度']:.2f}点")
                lines.append(f"   重要度: {item['重要度']:.2f}点")
                lines.append(f"   優先度スコア: {item['優先度スコア']:.2f}")
                lines.append(f"   分類: {item['象限']}")
        
        if priority['改善推奨項目']:
            lines.append("\n【改善推奨項目】")
            lines.append("※ 満足度向上の余地がある項目")
            lines.append("-"*80)
            
            for i, item in enumerate(priority['改善推奨項目'], 1):
                lines.append(f"\n{i}. {item['項目']}")
                lines.append(f"   満足度: {item['満足度']:.2f}点")
                lines.append(f"   重要度: {item['重要度']:.2f}点")
        
        if priority['維持項目']:
            lines.append("\n【維持項目】")
            lines.append("※ 現状の水準を維持")
            lines.append("-"*80)
            
            for i, item in enumerate(priority['維持項目'], 1):
                lines.append(f"{i}. {item['項目']} (満足度: {item['満足度']:.2f})")
        
        lines.append("\n" + "-"*80 + "\n")
        return "\n".join(lines)
    
    def _generate_recommendations(self) -> str:
        """推奨アクション生成"""
        lines = []
        lines.append("\n■ 8. 推奨アクション")
        lines.append("="*80)
        
        lines.append("\n【短期施策（1-3ヶ月）】")
        if 'priority' in self.results and self.results['priority']['最優先改善項目']:
            for item in self.results['priority']['最優先改善項目'][:2]:
                lines.append(f"・{item['項目']}の改善")
                lines.append(f"  現状分析と具体的な改善計画の策定")
        
        lines.append("\n【中期施策（3-6ヶ月）】")
        lines.append("・改善効果の測定と評価")
        lines.append("・追加改善項目の実施")
        lines.append("・従業員フィードバックの収集")
        
        lines.append("\n【長期施策（6-12ヶ月）】")
        lines.append("・定期的な満足度調査の実施")
        lines.append("・PDCAサイクルの確立")
        lines.append("・ベストプラクティスの共有")
        
        lines.append("\n" + "-"*80 + "\n")
        return "\n".join(lines)
    
    def _generate_footer(self) -> str:
        """フッター生成"""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("レポート終了")
        lines.append("="*80 + "\n")
        return "\n".join(lines)
    
    def save_json(self, output_file: str = 'analysis_results.json'):
        """
        分析結果をJSON形式で保存
        
        Args:
            output_file: 出力ファイル名
        """
        # NumPy型をPython標準型に変換
        def convert_to_serializable(obj):
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_to_serializable(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            else:
                return obj
        
        serializable_results = convert_to_serializable(self.results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
