"""
サンプルデータ生成モジュール
シンプル汎用版
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import random


class SurveyDataGenerator:
    """汎用データ生成クラス"""
    
    def __init__(self, config_file):
        """
        初期化
        
        Args:
            config_file: 設定ファイル(YAML)のパス
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {config_file}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        if self.config is None:
            raise ValueError(f"YAMLファイルが空です: {config_file}")
        
        self.config_name = config_path.stem
        self.fields = self.config.get('fields', [])
        self.enums = self.config.get('enums', {})
    
    def generate_sample_data(self, n=100):
        """
        サンプルデータの生成
        
        Args:
            n: 生成するサンプル数
            
        Returns:
            DataFrame: 生成されたサンプルデータ
        """
        np.random.seed(42)
        random.seed(42)
        
        data = {}
        
        # 先にenum型フィールドの値を生成
        enum_values = {}
        for field in self.fields:
            field_name = field.get('name')
            field_type = field.get('type')
            
            if field_type == 'enum':
                enum_ref = field.get('enum_ref')
                if enum_ref and enum_ref in self.enums:
                    enum_def = self.enums[enum_ref]
                    values = [v['id'] for v in enum_def.get('values', [])]
                    enum_values[field_name] = [random.choice(values) for _ in range(n)]
        
        # 各フィールドのデータを生成
        for field in self.fields:
            field_name = field.get('name')
            field_type = field.get('type')
            required = field.get('required', True)
            
            column_data = self._generate_field_data(
                field_name, field_type, field, n, enum_values
            )
            
            # required=Falseの場合、50%を欠損値に
            if not required:
                column_data = list(column_data)
                missing_count = int(n * 0.5)
                if missing_count > 0:
                    missing_indices = np.random.choice(n, size=missing_count, replace=False)
                    for idx in missing_indices:
                        column_data[idx] = None
            
            data[field_name] = column_data
        
        return pd.DataFrame(data)
    
    def _generate_field_data(self, field_name, field_type, field_config, n, enum_values):
        """フィールドごとのデータ生成"""
        
        # enum型
        if field_type == 'enum':
            return enum_values.get(field_name, ['unknown'] * n)
        
        # integer型
        if field_type == 'integer':
            # primary_keyの場合は連番
            if field_config.get('primary_key'):
                return list(range(1, n+1))
            
            # 制約がある場合
            constraints = field_config.get('constraints', {})
            if constraints:
                min_val = constraints.get('min', 1)
                max_val = constraints.get('max', 100)
                return np.random.randint(min_val, max_val + 1, n).tolist()
            
            # respondent_idは101から連番
            if field_name == 'respondent_id':
                return list(range(101, 101 + n))
            
            return np.random.randint(1, 1000, n).tolist()
        
        # boolean型
        if field_type == 'boolean':
            return np.random.choice([True, False], n).tolist()
        
        # text型
        if field_type == 'text':
            comments = [
                "対応は迅速でしたが、もう少し詳細な説明が欲しかったです。",
                "技術的な知識が豊富で、安心して任せられます。",
                "コミュニケーションが取りやすく、信頼できるパートナーです。",
                "改善提案が的確で、ビジネスに貢献してくれています。",
                "もう少しコストを抑えられると助かります。",
                "今後も継続して利用したいと思います。",
                "一部対応に遅れが見られることがあります。",
                "全体的に満足していますが、ドキュメントの質を向上してほしいです。",
            ]
            return [random.choice(comments) if random.random() > 0.3 else None for _ in range(n)]
        
        # datetime型
        if field_type == 'datetime':
            base_date = datetime.now()
            dates = []
            for _ in range(n):
                days_offset = random.randint(-30, 0)
                hours_offset = random.randint(8, 18)
                minutes_offset = random.randint(0, 59)
                date = base_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
                dates.append(date.strftime('%Y-%m-%d %H:%M:%S'))
            return dates
        
        # date型
        if field_type == 'date':
            date_format = field_config.get('format', 'YYYY-MM-DD')
            base_year = datetime.now().year
            dates = []
            for _ in range(n):
                year = base_year + random.randint(1, 3)
                month = random.randint(1, 12)
                if 'YYYY年M月' in date_format:
                    dates.append(f'{year}年{month}月')
                elif 'MMMM YYYY' in date_format:
                    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                                 'July', 'August', 'September', 'October', 'November', 'December']
                    dates.append(f'{month_names[month-1]} {year}')
                else:
                    dates.append(f'{year}-{month:02d}')
            return dates
        
        # array型
        if field_type == 'array':
            if 'tag' in field_name.lower():
                all_tags = ['React', 'Vue.js', 'Angular', 'Node.js', 'Python', 'Java', 
                           'PostgreSQL', 'MongoDB', 'AWS', 'Azure', 'Docker', 'Kubernetes']
                return [random.sample(all_tags, random.randint(2, 5)) for _ in range(n)]
            elif 'project' in field_name.lower():
                project_ids = ['ecommerce', 'crm', 'erp', 'analytics', 'mobile', 'portal']
                return [random.sample(project_ids, random.randint(1, 3)) for _ in range(n)]
            return [[] for _ in range(n)]
        
        # string型
        if field_type == 'string':
            # ラベルフィールド（JAで終わる、大文字小文字両対応）
            if field_name.endswith('JA') or field_name.endswith('_ja'):
                # categoryJA → category, department_ja → department
                base_field = field_name[:-2] if field_name.endswith('JA') else field_name[:-3]
                if base_field in enum_values:
                    enum_ref = self._get_enum_ref(base_field)
                    if enum_ref:
                        enum_def = self.enums.get(enum_ref, {})
                        return [self._get_enum_label(val, enum_def, 'ja') for val in enum_values[base_field]]
                return ['不明'] * n
            
            # ラベルフィールド（ENで終わる、大文字小文字両対応）
            if field_name.endswith('EN') or field_name.endswith('_en'):
                # categoryEN → category, department_en → department
                base_field = field_name[:-2] if field_name.endswith('EN') else field_name[:-3]
                if base_field in enum_values:
                    enum_ref = self._get_enum_ref(base_field)
                    if enum_ref:
                        enum_def = self.enums.get(enum_ref, {})
                        return [self._get_enum_label(val, enum_def, 'en') for val in enum_values[base_field]]
                return ['Unknown'] * n
            
            # vendor_name
            if field_name == 'vendor_name':
                if 'vendor_id' in enum_values:
                    vendor_enum = self.enums.get('vendorId', {})
                    return [self._get_enum_attr(val, vendor_enum, 'name') for val in enum_values['vendor_id']]
                return ['不明'] * n
            
            # id (primary_key)
            if field_name == 'id' or field_config.get('primary_key'):
                prefixes = ['ec', 'crm', 'erp', 'cms', 'api', 'admin', 'portal', 'dashboard', 'mobile', 'web']
                suffixes = ['site', 'system', 'service', 'app', 'platform', 'tool']
                return [f'{random.choice(prefixes)}-{random.choice(suffixes)}' for _ in range(n)]
            
            # nameJA
            if field_name == 'nameJA' or (field_name.endswith('JA') and 'name' in field_name.lower()):
                names = ['ECサイト', 'CRMシステム', 'ERPシステム', '顧客管理システム', 
                        '在庫管理システム', '販売管理システム', 'Webポータル', 'モバイルアプリ', 
                        'データ分析基盤', 'マーケティングツール', '社内SNS', 'ワークフローシステム']
                return [random.choice(names) for _ in range(n)]
            
            # nameEN
            if field_name == 'nameEN' or (field_name.endswith('EN') and 'name' in field_name.lower()):
                names = ['E-Commerce Site', 'CRM System', 'ERP System', 'Customer Management System',
                        'Inventory Management System', 'Sales Management System', 'Web Portal', 'Mobile App',
                        'Data Analytics Platform', 'Marketing Tool', 'Internal SNS', 'Workflow System']
                return [random.choice(names) for _ in range(n)]
            
            # icon
            if 'icon' in field_name.lower():
                icons = ['🛒', '💼', '📊', '📝', '👥', '📦', '💰', '🔧', '🌐', '📱', '⚙️', '🔐']
                return [random.choice(icons) for _ in range(n)]
            
            # デフォルト
            return [f'Value-{i:04d}' for i in range(1, n+1)]
        
        # デフォルト
        return [f'Data-{i:04d}' for i in range(1, n+1)]
    
    def _get_enum_ref(self, field_name):
        """フィールド名からenum_refを取得"""
        for field in self.fields:
            if field.get('name') == field_name and field.get('type') == 'enum':
                return field.get('enum_ref')
        return None
    
    def _get_enum_label(self, enum_id, enum_def, lang):
        """enum定義から指定言語のラベルを取得"""
        values = enum_def.get('values', [])
        for value in values:
            if value.get('id') == enum_id:
                return value.get(lang, enum_id)
        return enum_id
    
    def _get_enum_attr(self, enum_id, enum_def, attr):
        """enum定義から指定属性を取得"""
        values = enum_def.get('values', [])
        for value in values:
            if value.get('id') == enum_id:
                return value.get(attr, enum_id)
        return enum_id
    
    def save_to_csv(self, df, output_dir='csv'):
        """CSVに保存"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = f'{self.config_name}.csv'
        filepath = Path(output_dir) / filename
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        return str(filepath)
    
    def save_to_json(self, df, output_dir='json'):
        """JSONに保存"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = f'{self.config_name}.json'
        filepath = Path(output_dir) / filename
        df.to_json(filepath, orient='records', force_ascii=False, indent=2)
        return str(filepath)
    
    def get_statistics(self, df):
        """統計情報の取得"""
        return {
            'total_samples': len(df),
            'total_columns': len(df.columns),
            'ratings': {}
        }