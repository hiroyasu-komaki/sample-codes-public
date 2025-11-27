"""
IT部門サービス満足度アンケート データ分析モジュール
統計アプローチに基づいた包括的な分析を実施
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class SurveyDataAnalyser:
    """アンケートデータの分析クラス"""
    
    def __init__(self, data: pd.DataFrame):
        """
        初期化
        
        Args:
            data: アンケートデータのDataFrame
        """
        self.data = data.copy()
        self.results = {}
        
        # 満足度項目の定義
        self.satisfaction_items = [
            'overall_satisfaction',
            'response_speed',
            'technical_competence',
            'explanation_clarity',
            'service_politeness',
            'system_stability',
            'security_measures',
            'new_system_support'
        ]
        
        # 重要度項目の定義
        self.importance_items = [
            'response_speed_importance',
            'technical_competence_importance',
            'explanation_clarity_importance',
            'service_politeness_importance'
        ]
        
        # 日本語項目名のマッピング
        self.item_names = {
            'overall_satisfaction': '総合満足度',
            'response_speed': '対応スピード',
            'technical_competence': '技術的解決力',
            'explanation_clarity': '説明のわかりやすさ',
            'service_politeness': '対応の丁寧さ',
            'system_stability': 'システムの安定性',
            'security_measures': 'セキュリティ対策',
            'new_system_support': '新システム導入支援',
            'response_speed_importance': '対応スピード重要度',
            'technical_competence_importance': '技術的解決力重要度',
            'explanation_clarity_importance': '説明のわかりやすさ重要度',
            'service_politeness_importance': '対応の丁寧さ重要度'
        }
    
    def run_full_analysis(self) -> Dict:
        """
        全分析を実行
        
        Returns:
            分析結果を含む辞書
        """
        print("\n" + "="*70)
        print("データ分析実行中...")
        print("="*70)
        
        # 1. データクリーニング
        print("\n[1/7] データクリーニング...")
        self.results['cleaning'] = self.data_cleaning()
        
        # 2. 基本分析
        print("[2/7] 基本分析（記述統計）...")
        self.results['descriptive'] = self.descriptive_statistics()
        
        # 3. 相関分析
        print("[3/7] 相関分析...")
        self.results['correlation'] = self.correlation_analysis()
        
        # 4. 属性別分析
        print("[4/7] 属性別分析...")
        self.results['attribute'] = self.attribute_analysis()
        
        # 5. IPA分析
        print("[5/7] IPA分析（重要度-満足度分析）...")
        self.results['ipa'] = self.ipa_analysis()
        
        # 6. 回帰分析
        print("[6/7] 回帰分析...")
        self.results['regression'] = self.regression_analysis()
        
        # 7. 改善優先順位
        print("[7/7] 改善優先順位の決定...")
        self.results['priority'] = self.determine_priority()
        
        print("\n分析完了！\n")
        return self.results
    
    def data_cleaning(self) -> Dict:
        """
        データクリーニング
        欠損値の処理と代表性の確認
        
        Returns:
            クリーニング結果
        """
        result = {
            'original_count': len(self.data),
            'missing_rates': {},
            'cleaned_count': 0,
            'representativeness': {}
        }
        
        # 欠損値率の確認
        for item in self.satisfaction_items:
            if item in self.data.columns:
                missing_rate = self.data[item].isna().sum() / len(self.data) * 100
                result['missing_rates'][self.item_names[item]] = missing_rate
        
        # 欠損値処理（5%未満はリストワイズ削除、5-15%は平均値補完）
        cleaned_data = self.data.copy()
        
        for item in self.satisfaction_items:
            if item in cleaned_data.columns:
                missing_rate = cleaned_data[item].isna().sum() / len(cleaned_data) * 100
                
                if missing_rate < 5.0:
                    # 5%未満：リストワイズ削除
                    cleaned_data = cleaned_data.dropna(subset=[item])
                elif 5.0 <= missing_rate <= 15.0:
                    # 5-15%：平均値補完
                    mean_value = cleaned_data[item].mean()
                    cleaned_data[item].fillna(mean_value, inplace=True)
        
        self.data = cleaned_data
        result['cleaned_count'] = len(self.data)
        
        # 代表性の確認（属性分布）
        if 'department' in self.data.columns:
            dept_dist = self.data['department'].value_counts(normalize=True) * 100
            result['representativeness']['部署'] = dept_dist.to_dict()
        
        if 'position' in self.data.columns:
            pos_dist = self.data['position'].value_counts(normalize=True) * 100
            result['representativeness']['職位'] = pos_dist.to_dict()
        
        return result
    
    def descriptive_statistics(self) -> Dict:
        """
        記述統計
        平均値、標準偏差、95%信頼区間の算出
        
        Returns:
            記述統計結果
        """
        result = {}
        
        for item in self.satisfaction_items:
            if item in self.data.columns:
                valid_data = self.data[item].dropna()
                n = len(valid_data)
                
                if n > 0:
                    mean = valid_data.mean()
                    std = valid_data.std()
                    se = std / np.sqrt(n)
                    
                    # t分布を使用した95%信頼区間
                    t_value = stats.t.ppf(0.975, n - 1)
                    ci_lower = mean - t_value * se
                    ci_upper = mean + t_value * se
                    
                    # 満足度分布
                    dist = valid_data.value_counts(normalize=True).sort_index() * 100
                    satisfied_rate = (valid_data >= 4).sum() / n * 100
                    
                    result[self.item_names[item]] = {
                        '平均値': round(mean, 2),
                        '標準偏差': round(std, 2),
                        '標準誤差': round(se, 4),
                        'サンプル数': n,
                        '95%信頼区間下限': round(ci_lower, 2),
                        '95%信頼区間上限': round(ci_upper, 2),
                        '満足以上の割合': round(satisfied_rate, 1),
                        '分布': {int(k): round(v, 1) for k, v in dist.items()}
                    }
        
        return result
    
    def correlation_analysis(self) -> Dict:
        """
        相関分析
        総合満足度と各項目の相関
        
        Returns:
            相関分析結果
        """
        result = {}
        
        if 'overall_satisfaction' not in self.data.columns:
            return result
        
        overall = self.data['overall_satisfaction'].dropna()
        
        for item in self.satisfaction_items:
            if item != 'overall_satisfaction' and item in self.data.columns:
                item_data = self.data[item].dropna()
                
                # 共通のインデックスでデータを取得
                common_idx = overall.index.intersection(item_data.index)
                if len(common_idx) > 2:
                    corr, p_value = stats.pearsonr(
                        overall.loc[common_idx],
                        item_data.loc[common_idx]
                    )
                    
                    result[self.item_names[item]] = {
                        '相関係数': round(corr, 3),
                        'p値': round(p_value, 4),
                        '有意性': '有意 (p<0.01)' if p_value < 0.01 else 
                                  '有意 (p<0.05)' if p_value < 0.05 else '非有意'
                    }
        
        return result
    
    def attribute_analysis(self) -> Dict:
        """
        属性別分析
        部署別、職位別、ITスキル別の満足度差異
        
        Returns:
            属性別分析結果
        """
        result = {}
        
        attributes = {
            'department': '部署',
            'position': '職位',
            'it_skill_level': 'ITスキル'
        }
        
        for attr_col, attr_name in attributes.items():
            if attr_col not in self.data.columns:
                continue
            
            result[attr_name] = {}
            
            # 総合満足度の属性別平均
            if 'overall_satisfaction' in self.data.columns:
                attr_means = self.data.groupby(attr_col)['overall_satisfaction'].agg([
                    ('平均値', 'mean'),
                    ('標準偏差', 'std'),
                    ('サンプル数', 'count')
                ])
                
                result[attr_name]['総合満足度'] = {
                    idx: {
                        '平均値': round(row['平均値'], 2),
                        '標準偏差': round(row['標準偏差'], 2),
                        'サンプル数': int(row['サンプル数'])
                    }
                    for idx, row in attr_means.iterrows()
                }
                
                # 分散分析（ANOVA）
                groups = [group for name, group in 
                         self.data.groupby(attr_col)['overall_satisfaction'] 
                         if len(group.dropna()) > 0]
                
                if len(groups) > 1:
                    f_stat, p_value = stats.f_oneway(*groups)
                    result[attr_name]['ANOVA'] = {
                        'F値': round(f_stat, 3),
                        'p値': round(p_value, 4),
                        '有意差': 'あり (p<0.05)' if p_value < 0.05 else 'なし'
                    }
        
        return result
    
    def ipa_analysis(self) -> Dict:
        """
        IPA分析（重要度-満足度分析）
        
        Returns:
            IPA分析結果
        """
        result = {}
        
        # 重要度と満足度のマッピング
        ipa_pairs = {
            'response_speed': 'response_speed_importance',
            'technical_competence': 'technical_competence_importance',
            'explanation_clarity': 'explanation_clarity_importance',
            'service_politeness': 'service_politeness_importance'
        }
        
        for sat_item, imp_item in ipa_pairs.items():
            if sat_item in self.data.columns and imp_item in self.data.columns:
                sat_mean = self.data[sat_item].mean()
                imp_mean = self.data[imp_item].mean()
                
                # 象限の判定
                sat_threshold = 3.0  # 満足度の基準
                imp_threshold = 3.0  # 重要度の基準
                
                if imp_mean >= imp_threshold and sat_mean < sat_threshold:
                    quadrant = '第1象限（最優先改善エリア）'
                elif imp_mean >= imp_threshold and sat_mean >= sat_threshold:
                    quadrant = '第2象限（維持エリア）'
                elif imp_mean < imp_threshold and sat_mean < sat_threshold:
                    quadrant = '第3象限（改善検討エリア）'
                else:
                    quadrant = '第4象限（過剰品質エリア）'
                
                result[self.item_names[sat_item]] = {
                    '満足度': round(sat_mean, 2),
                    '重要度': round(imp_mean, 2),
                    '象限': quadrant
                }
        
        return result
    
    def regression_analysis(self) -> Dict:
        """
        回帰分析
        総合満足度を目的変数とした重回帰分析
        
        Returns:
            回帰分析結果
        """
        result = {}
        
        if 'overall_satisfaction' not in self.data.columns:
            return result
        
        # 説明変数として使用する満足度項目
        explanatory_items = [item for item in self.satisfaction_items 
                           if item != 'overall_satisfaction' and item in self.data.columns]
        
        if len(explanatory_items) == 0:
            return result
        
        # 欠損値を除外
        analysis_data = self.data[['overall_satisfaction'] + explanatory_items].dropna()
        
        if len(analysis_data) < 10:
            return result
        
        y = analysis_data['overall_satisfaction']
        X = analysis_data[explanatory_items]
        
        # 標準化（β係数の比較のため）
        X_std = (X - X.mean()) / X.std()
        y_std = (y - y.mean()) / y.std()
        
        # 重回帰分析の実行
        coefficients = {}
        for item in explanatory_items:
            # 単回帰で各変数の影響度を算出
            X_single = analysis_data[item].values.reshape(-1, 1)
            y_vals = y.values
            
            # 相関係数を標準化回帰係数の近似値として使用
            corr = np.corrcoef(X_single.flatten(), y_vals)[0, 1]
            
            coefficients[self.item_names[item]] = {
                '標準化係数': round(corr, 3),
                '影響度ランク': 0  # 後で設定
            }
        
        # ランキングの設定
        sorted_items = sorted(coefficients.items(), 
                            key=lambda x: abs(x[1]['標準化係数']), 
                            reverse=True)
        
        for rank, (item_name, data) in enumerate(sorted_items, 1):
            coefficients[item_name]['影響度ランク'] = rank
        
        result['係数'] = coefficients
        result['サンプル数'] = len(analysis_data)
        
        return result
    
    def determine_priority(self) -> Dict:
        """
        改善優先順位の決定
        
        Returns:
            改善優先順位
        """
        result = {
            '最優先改善項目': [],
            '改善推奨項目': [],
            '維持項目': []
        }
        
        # IPA分析と満足度から優先順位を決定
        if 'ipa' in self.results and 'descriptive' in self.results:
            priorities = []
            
            for item_name, ipa_data in self.results['ipa'].items():
                desc_data = self.results['descriptive'].get(item_name, {})
                
                sat_score = ipa_data.get('満足度', 0)
                imp_score = ipa_data.get('重要度', 0)
                quadrant = ipa_data.get('象限', '')
                
                # 優先度スコアの計算（重要度が高く満足度が低いほど高スコア）
                priority_score = imp_score * (5 - sat_score)
                
                priorities.append({
                    '項目': item_name,
                    '満足度': sat_score,
                    '重要度': imp_score,
                    '優先度スコア': round(priority_score, 2),
                    '象限': quadrant
                })
            
            # 優先度スコアでソート
            priorities.sort(key=lambda x: x['優先度スコア'], reverse=True)
            
            # 分類
            for p in priorities:
                if '最優先' in p['象限']:
                    result['最優先改善項目'].append(p)
                elif p['満足度'] < 3.0 and p['重要度'] >= 2.5:
                    result['改善推奨項目'].append(p)
                else:
                    result['維持項目'].append(p)
        
        return result
    
    def get_summary_statistics(self) -> str:
        """
        サマリー統計を文字列で返す
        
        Returns:
            サマリー統計の文字列
        """
        if not self.results:
            return "分析が実行されていません。"
        
        lines = []
        lines.append("\n" + "="*70)
        lines.append("分析結果サマリー")
        lines.append("="*70)
        
        # データクリーニング結果
        if 'cleaning' in self.results:
            cleaning = self.results['cleaning']
            lines.append(f"\n【データ品質】")
            lines.append(f"元のサンプル数: {cleaning['original_count']}件")
            lines.append(f"分析対象サンプル数: {cleaning['cleaned_count']}件")
            
            if cleaning['missing_rates']:
                lines.append(f"\n欠損値率:")
                for item, rate in cleaning['missing_rates'].items():
                    lines.append(f"  {item}: {rate:.1f}%")
        
        # 基本統計
        if 'descriptive' in self.results:
            lines.append(f"\n【満足度評価（5点満点）】")
            for item, stats in self.results['descriptive'].items():
                ci_text = f"{stats['95%信頼区間下限']}～{stats['95%信頼区間上限']}"
                lines.append(f"{item}: {stats['平均値']}点 " +
                           f"(95%CI: {ci_text}点, " +
                           f"満足以上: {stats['満足以上の割合']}%)")
        
        # 相関分析
        if 'correlation' in self.results and self.results['correlation']:
            lines.append(f"\n【総合満足度との相関】")
            sorted_corr = sorted(self.results['correlation'].items(),
                               key=lambda x: abs(x[1]['相関係数']),
                               reverse=True)
            for item, corr_data in sorted_corr:
                lines.append(f"{item}: r={corr_data['相関係数']} " +
                           f"({corr_data['有意性']})")
        
        # IPA分析
        if 'ipa' in self.results and self.results['ipa']:
            lines.append(f"\n【IPA分析（重要度-満足度分析）】")
            for item, ipa_data in self.results['ipa'].items():
                lines.append(f"{item}:")
                lines.append(f"  満足度: {ipa_data['満足度']}点, " +
                           f"重要度: {ipa_data['重要度']}点")
                lines.append(f"  → {ipa_data['象限']}")
        
        # 改善優先順位
        if 'priority' in self.results:
            priority = self.results['priority']
            
            if priority['最優先改善項目']:
                lines.append(f"\n【最優先改善項目】")
                for i, item in enumerate(priority['最優先改善項目'], 1):
                    lines.append(f"{i}. {item['項目']} " +
                               f"(満足度: {item['満足度']}, " +
                               f"重要度: {item['重要度']}, " +
                               f"優先度: {item['優先度スコア']})")
            
            if priority['改善推奨項目']:
                lines.append(f"\n【改善推奨項目】")
                for i, item in enumerate(priority['改善推奨項目'], 1):
                    lines.append(f"{i}. {item['項目']} " +
                               f"(満足度: {item['満足度']}, " +
                               f"重要度: {item['重要度']})")
        
        lines.append("\n" + "="*70)
        
        return "\n".join(lines)
