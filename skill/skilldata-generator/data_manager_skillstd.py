import yaml
from typing import List, Dict, Any
from pathlib import Path

class SkillDataManager:
    """
    スキルデータの読み込みと操作に特化したクラス
    YAMLファイルからスキルデータを読み込み、データ操作メソッドを提供
    """
    
    def __init__(self, yaml_file_path: str = "yml/skillstd.yaml"):
        """
        スキルデータマネージャーを初期化
        
        Args:
            yaml_file_path (str): YAMLファイルのパス
        """
        self.yaml_file_path = yaml_file_path
        self._skills_data = None
        self._load_skills_data()
    
    def _load_skills_data(self) -> None:
        """
        YAMLファイルからスキルデータを読み込み
        
        Raises:
            FileNotFoundError: YAMLファイルが見つからない場合
            yaml.YAMLError: YAML解析エラーの場合
        """
        try:
            yaml_path = Path(self.yaml_file_path)
            if not yaml_path.exists():
                raise FileNotFoundError(f"スキルデータファイルが見つかりません: {self.yaml_file_path}")
            
            with open(yaml_path, 'r', encoding='utf-8') as file:
                self._skills_data = yaml.safe_load(file)
                
            if not self._skills_data or 'skills' not in self._skills_data:
                raise ValueError("無効なYAMLファイル構造です。'skills'キーが必要です。")
                
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML解析エラー: {e}")
    
    def get_all_skills(self) -> List[Dict[str, Any]]:
        """
        全てのスキルデータを取得
        
        Returns:
            List[Dict[str, Any]]: スキルデータのリスト
        """
        return self._skills_data['skills']
    
    def get_skills_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        カテゴリー別にスキルデータを取得
        
        Args:
            category (str): カテゴリー名
            
        Returns:
            List[Dict[str, Any]]: 指定カテゴリーのスキルデータ
        """
        return [
            skill for skill in self._skills_data['skills']
            if skill.get('category') == category
        ]
    
    def get_skills_by_subcategory(self, subcategory: str) -> List[Dict[str, Any]]:
        """
        サブカテゴリー別にスキルデータを取得
        
        Args:
            subcategory (str): サブカテゴリー名
            
        Returns:
            List[Dict[str, Any]]: 指定サブカテゴリーのスキルデータ
        """
        return [
            skill for skill in self._skills_data['skills']
            if skill.get('subcategory') == subcategory
        ]
    
    def get_skill_by_name(self, skill_name: str) -> Dict[str, Any]:
        """
        スキル名でスキルデータを取得
        
        Args:
            skill_name (str): スキル名
            
        Returns:
            Dict[str, Any]: スキルデータ
            
        Raises:
            ValueError: スキルが見つからない場合
        """
        for skill in self._skills_data['skills']:
            if skill.get('skill_name') == skill_name:
                return skill
        
        raise ValueError(f"スキル '{skill_name}' が見つかりません")
    
    def get_all_categories(self) -> List[str]:
        """
        全てのカテゴリー名を取得
        
        Returns:
            List[str]: 重複を除いたカテゴリー名のリスト
        """
        categories = set()
        for skill in self._skills_data['skills']:
            categories.add(skill.get('category'))
        return sorted(list(categories))
    
    def get_all_subcategories(self) -> List[str]:
        """
        全てのサブカテゴリー名を取得
        
        Returns:
            List[str]: 重複を除いたサブカテゴリー名のリスト
        """
        subcategories = set()
        for skill in self._skills_data['skills']:
            subcategories.add(skill.get('subcategory'))
        return sorted(list(subcategories))
    
    def get_all_skill_names(self) -> List[str]:
        """
        全てのスキル名を取得
        
        Returns:
            List[str]: スキル名のリスト
        """
        return [skill.get('skill_name') for skill in self._skills_data['skills']]
    
    def get_all_roles(self) -> List[str]:
        """
        全てのロール（職種）名を取得
        
        Returns:
            List[str]: ロール名のリスト
        """
        if not self._skills_data['skills']:
            return []
        
        # 最初のスキルのlevelsキーからロール名を取得
        first_skill = self._skills_data['skills'][0]
        return list(first_skill.get('levels', {}).keys())
    
    def get_skill_level(self, skill_name: str, role: str) -> str:
        """
        特定のスキルと職種の組み合わせでスキルレベルを取得
        
        Args:
            skill_name (str): スキル名
            role (str): 職種名
            
        Returns:
            str: スキルレベル (a, b, c, d, z)
            
        Raises:
            ValueError: スキルまたは職種が見つからない場合
        """
        skill_data = self.get_skill_by_name(skill_name)
        levels = skill_data.get('levels', {})
        
        if role not in levels:
            raise ValueError(f"職種 '{role}' が見つかりません")
        
        return levels[role]
    
    def get_skills_for_role(self, role: str) -> List[Dict[str, str]]:
        """
        特定の職種のすべてのスキルレベルを取得
        
        Args:
            role (str): 職種名
            
        Returns:
            List[Dict[str, str]]: スキル情報とレベルのリスト
        """
        result = []
        for skill in self._skills_data['skills']:
            levels = skill.get('levels', {})
            if role in levels:
                result.append({
                    'category': skill.get('category'),
                    'subcategory': skill.get('subcategory'),
                    'skill_name': skill.get('skill_name'),
                    'level': levels[role]
                })
        return result
    
    def convert_to_legacy_format(self) -> List[List[str]]:
        """
        従来のリスト形式（skill_data.py形式）に変換
        既存のSkillStandardProcessorとの互換性のため
        
        Returns:
            List[List[str]]: [カテゴリー, サブカテゴリー, スキル名, level1, level2, ...]形式
        """
        result = []
        roles = self.get_all_roles()
        
        for skill in self._skills_data['skills']:
            row = [
                skill.get('category'),
                skill.get('subcategory'),
                skill.get('skill_name')
            ]
            
            # 各職種のレベルを順番に追加
            levels = skill.get('levels', {})
            for role in roles:
                row.append(levels.get(role, 'd'))  # デフォルトは'd'
            
            result.append(row)
        
        return result
    
    def validate_data(self) -> bool:
        """
        データの整合性を検証
        
        Returns:
            bool: 検証結果（True: 正常, False: 異常）
        """
        try:
            skills = self._skills_data['skills']
            if not skills:
                print("エラー: スキルデータが空です")
                return False
            
            # 必須フィールドの確認
            required_fields = ['category', 'subcategory', 'skill_name', 'levels']
            for i, skill in enumerate(skills):
                for field in required_fields:
                    if field not in skill:
                        print(f"エラー: スキル {i} に必須フィールド '{field}' がありません")
                        return False
            
            # 全スキルが同じ職種を持っているかチェック
            roles = self.get_all_roles()
            for skill in skills:
                skill_roles = set(skill.get('levels', {}).keys())
                if skill_roles != set(roles):
                    print(f"エラー: スキル '{skill.get('skill_name')}' の職種が不整合です")
                    return False
            
            # スキルレベルの値チェック
            valid_levels = {'a', 'b', 'c', 'd', 'z'}
            for skill in skills:
                for role, level in skill.get('levels', {}).items():
                    if level not in valid_levels:
                        print(f"エラー: 無効なスキルレベル '{level}' (スキル: {skill.get('skill_name')}, 職種: {role})")
                        return False
            
            print("データ検証成功: 全てのデータが正常です")
            return True
            
        except Exception as e:
            print(f"検証エラー: {str(e)}")
            return False
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        データの概要情報を取得
        
        Returns:
            Dict[str, Any]: データ概要
        """
        return {
            'total_skills': len(self._skills_data['skills']),
            'categories': self.get_all_categories(),
            'subcategories': self.get_all_subcategories(),
            'roles': self.get_all_roles(),
            'category_count': len(self.get_all_categories()),
            'subcategory_count': len(self.get_all_subcategories()),
            'role_count': len(self.get_all_roles())
        }