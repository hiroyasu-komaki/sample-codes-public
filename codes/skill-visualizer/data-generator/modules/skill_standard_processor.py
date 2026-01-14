"""
スキル標準プロセッサーモジュール
YAMLファイルからスキル標準データを処理してDataFrameを生成
"""

import os
import yaml
import pandas as pd
from pathlib import Path


class SkillStandardProcessor:
    """スキル標準データを処理するクラス"""
    
    def __init__(self, skills_yaml_path=None, master_yaml_path=None):
        """
        初期化
        
        Args:
            skills_yaml_path (str): スキルデータYAMLファイルのパス
            master_yaml_path (str): マスターデータYAMLファイルのパス
        """
        # スクリプトのディレクトリを取得（modulesディレクトリ）
        script_dir = Path(__file__).parent
        # プロジェクトルートディレクトリ（modulesの親ディレクトリ）
        project_root = script_dir.parent
        
        # デフォルトパスの設定
        if skills_yaml_path is None:
            skills_yaml_path = project_root / 'config' / 'skillstd.yaml'
        if master_yaml_path is None:
            master_yaml_path = project_root / 'config' / 'master_data.yaml'
        
        self.skills_yaml_path = str(skills_yaml_path)
        self.master_yaml_path = str(master_yaml_path)
        self.master_data = None
        self.skill_data = None
        
        # YAMLファイルの読み込み
        self._load_yaml_files()
    
    def _load_yaml_files(self):
        """YAMLファイルを読み込む"""
        try:
            # マスターデータの読み込み
            with open(self.master_yaml_path, 'r', encoding='utf-8') as file:
                self.master_data = yaml.safe_load(file)
            
            # スキルデータの読み込み
            with open(self.skills_yaml_path, 'r', encoding='utf-8') as file:
                self.skill_data = yaml.safe_load(file)
                
        except FileNotFoundError as e:
            raise FileNotFoundError(f"YAMLファイルが見つかりません: {e}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML解析エラー: {e}")
    
    def process_data(self):
        """
        スキルデータを処理してDataFrameを生成
        
        Returns:
            pd.DataFrame: 処理済みスキルデータ
        """
        # マスターデータの取得
        roles = self.master_data['roles']
        role_speciality_mapping = self.master_data['role_speciality_mapping']
        skill_level_mapping = self.master_data['skill_level_mapping']
        
        # データリスト
        data = []
        
        # スキルデータを展開
        for skill in self.skill_data['skills']:
            category = skill['category']
            subcategory = skill['subcategory']
            skill_name = skill['skill_name']
            levels = skill['levels']
            
            # 各ロールに対してレコードを作成
            for role in roles:
                skill_level = levels.get(role, 'd')  # デフォルトは'd'
                speciality = role_speciality_mapping.get(role, 'その他')
                skill_level_value = skill_level_mapping.get(skill_level, 1)
                
                data.append({
                    'カテゴリー': category,
                    'サブカテゴリー': subcategory,
                    'スキル項目': skill_name,
                    'ロール': role,
                    '専門性': speciality,
                    'スキルレベル': skill_level,
                    'スキルレベル_数値': skill_level_value
                })
        
        # DataFrameを作成
        df = pd.DataFrame(data)
        
        return df
    
    def get_data_summary(self):
        """
        データの概要情報を取得
        
        Returns:
            dict: データ概要情報
        """
        roles = self.master_data['roles']
        skills = self.skill_data['skills']
        specialities = list(set(self.master_data['role_speciality_mapping'].values()))
        
        return {
            'total_roles': len(roles),
            'total_skills': len(skills),
            'total_specialities': len(specialities),
            'expected_rows': len(roles) * len(skills),
            'roles': roles,
            'specialities': specialities
        }
    
    def validate_data(self, df):
        """
        生成されたデータの検証
        
        Args:
            df (pd.DataFrame): 検証するDataFrame
            
        Returns:
            bool: 検証結果（True: 正常, False: 異常）
        """
        try:
            # 必須カラムの存在チェック
            required_columns = [
                'カテゴリー', 'サブカテゴリー', 'スキル項目',
                'ロール', '専門性', 'スキルレベル', 'スキルレベル_数値'
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    print(f"❌ Error: Missing column {col}")
                    return False
            
            # NULL値のチェック
            if df.isnull().any().any():
                print("❌ Error: Found NULL values in data")
                return False
            
            # スキルレベルの値チェック
            valid_levels = set(self.master_data['skill_level_mapping'].keys())
            if not set(df['スキルレベル'].unique()).issubset(valid_levels):
                print("❌ Error: Invalid skill level values found")
                return False
            
            # 行数の検証
            summary = self.get_data_summary()
            expected_rows = summary['expected_rows']
            if len(df) != expected_rows:
                print(f"❌ Error: Expected {expected_rows} rows, but got {len(df)}")
                return False
            
            print("✅ Data validation passed!")
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {str(e)}")
            return False
