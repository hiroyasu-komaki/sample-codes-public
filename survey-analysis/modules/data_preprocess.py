"""
データ前処理モジュール（代表性検証機能追加版）
アンケートデータの包括的な前処理を実施
"""

import sys
import os
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class DataPreprocessor:
    """アンケートデータの前処理クラス"""
    
    def __init__(self, config_file: str = 'config/survey_questions.yaml',
                 main_config_file: str = 'config/config.yaml'):
        """
        初期化
        
        Args:
            config_file: アンケート項目定義ファイルのパス
            main_config_file: メイン設定ファイルのパス（母集団情報を含む）
        """
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # メイン設定ファイルの読み込み（母集団情報用）
        self.main_config = None
        if os.path.exists(main_config_file):
            with open(main_config_file, 'r', encoding='utf-8') as f:
                self.main_config = yaml.safe_load(f)
        
        self.raw_data = None
        self.processed_data = None
        self.preprocessing_report = {
            'data_types': {},
            'outliers': {},
            'encoding': {},
            'standardization': {},
            'missing_values': {},
            'quality_metrics': {},
            'representativeness': {}  # 代表性検証結果を追加
        }
    
    def check_representativeness(self, 
                                 population_dist: Dict[str, Dict[str, float]] = None) -> Dict[str, Any]:
        """
        回答者の代表性を検証
        
        Args:
            population_dist: 母集団の属性分布（Noneの場合はconfig.yamlから取得）
                例: {
                    'department': {'営業部': 0.30, '製造部': 0.40, ...},
                    'position': {'一般職': 0.85, '管理職': 0.15}
                }
        
        Returns:
            各属性の乖離度と判定結果
        """
        # 母集団分布の取得
        if population_dist is None:
            if self.main_config and 'population_distribution' in self.main_config:
                population_dist = self.main_config['population_distribution']
            else:
                print("警告: 母集団分布が設定されていません。代表性検証をスキップします。")
                return {}
        
        # 判定基準の取得
        thresholds = {
            'good': 5.0,
            'acceptable': 10.0
        }
        if self.main_config and 'representativeness_check' in self.main_config:
            config_thresholds = self.main_config['representativeness_check'].get('thresholds', {})
            thresholds.update(config_thresholds)
        
        representativeness_report = {}
        
        for attr, expected_dist in population_dist.items():
            if attr not in self.processed_data.columns:
                continue
            
            # 実際の分布を計算
            actual_counts = self.processed_data[attr].value_counts()
            total = len(self.processed_data)
            actual_dist_calculated = (actual_counts / total).to_dict()
            
            # 乖離度を計算
            deviations = {}
            for category, expected_ratio in expected_dist.items():
                actual_ratio = actual_dist_calculated.get(category, 0.0)
                deviation = (actual_ratio - expected_ratio) * 100  # パーセント表示
                
                deviations[category] = {
                    'expected_pct': expected_ratio * 100,
                    'actual_pct': actual_ratio * 100,
                    'deviation_pct': deviation,
                    'actual_count': int(actual_counts.get(category, 0))
                }
            
            # 最大乖離度で判定
            max_deviation = max(abs(d['deviation_pct']) for d in deviations.values())
            
            if max_deviation <= thresholds['good']:
                status = '良好'
                status_en = 'good'
            elif max_deviation <= thresholds['acceptable']:
                status = '許容範囲'
                status_en = 'acceptable'
            else:
                status = '要調整'
                status_en = 'needs_adjustment'
            
            representativeness_report[attr] = {
                'deviations': deviations,
                'max_deviation': max_deviation,
                'status': status,
                'status_en': status_en,
                'total_responses': total
            }
        
        # レポートに保存
        self.preprocessing_report['representativeness'] = representativeness_report
        
        return representativeness_report
    
    def load_data(self, filepath: str) -> pd.DataFrame:
        """
        データの読み込み
        
        Args:
            filepath: CSVファイルのパス
            
        Returns:
            読み込んだDataFrame
        """
        self.raw_data = pd.read_csv(filepath)
        self.processed_data = self.raw_data.copy()
        
        return self.raw_data
    
    def identify_data_types(self) -> Dict[str, List[str]]:
        """
        データ型の識別
        
        Returns:
            データ型別のカラムリスト
        """
        data_types = {
            'identifier': [],
            'numeric_continuous': [],
            'categorical_ordinal': [],
            'categorical_nominal': [],
            'multiple_choice': []
        }
        
        # 各セクションから情報を取得
        all_configs = {}
        
        # respondent_attributes
        if 'respondent_attributes' in self.config:
            for col, config in self.config['respondent_attributes'].items():
                if col in self.processed_data.columns:
                    all_configs[col] = config
        
        # service_usage
        if 'service_usage' in self.config:
            for col, config in self.config['service_usage'].items():
                if col in self.processed_data.columns:
                    all_configs[col] = config
        
        # satisfaction_ratings
        if 'satisfaction_ratings' in self.config:
            for col, config in self.config['satisfaction_ratings'].items():
                if col in self.processed_data.columns:
                    all_configs[col] = config
        
        # importance_ratings
        if 'importance_ratings' in self.config:
            for col, config in self.config['importance_ratings'].items():
                if col in self.processed_data.columns:
                    all_configs[col] = config
        
        # improvement_requests
        if 'improvement_requests' in self.config:
            for col, config in self.config['improvement_requests'].items():
                if col in self.processed_data.columns:
                    all_configs[col] = config
        
        # データ型を識別
        for col, config in all_configs.items():
            dtype = config.get('data_type', 'unknown')
            if dtype in data_types:
                data_types[dtype].append(col)
        
        self.preprocessing_report['data_types'] = data_types
        
        return data_types
    
    def detect_outliers(self, columns: List[str], method: str = 'iqr', 
                       threshold: float = 1.5) -> Dict[str, Dict]:
        """
        外れ値の検出
        
        Args:
            columns: 対象カラムのリスト
            method: 検出方法 ('iqr' or 'zscore')
            threshold: 閾値（IQRの場合は倍率、Z-scoreの場合は標準偏差数）
            
        Returns:
            外れ値情報
        """
        outlier_info = {}
        
        for col in columns:
            if col not in self.processed_data.columns:
                continue
            
            data = self.processed_data[col].dropna()
            
            if len(data) == 0:
                continue
            
            if method == 'iqr':
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outliers = data[(data < lower_bound) | (data > upper_bound)]
                
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(data))
                outliers = data[z_scores > threshold]
            
            else:
                outliers = pd.Series([])
            
            if len(outliers) > 0:
                outlier_info[col] = {
                    'count': len(outliers),
                    'percentage': len(outliers) / len(data) * 100,
                    'values': outliers.tolist()
                }
            else:
                outlier_info[col] = {'count': 0, 'percentage': 0.0}
        
        self.preprocessing_report['outliers'] = outlier_info
        return outlier_info
    
    def handle_outliers(self, columns: List[str], method: str = 'cap'):
        """
        外れ値の処理
        
        Args:
            columns: 対象カラム
            method: 処理方法 ('cap', 'remove', 'keep')
        """
        if method == 'keep':
            return
        
        for col in columns:
            if col not in self.processed_data.columns:
                continue
            
            data = self.processed_data[col].dropna()
            
            if len(data) == 0:
                continue
            
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            if method == 'cap':
                # 上限・下限でキャッピング
                self.processed_data[col] = self.processed_data[col].clip(
                    lower=lower_bound, upper=upper_bound
                )
            elif method == 'remove':
                # 外れ値を持つ行を削除
                mask = (self.processed_data[col] >= lower_bound) & \
                       (self.processed_data[col] <= upper_bound)
                self.processed_data = self.processed_data[mask]
    
    def encode_ordinal_variables(self, columns: List[str]) -> Dict[str, Dict]:
        """
        順序カテゴリカル変数のエンコーディング
        
        Args:
            columns: 対象カラム
            
        Returns:
            エンコーディング情報
        """
        encoding_info = {}
        
        for col in columns:
            if col not in self.processed_data.columns:
                continue
            
            # 設定からエンコーディング順序を取得
            config = self._get_column_config(col)
            if not config or 'encoding' not in config:
                continue
            
            encoding = config['encoding']
            if encoding.get('method') == 'ordinal' and 'order' in encoding:
                order_map = encoding['order']
                
                # エンコーディング実行
                self.processed_data[f'{col}_encoded'] = \
                    self.processed_data[col].map(order_map)
                
                encoding_info[col] = {
                    'method': 'ordinal',
                    'mapping': order_map,
                    'encoded_column': f'{col}_encoded'
                }
                
        
        self.preprocessing_report['encoding'].update(encoding_info)
        return encoding_info
    
    def encode_nominal_variables(self, columns: List[str]) -> Dict[str, Dict]:
        """
        名義カテゴリカル変数のOne-hotエンコーディング
        
        Args:
            columns: 対象カラム
            
        Returns:
            エンコーディング情報
        """
        
        encoding_info = {}
        
        for col in columns:
            if col not in self.processed_data.columns:
                continue
            
            # 設定から情報を取得
            config = self._get_column_config(col)
            if not config or 'encoding' not in config:
                continue
            
            encoding = config['encoding']
            prefix = encoding.get('prefix', col)
            
            # One-hotエンコーディング実行
            dummies = pd.get_dummies(
                self.processed_data[col], 
                prefix=prefix,
                drop_first=False  # 全てのカテゴリを保持
            )
            
            # データに追加
            self.processed_data = pd.concat([self.processed_data, dummies], axis=1)
            
            encoding_info[col] = {
                'method': 'one_hot',
                'prefix': prefix,
                'new_columns': dummies.columns.tolist()
            }
        
        self.preprocessing_report['encoding'].update(encoding_info)
        return encoding_info
    
    def expand_multiple_choice(self, columns: List[str]) -> Dict[str, Dict]:
        """
        複数選択データの二値展開
        
        Args:
            columns: 対象カラム
            
        Returns:
            展開情報
        """
        
        expansion_info = {}
        
        for col in columns:
            if col not in self.processed_data.columns:
                continue
            
            # 設定から情報を取得
            config = self._get_column_config(col)
            if not config:
                continue
            
            options = config.get('options', [])
            encoding = config.get('encoding', {})
            prefix = encoding.get('prefix', col)
            separator = encoding.get('separator', ',')
            
            # 各オプションに対して二値変数を作成
            for option in options:
                col_name = f"{prefix}_{option}"
                # カンマ区切りの文字列に含まれるかチェック
                self.processed_data[col_name] = \
                    self.processed_data[col].apply(
                        lambda x: 1 if isinstance(x, str) and option in x.split(separator) else 0
                    )
            
            new_columns = [f"{prefix}_{opt}" for opt in options]
            expansion_info[col] = {
                'method': 'multi_hot',
                'prefix': prefix,
                'options': options,
                'new_columns': new_columns
            }
        
        self.preprocessing_report['encoding'].update(expansion_info)
        return expansion_info
    
    def handle_missing_values(self, numeric_cols: List[str], 
                             strategy: str = 'auto') -> Dict[str, Any]:
        """
        欠損値の処理
        
        Args:
            numeric_cols: 数値カラムのリスト
            strategy: 処理戦略 ('auto', 'mean', 'median', 'drop')
            
        Returns:
            欠損値処理情報
        """
        
        missing_info = {}
        
        for col in numeric_cols:
            if col not in self.processed_data.columns:
                continue
            
            missing_count = self.processed_data[col].isna().sum()
            total_count = len(self.processed_data)
            missing_rate = missing_count / total_count * 100
            
            if missing_count == 0:
                missing_info[col] = {
                    'count': 0,
                    'rate': 0.0,
                    'action': 'none'
                }
                continue
            
            # 設定から処理方法を取得
            config = self._get_column_config(col)
            handling_method = 'drop'  # デフォルト
            
            if config and 'preprocessing' in config:
                handling_method = config['preprocessing'].get(
                    'missing_handling', 'listwise_deletion'
                )
            
            # 自動戦略の場合、欠損率に基づいて決定
            if strategy == 'auto':
                if missing_rate < 5.0:
                    action = 'drop'
                elif 5.0 <= missing_rate <= 15.0:
                    action = 'mean'
                else:
                    action = 'keep'
            else:
                action = strategy
            
            # 欠損値処理の実行
            if action == 'drop':
                self.processed_data = self.processed_data.dropna(subset=[col])
                action_taken = 'リストワイズ削除'
            elif action == 'mean':
                mean_value = self.processed_data[col].mean()
                self.processed_data[col].fillna(mean_value, inplace=True)
                action_taken = f'平均値補完 ({mean_value:.2f})'
            elif action == 'median':
                median_value = self.processed_data[col].median()
                self.processed_data[col].fillna(median_value, inplace=True)
                action_taken = f'中央値補完 ({median_value:.2f})'
            else:
                action_taken = '処理なし'
            
            missing_info[col] = {
                'count': missing_count,
                'rate': missing_rate,
                'action': action_taken
            }
            
        
        self.preprocessing_report['missing_values'] = missing_info
        return missing_info
    
    def standardize_numeric(self, columns: List[str], 
                           method: str = 'z_score') -> Dict[str, Dict]:
        """
        数値データの標準化
        
        Args:
            columns: 対象カラム
            method: 標準化方法 ('z_score', 'min_max', 'robust')
            
        Returns:
            標準化情報
        """
        
        standardization_info = {}
        
        for col in columns:
            if col not in self.processed_data.columns:
                continue
            
            data = self.processed_data[col].dropna()
            
            if len(data) == 0:
                continue
            
            if method == 'z_score':
                # Z-score標準化
                mean = data.mean()
                std = data.std()
                self.processed_data[f'{col}_std'] = \
                    (self.processed_data[col] - mean) / std
                
                # リスケーリング: 標準化後のデータを元の範囲に変換
                # ただし、標準偏差=1を保持する
                config = self._get_column_config(col)
                if config and 'scale' in config:
                    original_min = 1
                    original_max = config['scale']
                else:
                    # フォールバック: データから推定
                    original_min = self.processed_data[col].min()
                    original_max = self.processed_data[col].max()
                
                # 目標の中心値と標準偏差
                target_center = (original_max + original_min) / 2  # 例: (5+1)/2 = 3.0
                target_std = 1.0  # 標準偏差は1に保つ
                
                # リスケール: 標準化値 × 目標標準偏差 + 目標中心値
                std_col = f'{col}_std'
                self.processed_data[f'{col}_rescaled'] = \
                    self.processed_data[std_col] * target_std + target_center
                
                standardization_info[col] = {
                    'method': 'z_score',
                    'mean': mean,
                    'std': std,
                    'original_range': (original_min, original_max),
                    'target_center': target_center,
                    'target_std': target_std,
                    'standardized_column': f'{col}_std',
                    'rescaled_column': f'{col}_rescaled'
                }
                
                
            elif method == 'min_max':
                # Min-Max正規化
                min_val = data.min()
                max_val = data.max()
                self.processed_data[f'{col}_norm'] = \
                    (self.processed_data[col] - min_val) / (max_val - min_val)
                
                standardization_info[col] = {
                    'method': 'min_max',
                    'min': min_val,
                    'max': max_val,
                    'normalized_column': f'{col}_norm'
                }
                
                
            elif method == 'robust':
                # Robust標準化（中央値とIQRを使用）
                median = data.median()
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                self.processed_data[f'{col}_robust'] = \
                    (self.processed_data[col] - median) / IQR
                
                standardization_info[col] = {
                    'method': 'robust',
                    'median': median,
                    'iqr': IQR,
                    'standardized_column': f'{col}_robust'
                }
                
        
        self.preprocessing_report['standardization'] = standardization_info
        return standardization_info
    
    def check_data_quality(self) -> Dict[str, Any]:
        """
        データ品質のチェック
        
        Returns:
            品質指標
        """
        
        quality_metrics = {}
        
        # 基本統計
        quality_metrics['shape'] = {
            'rows': self.processed_data.shape[0],
            'columns': self.processed_data.shape[1]
        }
        
        # 欠損値の総計
        total_missing = self.processed_data.isna().sum().sum()
        total_cells = self.processed_data.shape[0] * self.processed_data.shape[1]
        
        quality_metrics['missing'] = {
            'total_count': int(total_missing),
            'total_rate': total_missing / total_cells * 100
        }
        
        # データ型の分布
        quality_metrics['dtypes'] = self.processed_data.dtypes.value_counts().to_dict()
        
        self.preprocessing_report['quality_metrics'] = quality_metrics
        return quality_metrics
    
    def preprocess_pipeline(self, check_representativeness: bool = True) -> pd.DataFrame:
        """
        前処理パイプラインの実行
        
        Args:
            check_representativeness: 代表性検証を実行するかどうか
        
        Returns:
            前処理済みDataFrame
        """
        # 1. データ型の識別
        data_types = self.identify_data_types()
        
        # エンコーディング処理は削除（機械学習を行わないため）
        # 2. 複数選択データの展開 - 削除
        # 3. 順序カテゴリカルデータのエンコーディング - 削除
        # 4. 名義カテゴリカルデータのエンコーディング - 削除
        
        # 5. 外れ値検出
        if data_types['numeric_continuous']:
            self.detect_outliers(data_types['numeric_continuous'], method='iqr')
            # 外れ値は検出のみで処理はしない（保持）
            self.handle_outliers(data_types['numeric_continuous'], method='keep')
        
        # 6. 欠損値処理
        if data_types['numeric_continuous']:
            self.handle_missing_values(data_types['numeric_continuous'], strategy='auto')
        
        # 7. 数値データの標準化（リスケール項目を分析で使用）
        if data_types['numeric_continuous']:
            self.standardize_numeric(data_types['numeric_continuous'], method='z_score')
        
        # 8. データ品質チェック
        self.check_data_quality()
        
        # 9. 代表性検証（オプション）
        if check_representativeness:
            if self.main_config and 'representativeness_check' in self.main_config:
                if self.main_config['representativeness_check'].get('enabled', True):
                    self.check_representativeness()
        
        return self.processed_data
    
    def save_processed_data(self, output_path: str):
        """
        前処理済みデータの保存
        
        Args:
            output_path: 出力先パス
        """
        self.processed_data.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    def save_report(self, output_path: str):
        """
        前処理レポートの保存
        
        Args:
            output_path: 出力先パス
        """
        import json
        
        # NumPy型をJSON対応型に変換
        def convert_to_json_serializable(obj):
            if isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Series):
                return obj.tolist()
            elif isinstance(obj, dict):
                # dictのキーも変換
                return {str(k): convert_to_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_json_serializable(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif pd.api.types.is_extension_array_dtype(type(obj)):
                return str(obj)
            else:
                return obj
        
        serializable_report = convert_to_json_serializable(self.preprocessing_report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_report, f, ensure_ascii=False, indent=2)
    
    def _get_column_config(self, column_name: str) -> Dict:
        """
        カラムの設定情報を取得
        
        Args:
            column_name: カラム名
            
        Returns:
            設定情報
        """
        # 全セクションから検索
        for section_name in ['respondent_attributes', 'service_usage', 
                            'satisfaction_ratings', 'importance_ratings', 
                            'improvement_requests']:
            if section_name in self.config:
                section = self.config[section_name]
                if column_name in section:
                    return section[column_name]
        
        return {}
    
    def get_preprocessing_summary(self) -> str:
        """
        前処理サマリーの取得（簡潔版）
        
        Returns:
            サマリー文字列
        """
        lines = []
        lines.append("\n" + "-"*70)
        lines.append("前処理結果サマリー")
        lines.append("-"*70)
        
        # データサイズ
        if self.raw_data is not None and self.processed_data is not None:
            lines.append(f"データサイズ: {self.raw_data.shape[0]}行 → {self.processed_data.shape[0]}行")
            lines.append(f"カラム数: {self.raw_data.shape[1]}列 → {self.processed_data.shape[1]}列")
        
        # 標準化の効果
        if 'standardization' in self.preprocessing_report and self.preprocessing_report['standardization']:
            lines.append("\n標準化済み数値項目:")
            lines.append(f"{'項目':<35} {'元の平均':<12} {'元の標準偏差':<12} {'標準化後'}")
            lines.append("-" * 70)
            
            for col, info in self.preprocessing_report['standardization'].items():
                if info['method'] == 'z_score':
                    lines.append(
                        f"{col:<35} "
                        f"{info['mean']:>10.3f}   "
                        f"{info['std']:>10.3f}   "
                        f"平均=0, 標準偏差=1"
                    )
        
        # エンコーディング
        if 'encoding' in self.preprocessing_report and self.preprocessing_report['encoding']:
            encode_count = len(self.preprocessing_report['encoding'])
            lines.append(f"\nエンコーディング済み項目: {encode_count}個")
        
        # 欠損値処理
        if 'missing_values' in self.preprocessing_report and self.preprocessing_report['missing_values']:
            total_missing = sum(v['count'] for v in self.preprocessing_report['missing_values'].values() if isinstance(v, dict) and 'count' in v)
            lines.append(f"欠損値処理: {total_missing}個")
        
        lines.append("-" * 70)
        
        return "\n".join(lines)