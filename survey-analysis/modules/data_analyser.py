"""
データ分析モジュール

前処理済みデータの統計分析を実行します。
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import yaml
import json
from pathlib import Path
from scipy import stats


class SurveyDataAnalyser:
    """アンケートデータ分析クラス"""
    
    def __init__(self, 
                 config_file: str = 'config/survey_questions.yaml',
                 main_config_file: str = 'config/config.yaml'):
        """
        初期化
        
        Args:
            config_file: アンケート項目定義ファイルのパス
            main_config_file: メイン設定ファイルのパス
        """
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        with open(main_config_file, 'r', encoding='utf-8') as f:
            self.main_config = yaml.safe_load(f)
        
        self.data = None
        self.analysis_results = {}
        
        # 分析用のカラム名を抽出
        self._extract_column_names()
    
    def _extract_column_names(self):
        """設定ファイルから分析対象のカラム名を抽出"""
        self.satisfaction_columns = list(self.config['satisfaction_ratings'].keys())
        self.importance_columns = list(self.config['importance_ratings'].keys())
        self.attribute_columns = list(self.config['respondent_attributes'].keys())
        
        # リスケール版のカラム名も追加
        self.satisfaction_columns_rescaled = [f'{col}_rescaled' for col in self.satisfaction_columns]
        self.importance_columns_rescaled = [f'{col}_rescaled' for col in self.importance_columns]
        
        # 満足度と重要度のペア（IPA分析用）
        self.ipa_pairs = {
            'response_speed': 'response_speed_importance',
            'technical_competence': 'technical_competence_importance',
            'explanation_clarity': 'explanation_clarity_importance',
            'service_politeness': 'service_politeness_importance'
        }
        
        # リスケール版のペアも定義
        self.ipa_pairs_rescaled = {
            f'{k}_rescaled': f'{v}_rescaled' for k, v in self.ipa_pairs.items()
        }
    
    def load_data(self, filepath: str) -> None:
        """
        前処理済みデータの読み込み
        
        Args:
            filepath: 前処理済みCSVファイルのパス
        """
        self.data = pd.read_csv(filepath, encoding='utf-8-sig')
        print(f"データ読み込み完了: {self.data.shape[0]}行 × {self.data.shape[1]}列")
    
    # ==========================================
    # 1. 基本分析
    # ==========================================
    
    def calculate_descriptive_statistics(self) -> Dict[str, Any]:
        """
        記述統計の計算（標準化前と標準化後の両方）
        
        計算内容:
        - 平均値（mean）
        - 中央値（median）
        - 標準偏差（std）
        - 最小値・最大値
        - 四分位数（Q1, Q3）
        - 欠損数
        
        Returns:
            各項目の記述統計量（original と rescaled）
        """
        descriptive_stats = {
            'original': {},
            'rescaled': {}
        }
        
        # 満足度項目の統計（標準化前）
        for col in self.satisfaction_columns:
            if col in self.data.columns:
                series = self.data[col]
                valid_data = series.dropna()
                
                if len(valid_data) > 0:
                    descriptive_stats['original'][col] = {
                        'mean': float(valid_data.mean()),
                        'median': float(valid_data.median()),
                        'std': float(valid_data.std()),
                        'min': float(valid_data.min()),
                        'max': float(valid_data.max()),
                        'q1': float(valid_data.quantile(0.25)),
                        'q3': float(valid_data.quantile(0.75)),
                        'missing_count': int(series.isna().sum()),
                        'valid_count': int(len(valid_data))
                    }
        
        # 満足度項目の統計（標準化後）
        for col in self.satisfaction_columns_rescaled:
            if col in self.data.columns:
                series = self.data[col]
                valid_data = series.dropna()
                
                if len(valid_data) > 0:
                    descriptive_stats['rescaled'][col] = {
                        'mean': float(valid_data.mean()),
                        'median': float(valid_data.median()),
                        'std': float(valid_data.std()),
                        'min': float(valid_data.min()),
                        'max': float(valid_data.max()),
                        'q1': float(valid_data.quantile(0.25)),
                        'q3': float(valid_data.quantile(0.75)),
                        'missing_count': int(series.isna().sum()),
                        'valid_count': int(len(valid_data))
                    }
        
        # 重要度項目の統計（標準化前）
        for col in self.importance_columns:
            if col in self.data.columns:
                series = self.data[col]
                valid_data = series.dropna()
                
                if len(valid_data) > 0:
                    descriptive_stats['original'][col] = {
                        'mean': float(valid_data.mean()),
                        'median': float(valid_data.median()),
                        'std': float(valid_data.std()),
                        'min': float(valid_data.min()),
                        'max': float(valid_data.max()),
                        'q1': float(valid_data.quantile(0.25)),
                        'q3': float(valid_data.quantile(0.75)),
                        'missing_count': int(series.isna().sum()),
                        'valid_count': int(len(valid_data))
                    }
        
        # 重要度項目の統計（標準化後）
        for col in self.importance_columns_rescaled:
            if col in self.data.columns:
                series = self.data[col]
                valid_data = series.dropna()
                
                if len(valid_data) > 0:
                    descriptive_stats['rescaled'][col] = {
                        'mean': float(valid_data.mean()),
                        'median': float(valid_data.median()),
                        'std': float(valid_data.std()),
                        'min': float(valid_data.min()),
                        'max': float(valid_data.max()),
                        'q1': float(valid_data.quantile(0.25)),
                        'q3': float(valid_data.quantile(0.75)),
                        'missing_count': int(series.isna().sum()),
                        'valid_count': int(len(valid_data))
                    }
        
        return descriptive_stats
    
    def calculate_satisfaction_distribution(self) -> Dict[str, Any]:
        """
        満足度分布の計算
        
        計算内容:
        - 各評価値（1-5）の件数・割合
        - 満足以上（4-5点）の割合
        - 不満以下（1-2点）の割合
        
        Returns:
            満足度分布データ
        """
        distribution = {}
        
        for col in self.satisfaction_columns:
            if col in self.data.columns:
                series = self.data[col].dropna()
                total = len(series)
                
                if total > 0:
                    dist_dict = {}
                    
                    # 各評価値の件数と割合
                    for value in [1, 2, 3, 4, 5]:
                        count = int((series == value).sum())
                        percentage = (count / total) * 100
                        dist_dict[str(value)] = {
                            'count': count,
                            'percentage': float(percentage)
                        }
                    
                    # 満足以上（4-5点）
                    satisfied_count = int((series >= 4).sum())
                    dist_dict['satisfied'] = {
                        'count': satisfied_count,
                        'percentage': float((satisfied_count / total) * 100)
                    }
                    
                    # 不満以下（1-2点）
                    dissatisfied_count = int((series <= 2).sum())
                    dist_dict['dissatisfied'] = {
                        'count': dissatisfied_count,
                        'percentage': float((dissatisfied_count / total) * 100)
                    }
                    
                    distribution[col] = dist_dict
        
        return distribution
    
    def calculate_confidence_intervals(self, 
                                      columns: List[str] = None,
                                      confidence_level: float = 0.95) -> Dict[str, Dict]:
        """
        信頼区間の計算
        
        計算式:
        信頼区間下限 = 平均値 - Z × 標準誤差
        信頼区間上限 = 平均値 + Z × 標準誤差
        標準誤差 = 標準偏差 ÷ √n
        
        Args:
            columns: 対象カラムのリスト（Noneの場合は満足度項目全て）
            confidence_level: 信頼水準（デフォルト95%）
        
        Returns:
            各項目の信頼区間情報
        """
        if columns is None:
            columns = self.satisfaction_columns
        
        # Z値の取得
        alpha = 1 - confidence_level
        z_value = stats.norm.ppf(1 - alpha/2)
        
        confidence_intervals = {}
        
        for col in columns:
            if col in self.data.columns:
                series = self.data[col].dropna()
                
                if len(series) > 0:
                    mean = series.mean()
                    std = series.std()
                    n = len(series)
                    
                    # 標準誤差
                    standard_error = std / np.sqrt(n)
                    
                    # 誤差範囲
                    margin_of_error = z_value * standard_error
                    
                    # 信頼区間
                    ci_lower = mean - margin_of_error
                    ci_upper = mean + margin_of_error
                    
                    confidence_intervals[col] = {
                        'mean': float(mean),
                        'std': float(std),
                        'n': int(n),
                        'confidence_level': confidence_level,
                        'standard_error': float(standard_error),
                        'margin_of_error': float(margin_of_error),
                        'ci_lower': float(ci_lower),
                        'ci_upper': float(ci_upper)
                    }
        
        return confidence_intervals
    
    # ==========================================
    # 2. 総合満足度の算出
    # ==========================================
    
    def calculate_overall_satisfaction_direct(self) -> Dict[str, float]:
        """
        直接測定法による総合満足度
        
        方法:
        アンケートの「総合満足度」項目をそのまま使用
        
        Returns:
            総合満足度の統計量
        """
        if 'overall_satisfaction' not in self.data.columns:
            return {}
        
        series = self.data['overall_satisfaction'].dropna()
        
        if len(series) == 0:
            return {}
        
        return {
            'value': float(series.mean()),
            'std': float(series.std()),
            'n': int(len(series)),
            'method': '直接測定法',
            'description': 'アンケート項目「総合満足度」の平均'
        }
    
    def calculate_overall_satisfaction_simple_average(self,
                                                      items: List[str] = None) -> Dict[str, float]:
        """
        単純平均法による総合満足度
        
        計算式:
        総合満足度 = Σ(各項目の満足度) ÷ 項目数
        
        Args:
            items: 満足度項目のリスト（Noneの場合は総合満足度以外の全項目）
        
        Returns:
            総合満足度の統計量
        """
        if items is None:
            # 総合満足度以外の満足度項目
            items = [col for col in self.satisfaction_columns 
                    if col != 'overall_satisfaction' and col in self.data.columns]
        
        if not items:
            return {}
        
        # 各行の平均を計算（欠損値は無視）
        means = self.data[items].mean(axis=1)
        valid_means = means.dropna()
        
        if len(valid_means) == 0:
            return {}
        
        return {
            'value': float(valid_means.mean()),
            'std': float(valid_means.std()),
            'n': int(len(valid_means)),
            'method': '単純平均法',
            'description': f'{len(items)}項目の満足度の単純平均'
        }
    
    def calculate_overall_satisfaction_weighted(self,
                                               satisfaction_items: List[str] = None,
                                               importance_items: List[str] = None) -> Dict[str, float]:
        """
        重要度加重平均法による総合満足度
        
        計算式:
        総合満足度 = Σ(各項目の満足度 × 重要度) ÷ Σ(重要度)
        
        Args:
            satisfaction_items: 満足度項目のリスト
            importance_items: 対応する重要度項目のリスト
        
        Returns:
            総合満足度の統計量
        """
        if satisfaction_items is None or importance_items is None:
            # デフォルトはIPA分析用のペアを使用
            satisfaction_items = list(self.ipa_pairs.keys())
            importance_items = list(self.ipa_pairs.values())
        
        # 両方のリストが同じ長さか確認
        if len(satisfaction_items) != len(importance_items):
            return {}
        
        weighted_values = []
        
        for i in range(len(self.data)):
            numerator = 0
            denominator = 0
            
            for sat_col, imp_col in zip(satisfaction_items, importance_items):
                if sat_col in self.data.columns and imp_col in self.data.columns:
                    sat_val = self.data[sat_col].iloc[i]
                    imp_val = self.data[imp_col].iloc[i]
                    
                    if pd.notna(sat_val) and pd.notna(imp_val):
                        numerator += sat_val * imp_val
                        denominator += imp_val
            
            if denominator > 0:
                weighted_values.append(numerator / denominator)
        
        if not weighted_values:
            return {}
        
        weighted_series = pd.Series(weighted_values)
        
        return {
            'value': float(weighted_series.mean()),
            'std': float(weighted_series.std()),
            'n': int(len(weighted_series)),
            'method': '重要度加重平均法',
            'description': '重要度で重み付けした平均'
        }
    
    # ==========================================
    # 3. 相関分析
    # ==========================================
    
    def calculate_correlations(self,
                               target_column: str,
                               analysis_columns: List[str] = None) -> Dict[str, Dict]:
        """
        相関分析（ピアソン相関係数）
        
        分析内容:
        - 総合満足度と各項目の相関
        - 重要度と満足度の相関
        - 利用頻度と満足度の相関
        
        Args:
            target_column: 目的変数（例: 総合満足度）
            analysis_columns: 説明変数のリスト
        
        Returns:
            相関係数と有意確率（p値）
        """
        if target_column not in self.data.columns:
            return {}
        
        if analysis_columns is None:
            # デフォルトは総合満足度以外の満足度項目
            analysis_columns = [col for col in self.satisfaction_columns 
                              if col != target_column and col in self.data.columns]
        
        correlations = {}
        
        for col in analysis_columns:
            if col in self.data.columns:
                # 両方のカラムから欠損値を除外
                valid_data = self.data[[target_column, col]].dropna()
                
                if len(valid_data) > 2:  # 相関計算には最低3つのデータポイントが必要
                    r, p_value = stats.pearsonr(
                        valid_data[target_column], 
                        valid_data[col]
                    )
                    
                    correlations[col] = {
                        'correlation': float(r),
                        'p_value': float(p_value),
                        'n': int(len(valid_data)),
                        'significant': p_value < 0.05
                    }
        
        return correlations
    
    def calculate_correlation_matrix(self,
                                    columns: List[str] = None) -> pd.DataFrame:
        """
        相関行列の計算
        
        Args:
            columns: 分析対象カラムのリスト
        
        Returns:
            相関行列（DataFrame）
        """
        if columns is None:
            columns = self.satisfaction_columns
        
        # 存在するカラムのみ抽出
        valid_columns = [col for col in columns if col in self.data.columns]
        
        if not valid_columns:
            return pd.DataFrame()
        
        # 相関行列を計算
        correlation_matrix = self.data[valid_columns].corr()
        
        return correlation_matrix
    
    # ==========================================
    # 4. 属性別分析
    # ==========================================
    
    def analyze_by_attribute(self,
                            satisfaction_column: str,
                            attribute_column: str) -> Dict[str, Any]:
        """
        属性別満足度の分析
        
        分析内容:
        - 各属性グループの記述統計
        - グループ間の平均値比較
        - 箱ひげ図用の生データ
        
        Args:
            satisfaction_column: 満足度カラム
            attribute_column: 属性カラム（部署、職位など）
        
        Returns:
            属性別統計量
        """
        if satisfaction_column not in self.data.columns or \
           attribute_column not in self.data.columns:
            return {}
        
        # 属性値でグループ化
        grouped = self.data.groupby(attribute_column)[satisfaction_column]
        
        attribute_stats = {}
        raw_data = {}  # 箱ひげ図用の生データ
        
        for group_name, group_data in grouped:
            valid_data = group_data.dropna()
            
            if len(valid_data) > 0:
                mean = valid_data.mean()
                std = valid_data.std()
                n = len(valid_data)
                
                # 95%信頼区間の計算
                if n > 1:
                    se = std / np.sqrt(n)
                    ci_margin = 1.96 * se
                    ci_lower = mean - ci_margin
                    ci_upper = mean + ci_margin
                else:
                    ci_lower = None
                    ci_upper = None
                
                attribute_stats[str(group_name)] = {
                    'mean': float(mean),
                    'std': float(std) if pd.notna(std) else 0.0,
                    'n': int(n),
                    'ci_lower': float(ci_lower) if ci_lower is not None else None,
                    'ci_upper': float(ci_upper) if ci_upper is not None else None
                }
                
                # 生データを保存（箱ひげ図用）
                raw_data[str(group_name)] = valid_data.tolist()
        
        # 最高値と最低値のグループを特定
        if attribute_stats:
            means = {k: v['mean'] for k, v in attribute_stats.items()}
            max_group = max(means, key=means.get)
            min_group = min(means, key=means.get)
            
            result = {
                'groups': attribute_stats,
                'raw_data': raw_data,  # 生データを追加
                'summary': {
                    'highest_group': max_group,
                    'highest_mean': means[max_group],
                    'lowest_group': min_group,
                    'lowest_mean': means[min_group],
                    'difference': means[max_group] - means[min_group]
                }
            }
            
            return result
        
        return {}
    
    # ==========================================
    # 5. IPA分析（重要度・満足度分析）
    # ==========================================
    
    def perform_ipa_analysis(self,
                            satisfaction_items: List[str] = None,
                            importance_items: List[str] = None,
                            use_rescaled: bool = False) -> Dict[str, Any]:
        """
        IPA分析の実行（標準化前または標準化後データ）
        
        分析手順:
        1. 各項目の満足度・重要度の平均を算出
        2. 中央値（または平均値）で4象限に分割
        3. 各項目を象限に分類
        
        象限の定義:
        - 第Ⅰ象限（右上）: 重要度高・満足度高 → 維持エリア
        - 第Ⅱ象限（左上）: 重要度高・満足度低 → 最優先改善エリア
        - 第Ⅲ象限（左下）: 重要度低・満足度低 → 改善検討エリア
        - 第Ⅳ象限（右下）: 重要度低・満足度高 → 過剰品質エリア
        
        Args:
            satisfaction_items: 満足度項目のリスト
            importance_items: 対応する重要度項目のリスト
            use_rescaled: 標準化後データを使用するか
        
        Returns:
            IPA分析結果（象限分類、改善優先順位）
        """
        if satisfaction_items is None or importance_items is None:
            # use_rescaledに応じてデフォルトを選択
            if use_rescaled:
                satisfaction_items = list(self.ipa_pairs_rescaled.keys())
                importance_items = list(self.ipa_pairs_rescaled.values())
            else:
                satisfaction_items = list(self.ipa_pairs.keys())
                importance_items = list(self.ipa_pairs.values())
        
        # 各項目の平均を計算
        item_scores = {}
        
        for sat_col, imp_col in zip(satisfaction_items, importance_items):
            if sat_col in self.data.columns and imp_col in self.data.columns:
                sat_mean = self.data[sat_col].mean()
                imp_mean = self.data[imp_col].mean()
                
                if pd.notna(sat_mean) and pd.notna(imp_mean):
                    item_scores[sat_col] = {
                        'satisfaction': float(sat_mean),
                        'importance': float(imp_mean)
                    }
        
        if not item_scores:
            return {}
        
        # 中央値を計算
        satisfaction_values = [v['satisfaction'] for v in item_scores.values()]
        importance_values = [v['importance'] for v in item_scores.values()]
        
        satisfaction_median = float(np.median(satisfaction_values))
        importance_median = float(np.median(importance_values))
        
        # 各項目を象限に分類
        items_analysis = {}
        quadrant_summary = {
            'Ⅰ': [],
            'Ⅱ': [],
            'Ⅲ': [],
            'Ⅳ': []
        }
        
        priority_items = []  # 最優先改善項目（第Ⅱ象限）
        
        for item, scores in item_scores.items():
            satisfaction = scores['satisfaction']
            importance = scores['importance']
            gap = importance - satisfaction
            
            # 象限分類
            quadrant = self.classify_ipa_quadrant(
                satisfaction, importance,
                satisfaction_median, importance_median
            )
            
            quadrant_names = {
                'Ⅰ': '維持エリア',
                'Ⅱ': '最優先改善エリア',
                'Ⅲ': '改善検討エリア',
                'Ⅳ': '過剰品質エリア'
            }
            
            items_analysis[item] = {
                'satisfaction': satisfaction,
                'importance': importance,
                'gap': float(gap),
                'quadrant': quadrant,
                'quadrant_name': quadrant_names[quadrant],
                'priority': None
            }
            
            quadrant_summary[quadrant].append(item)
            
            # 第Ⅱ象限の項目は優先順位を設定（ギャップが大きい順）
            if quadrant == 'Ⅱ':
                priority_items.append((item, gap))
        
        # 優先順位を設定
        priority_items.sort(key=lambda x: x[1], reverse=True)
        for i, (item, _) in enumerate(priority_items, 1):
            items_analysis[item]['priority'] = i
        
        ipa_results = {
            'settings': {
                'satisfaction_median': satisfaction_median,
                'importance_median': importance_median,
                'split_method': 'median'
            },
            'items': items_analysis,
            'summary': quadrant_summary
        }
        
        return ipa_results
    
    def classify_ipa_quadrant(self,
                             satisfaction: float,
                             importance: float,
                             satisfaction_median: float,
                             importance_median: float) -> str:
        """
        IPA象限の分類
        
        Args:
            satisfaction: 満足度スコア
            importance: 重要度スコア
            satisfaction_median: 満足度の中央値
            importance_median: 重要度の中央値
        
        Returns:
            象限名（'Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ'）
        """
        if importance >= importance_median and satisfaction >= satisfaction_median:
            return 'Ⅰ'  # 維持エリア
        elif importance >= importance_median and satisfaction < satisfaction_median:
            return 'Ⅱ'  # 最優先改善エリア
        elif importance < importance_median and satisfaction < satisfaction_median:
            return 'Ⅲ'  # 改善検討エリア
        else:
            return 'Ⅳ'  # 過剰品質エリア
    
    # ==========================================
    # 6. 分析パイプライン
    # ==========================================
    
    def analysis_pipeline(self) -> Dict[str, Any]:
        """
        分析パイプラインの実行（標準化前と標準化後の両方）
        
        実行順序:
        1. 基本分析（記述統計、分布）- 標準化前と標準化後
        2. 信頼区間の計算 - 標準化前と標準化後
        3. 総合満足度の算出（3手法）
        4. 相関分析 - 標準化前と標準化後
        5. 属性別分析
        6. IPA分析 - 標準化前と標準化後
        
        Returns:
            全分析結果を含む辞書
        """
        print("\n分析パイプライン開始...")
        
        results = {}
        
        # 1. 基本分析（標準化前と標準化後を含む）
        print("  1/7 基本分析（記述統計・分布）...")
        results['basic_statistics'] = {
            'descriptive_stats': self.calculate_descriptive_statistics(),
            'satisfaction_distribution': self.calculate_satisfaction_distribution(),
        }
        
        # 2. 信頼区間（標準化前）
        print("  2/7 信頼区間の計算（標準化前）...")
        results['basic_statistics']['confidence_intervals'] = {
            'original': self.calculate_confidence_intervals(),
        }
        
        # 信頼区間（標準化後）
        print("  2.5/7 信頼区間の計算（標準化後）...")
        rescaled_columns = [col for col in self.satisfaction_columns_rescaled if col in self.data.columns]
        if rescaled_columns:
            results['basic_statistics']['confidence_intervals']['rescaled'] = \
                self.calculate_confidence_intervals(columns=rescaled_columns)
        
        # 3. 総合満足度
        print("  3/7 総合満足度の算出（3手法）...")
        results['overall_satisfaction'] = {
            'direct': self.calculate_overall_satisfaction_direct(),
            'simple_average': self.calculate_overall_satisfaction_simple_average(),
            'weighted_average': self.calculate_overall_satisfaction_weighted()
        }
        
        # 推奨手法を設定
        results['overall_satisfaction']['recommended'] = 'direct'
        
        # 4. 相関分析（標準化前）
        print("  4/7 相関分析（標準化前）...")
        results['correlation_analysis'] = {
            'original': {},
            'rescaled': {}
        }
        
        if 'overall_satisfaction' in self.data.columns:
            results['correlation_analysis']['original']['with_overall_satisfaction'] = \
                self.calculate_correlations('overall_satisfaction')
        
        # 相関行列（標準化前）
        correlation_matrix = self.calculate_correlation_matrix()
        if not correlation_matrix.empty:
            results['correlation_analysis']['original']['correlation_matrix'] = \
                correlation_matrix.to_dict()
        
        # 相関分析（標準化後）
        print("  4.5/7 相関分析（標準化後）...")
        if 'overall_satisfaction_rescaled' in self.data.columns:
            results['correlation_analysis']['rescaled']['with_overall_satisfaction'] = \
                self.calculate_correlations('overall_satisfaction_rescaled')
        
        # 相関行列（標準化後）- 標準化後のカラムのみで計算
        rescaled_numeric_cols = [col for col in self.satisfaction_columns_rescaled + self.importance_columns_rescaled 
                                if col in self.data.columns]
        if len(rescaled_numeric_cols) > 1:
            rescaled_corr_matrix = self.data[rescaled_numeric_cols].corr()
            results['correlation_analysis']['rescaled']['correlation_matrix'] = \
                rescaled_corr_matrix.to_dict()
        
        # 5. 属性別分析（標準化前と標準化後）
        print("  5/7 属性別分析（標準化前と標準化後）...")
        results['attribute_analysis'] = {
            'original': {},
            'rescaled': {}
        }
        
        # 標準化前データでの属性別分析
        if 'overall_satisfaction' in self.data.columns:
            for attr in self.attribute_columns:
                if attr in self.data.columns:
                    results['attribute_analysis']['original'][f'by_{attr}'] = \
                        self.analyze_by_attribute('overall_satisfaction', attr)
        
        # 標準化後データでの属性別分析
        if 'overall_satisfaction_rescaled' in self.data.columns:
            for attr in self.attribute_columns:
                if attr in self.data.columns:
                    results['attribute_analysis']['rescaled'][f'by_{attr}'] = \
                        self.analyze_by_attribute('overall_satisfaction_rescaled', attr)
        
        # 6. IPA分析（標準化前）
        print("  6/7 IPA分析（標準化前）...")
        results['ipa_analysis'] = {
            'original': self.perform_ipa_analysis(use_rescaled=False)
        }
        
        # IPA分析（標準化後）
        print("  7/7 IPA分析（標準化後）...")
        results['ipa_analysis']['rescaled'] = self.perform_ipa_analysis(use_rescaled=True)
        
        print("分析パイプライン完了！")
        
        self.analysis_results = results
        return results
        
        print("分析パイプライン完了！")
        
        self.analysis_results = results
        return results
    
    def _convert_to_json_serializable(self, obj):
        """
        オブジェクトをJSON シリアライズ可能な形式に変換
        
        Args:
            obj: 変換対象のオブジェクト
        
        Returns:
            JSON シリアライズ可能なオブジェクト
        """
        if isinstance(obj, dict):
            return {k: self._convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    def save_analysis_results(self, output_path: str) -> None:
        """
        分析結果の保存
        
        Args:
            output_path: 出力先パス（JSON形式）
        """
        # ディレクトリが存在しない場合は作成
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON シリアライズ可能な形式に変換
        serializable_results = self._convert_to_json_serializable(self.analysis_results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n分析結果を保存しました: {output_path}")


if __name__ == "__main__":
    # 使用例
    analyser = SurveyDataAnalyser(
        config_file='config/survey_questions.yaml',
        main_config_file='config/config.yaml'
    )
    
    # データ読み込み
    analyser.load_data('csv/survey_preprocessed_data.csv')
    
    # 分析パイプライン実行
    results = analyser.analysis_pipeline()
    
    # 結果保存
    analyser.save_analysis_results('out/analysis_results.json')
    
    print("分析完了")