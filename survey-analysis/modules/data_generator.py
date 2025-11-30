"""
サンプルデータ生成モジュール（簡易版）
アンケートデータのサンプルを生成
"""

import pandas as pd
import numpy as np
import yaml


class SurveyDataGenerator:
    """アンケートサンプルデータ生成クラス"""
    
    def __init__(self, config_file='survey_questions.yaml'):
        """
        初期化
        
        Args:
            config_file: 設定ファイルのパス
        """
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def generate_sample_data(self, n=100):
        """
        サンプルデータの生成
        
        Args:
            n: 生成するサンプル数
            
        Returns:
            DataFrame: 生成されたサンプルデータ
        """
        np.random.seed(42)
        
        data = {}
        
        # 回答者ID
        data['respondent_id'] = [f'R{i:04d}' for i in range(1, n+1)]
        
        # 回答者属性
        for attr_key, attr_config in self.config['respondent_attributes'].items():
            options = attr_config['options']
            data[attr_key] = np.random.choice(options, n)
        
        # サービス利用状況
        for usage_key, usage_config in self.config['service_usage'].items():
            if usage_config['type'] == 'single_choice':
                options = usage_config['options']
                data[usage_key] = np.random.choice(options, n)
            elif usage_config['type'] == 'multiple_choice':
                # 複数選択はカンマ区切りで保存
                options = usage_config['options']
                data[usage_key] = [
                    ','.join(np.random.choice(options, 
                             size=np.random.randint(1, min(4, len(options)+1)),
                             replace=False))
                    for _ in range(n)
                ]
        
        # 満足度評価（5段階、欠損値あり）
        for rating_key, rating_config in self.config['satisfaction_ratings'].items():
            # 項目ごとにランダムな平均値と標準偏差を生成
            # 平均値: 2.0〜4.0の範囲でランダム
            # 標準偏差: 0.7〜1.3の範囲でランダム
            mean_value = np.random.uniform(2.0, 4.0)
            std_value = np.random.uniform(0.7, 1.3)
            
            ratings = np.random.normal(mean_value, std_value, n)
            ratings = np.clip(ratings, 1, 5)
            ratings = np.round(ratings).astype(float)
            
            # ランダムに5%程度を欠損値に
            missing_mask = np.random.random(n) < 0.05
            ratings[missing_mask] = np.nan
            
            data[rating_key] = ratings
        
        # 重要度評価（4段階）
        for imp_key, imp_config in self.config['importance_ratings'].items():
            # 項目ごとにランダムな平均値と標準偏差を生成
            # 平均値: 2.0〜3.5の範囲でランダム（重要度は全体的に高めだが差をつける）
            # 標準偏差: 0.5〜1.0の範囲でランダム
            mean_value = np.random.uniform(2.0, 3.5)
            std_value = np.random.uniform(0.5, 1.0)
            
            importance = np.random.normal(mean_value, std_value, n)
            importance = np.clip(importance, 1, 4)
            importance = np.round(importance).astype(float)
            data[imp_key] = importance
        
        # 改善要望
        for req_key, req_config in self.config['improvement_requests'].items():
            if req_config['type'] == 'single_choice':
                options = req_config['options']
                data[req_key] = np.random.choice(options, n)
            elif req_config['type'] == 'multiple_choice':
                options = req_config['options']
                data[req_key] = [
                    ','.join(np.random.choice(options,
                             size=np.random.randint(1, min(3, len(options)+1)),
                             replace=False))
                    for _ in range(n)
                ]
        
        return pd.DataFrame(data)
    
    def save_to_csv(self, df, filename='survey_sample_data.csv'):
        """
        DataFrameをCSVに保存
        
        Args:
            df: 保存するDataFrame
            filename: 保存ファイル名
        """
        df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    def get_statistics(self, df):
        """
        統計情報の取得
        
        Args:
            df: 対象のDataFrame
            
        Returns:
            dict: 統計情報
        """
        stats = {
            'total_samples': len(df),
            'satisfaction_ratings': {},
            'importance_ratings': {}
        }
        
        # 満足度評価の統計（YAMLから動的に取得）
        if 'satisfaction_ratings' in self.config:
            for item in self.config['satisfaction_ratings'].keys():
                if item in df.columns:
                    valid_data = df[item].dropna()
                    stats['satisfaction_ratings'][item] = {
                        'mean': valid_data.mean(),
                        'std': valid_data.std(),
                        'missing': df[item].isna().sum()
                    }
        
        # 重要度評価の統計（YAMLから動的に取得）
        if 'importance_ratings' in self.config:
            for item in self.config['importance_ratings'].keys():
                if item in df.columns:
                    valid_data = df[item].dropna()
                    stats['importance_ratings'][item] = {
                        'mean': valid_data.mean(),
                        'std': valid_data.std(),
                        'missing': df[item].isna().sum()
                    }
        
        return stats