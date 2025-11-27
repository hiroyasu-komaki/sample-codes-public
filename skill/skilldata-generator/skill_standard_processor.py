import pandas as pd
from data_manager_skillstd import SkillDataManager
from data_manager_skillmaster import MasterDataManager

class SkillStandardProcessor:
    def __init__(self, skills_yaml_path: str = "yml/skillstd.yaml", master_data_yaml_path: str = "yml/master_data.yaml"):
        """
        スキル標準プロセッサーを初期化
        
        Args:
            skills_yaml_path (str): スキルデータYAMLファイルのパス
            master_data_yaml_path (str): マスターデータYAMLファイルのパス
        """
        self.skill_manager = SkillDataManager(skills_yaml_path)
        self.master_manager = MasterDataManager(master_data_yaml_path)
        self.raw_data = {
            'カテゴリー': [],
            'サブカテゴリー': [],
            'スキル項目': [],
            'ロール': [],
            '専門性': [],
            'スキルレベル': []
        }

    def process_data(self) -> pd.DataFrame:
        """
        スキルデータを処理してDataFrameを作成します。
        
        Returns:
            pd.DataFrame: 処理済みのスキルデータ
        """
        roles = self.master_manager.get_roles()
        role_speciality_mapping = self.master_manager.get_role_speciality_mapping()
        skills_data = self.skill_manager.get_all_skills()

        # データの展開
        for skill in skills_data:
            category = skill.get('category')
            subcategory = skill.get('subcategory')
            skill_name = skill.get('skill_name')
            levels = skill.get('levels', {})
            
            # 各ロールに対するスキルレベルを展開
            for role in roles:
                skill_level = levels.get(role, 'd')  # デフォルトは'd'
                speciality = role_speciality_mapping.get(role, 'その他')
                
                self.raw_data['カテゴリー'].append(category)
                self.raw_data['サブカテゴリー'].append(subcategory)
                self.raw_data['スキル項目'].append(skill_name)
                self.raw_data['ロール'].append(role)
                self.raw_data['専門性'].append(speciality)
                self.raw_data['スキルレベル'].append(skill_level)

        # DataFrameを作成
        df = pd.DataFrame(self.raw_data)
        
        # スキルレベルを数値に変換
        df['スキルレベル_数値'] = df['スキルレベル'].map(
            self.master_manager.get_skill_level_mapping()
        )

        return df

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        生成されたデータの検証を行います。
        
        Args:
            df (pd.DataFrame): 検証するDataFrame
        
        Returns:
            bool: 検証結果（True: 正常, False: 異常）
        """
        try:
            # YAMLデータの検証
            if not self.skill_manager.validate_data():
                return False
                
            if not self.master_manager.validate_data():
                return False
            
            # 必須カラムの存在チェック
            required_columns = [
                'カテゴリー', 'サブカテゴリー', 'スキル項目', 
                'ロール', '専門性', 'スキルレベル', 'スキルレベル_数値'
            ]
            for col in required_columns:
                if col not in df.columns:
                    print(f"Error: Missing column {col}")
                    return False

            # NULL値のチェック
            if df.isnull().any().any():
                print("Error: Found NULL values in data")
                return False

            # スキルレベルの値チェック
            valid_levels = set(self.master_manager.get_skill_level_mapping().keys())
            if not set(df['スキルレベル'].unique()).issubset(valid_levels):
                print("Error: Invalid skill level values found")
                return False

            # 行数の検証
            expected_rows = len(self.skill_manager.get_all_skills()) * len(self.master_manager.get_roles())
            if len(df) != expected_rows:
                print(f"Error: Expected {expected_rows} rows, but got {len(df)}")
                return False

            print("Data validation successful!")
            return True

        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False
    
    def get_data_summary(self) -> dict:
        """
        データの概要情報を取得
        
        Returns:
            dict: データ概要情報
        """
        skill_summary = self.skill_manager.get_data_summary()
        master_summary = self.master_manager.get_data_summary()
        
        return {
            'skills': skill_summary,
            'master_data': master_summary,
            'expected_total_rows': skill_summary['total_skills'] * master_summary['total_roles']
        }