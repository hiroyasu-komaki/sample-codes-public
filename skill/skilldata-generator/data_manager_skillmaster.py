import yaml
from typing import List, Dict, Any
from pathlib import Path

class MasterDataManager:
    """
    マスターデータの読み込みと管理に特化したクラス
    YAMLファイルからマスターデータを読み込み、データアクセスメソッドを提供
    """
    
    def __init__(self, yaml_file_path: str = "yml/master_data.yaml"):
        """
        マスターデータマネージャーを初期化
        
        Args:
            yaml_file_path (str): YAMLファイルのパス
        """
        self.yaml_file_path = yaml_file_path
        self._master_data = None
        self._load_master_data()
    
    def _load_master_data(self) -> None:
        """
        YAMLファイルからマスターデータを読み込み
        
        Raises:
            FileNotFoundError: YAMLファイルが見つからない場合
            yaml.YAMLError: YAML解析エラーの場合
        """
        try:
            yaml_path = Path(self.yaml_file_path)
            if not yaml_path.exists():
                raise FileNotFoundError(f"マスターデータファイルが見つかりません: {self.yaml_file_path}")
            
            with open(yaml_path, 'r', encoding='utf-8') as file:
                self._master_data = yaml.safe_load(file)
                
            # 必要なキーの存在確認
            required_keys = ['roles', 'role_speciality_mapping', 'skill_level_mapping']
            for key in required_keys:
                if key not in self._master_data:
                    raise ValueError(f"無効なYAMLファイル構造です。'{key}'キーが必要です。")
                
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML解析エラー: {e}")
    
    def get_roles(self) -> List[str]:
        """
        全ての職種（ロール）を取得
        
        Returns:
            List[str]: 職種のリスト（順序が保持される）
        """
        return self._master_data['roles']
    
    def get_role_speciality_mapping(self) -> Dict[str, str]:
        """
        職種と専門性のマッピングを取得
        
        Returns:
            Dict[str, str]: 職種 -> 専門性のマッピング
        """
        return self._master_data['role_speciality_mapping']
    
    def get_skill_level_mapping(self) -> Dict[str, float]:
        """
        スキルレベルと数値のマッピングを取得
        
        Returns:
            Dict[str, float]: スキルレベル -> 数値のマッピング
        """
        return self._master_data['skill_level_mapping']
    
    def get_specialities(self) -> List[str]:
        """
        全ての専門性を取得
        
        Returns:
            List[str]: 専門性のリスト
        """
        return self._master_data.get('specialities', [])
    
    def get_skill_level_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        スキルレベルの詳細定義を取得
        
        Returns:
            Dict[str, Dict[str, Any]]: スキルレベルの詳細情報
        """
        return self._master_data.get('skill_level_definitions', {})
    
    def get_speciality_by_role(self, role: str) -> str:
        """
        指定された職種の専門性を取得
        
        Args:
            role (str): 職種名
            
        Returns:
            str: 専門性
            
        Raises:
            ValueError: 職種が見つからない場合
        """
        mapping = self.get_role_speciality_mapping()
        if role not in mapping:
            raise ValueError(f"職種 '{role}' が見つかりません")
        return mapping[role]
    
    def get_skill_level_value(self, level: str) -> float:
        """
        スキルレベルの数値を取得
        
        Args:
            level (str): スキルレベル (a, b, c, d, z)
            
        Returns:
            float: スキルレベルの数値
            
        Raises:
            ValueError: スキルレベルが見つからない場合
        """
        mapping = self.get_skill_level_mapping()
        if level not in mapping:
            raise ValueError(f"スキルレベル '{level}' が見つかりません")
        return mapping[level]
    
    def get_roles_by_speciality(self, speciality: str) -> List[str]:
        """
        指定された専門性に属する職種を取得
        
        Args:
            speciality (str): 専門性
            
        Returns:
            List[str]: その専門性に属する職種のリスト
        """
        mapping = self.get_role_speciality_mapping()
        return [role for role, spec in mapping.items() if spec == speciality]
    
    def validate_role(self, role: str) -> bool:
        """
        職種が有効かチェック
        
        Args:
            role (str): 職種名
            
        Returns:
            bool: 有効な場合True
        """
        return role in self.get_roles()
    
    def validate_skill_level(self, level: str) -> bool:
        """
        スキルレベルが有効かチェック
        
        Args:
            level (str): スキルレベル
            
        Returns:
            bool: 有効な場合True
        """
        return level in self.get_skill_level_mapping()
    
    def validate_speciality(self, speciality: str) -> bool:
        """
        専門性が有効かチェック
        
        Args:
            speciality (str): 専門性
            
        Returns:
            bool: 有効な場合True
        """
        return speciality in self.get_specialities()
    
    def validate_data(self) -> bool:
        """
        マスターデータの整合性を検証
        
        Returns:
            bool: 検証結果（True: 正常, False: 異常）
        """
        try:
            # 職種と専門性のマッピング整合性チェック
            roles = set(self.get_roles())
            mapping_roles = set(self.get_role_speciality_mapping().keys())
            
            if roles != mapping_roles:
                print("エラー: 職種リストとマッピングの職種が一致しません")
                return False
            
            # 専門性の整合性チェック
            mapping_specialities = set(self.get_role_speciality_mapping().values())
            defined_specialities = set(self.get_specialities())
            
            if mapping_specialities != defined_specialities:
                print("エラー: マッピングの専門性と定義済み専門性が一致しません")
                return False
            
            # スキルレベル定義の整合性チェック
            skill_levels = set(self.get_skill_level_mapping().keys())
            defined_levels = set(self.get_skill_level_definitions().keys())
            
            if skill_levels != defined_levels:
                print("エラー: スキルレベルマッピングと定義が一致しません")
                return False
            
            print("マスターデータ検証成功: 全てのデータが正常です")
            return True
            
        except Exception as e:
            print(f"マスターデータ検証エラー: {str(e)}")
            return False
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        マスターデータの概要情報を取得
        
        Returns:
            Dict[str, Any]: データ概要
        """
        return {
            'total_roles': len(self.get_roles()),
            'total_specialities': len(self.get_specialities()),
            'total_skill_levels': len(self.get_skill_level_mapping()),
            'roles': self.get_roles(),
            'specialities': self.get_specialities(),
            'skill_levels': list(self.get_skill_level_mapping().keys())
        }