#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
供給データ（社員データ）生成モジュール
YAMLファイルでデータ定義を読み込み、CSV形式でサンプルデータを出力します
"""

import yaml
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


class SupplyDataGenerator:
    """供給データ（社員データ）生成クラス"""
    
    def __init__(self, config_file='config/data_definition_supply.yaml'):
        """
        初期化
        
        Args:
            config_file (str): YAML設定ファイルのパス
        """
        self.config_file = config_file
        self.config = self._load_config()
        # 設定値を取得
        self.settings = self.config.get('settings', {})
        
    def _load_config(self):
        """YAML設定ファイルを読み込む"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML解析エラー: {e}")
    
    def _generate_employee_id(self, index):
        """
        社員IDを生成
        
        Args:
            index (int): インデックス番号
            
        Returns:
            str: 社員ID（例: EMP00001）
        """
        id_format = self.settings.get('employee_id_format', {})
        prefix = id_format.get('prefix', 'EMP')
        digits = id_format.get('digits', 5)
        return f"{prefix}{index + 1:0{digits}d}"
    
    def _generate_work_start_month(self):
        """
        稼働開始月を生成
        既存社員の場合は過去年月、入社予定者は将来年月
        
        Returns:
            datetime: 稼働開始月
        """
        work_start_config = self.settings.get('work_start_period', {})
        from_days_ago = work_start_config.get('from_days_ago', 1825)  # デフォルト5年前
        to_days_ahead = work_start_config.get('to_days_ahead', 365)   # デフォルト1年後
        
        base_date = datetime.now()
        days_offset = random.randint(-from_days_ago, to_days_ahead)
        start_date = base_date + timedelta(days=days_offset)
        
        # 月初に正規化
        return datetime(start_date.year, start_date.month, 1)
    
    def _generate_work_end_month(self, work_start_month):
        """
        稼働終了月を生成
        既存社員で且つ退職年月が決まっている場合のみ設定
        
        Args:
            work_start_month (datetime): 稼働開始月
            
        Returns:
            str or None: 稼働終了月（YYYY/MM形式）またはNone
        """
        work_end_config = self.settings.get('work_end_period', {})
        probability = work_end_config.get('probability', 0.2)
        
        # 確率判定：退職年月を設定するか
        if random.random() > probability:
            return None
        
        # 稼働開始月より後の日付を生成
        min_months = work_end_config.get('min_months_after_start', 6)
        max_months = work_end_config.get('max_months_after_start', 60)
        
        months_after = random.randint(min_months, max_months)
        
        # 月の加算
        end_year = work_start_month.year
        end_month = work_start_month.month + months_after
        
        # 12月を超える場合の処理
        while end_month > 12:
            end_month -= 12
            end_year += 1
        
        end_date = datetime(end_year, end_month, 1)
        
        # 月フォーマットを取得
        month_format = self.settings.get('month_format', "%Y/%m")
        return end_date.strftime(month_format)
    
    def _generate_capability_value(self):
        """
        ケイパビリティ値を生成（0.00〜1.00の範囲）
        
        Returns:
            float: ケイパビリティ値（小数点第2位まで）
        """
        capability_config = self.settings.get('capability', {})
        min_val = capability_config.get('min', 0.0)
        max_val = capability_config.get('max', 1.0)
        decimal_places = capability_config.get('decimal_places', 2)
        
        # ランダムな値を生成
        value = random.uniform(min_val, max_val)
        
        # 指定された小数点以下の桁数に丸める
        return round(value, decimal_places)
    
    def _generate_correlated_capabilities(self):
        """
        相関を考慮したケイパビリティ値を生成
        
        Returns:
            dict: 4つのケイパビリティ値
        """
        capability_config = self.settings.get('capability', {})
        correlation_config = capability_config.get('correlation', {})
        
        if not correlation_config.get('enabled', False):
            # 相関を考慮しない場合は独立して生成
            return {
                'ビジネスケイパビリティ': self._generate_capability_value(),
                'デリバリケイパビリティ': self._generate_capability_value(),
                'テクニカルケイパビリティ': self._generate_capability_value(),
                'リーダーシップケイパビリティ': self._generate_capability_value()
            }
        
        # 相関を考慮する場合
        base_variance = correlation_config.get('base_variance', 0.3)
        
        # 基準値を生成（この社員の全体的なスキルレベル）
        base_value = random.uniform(0.3, 0.9)
        
        capabilities = {}
        capability_names = [
            'ビジネスケイパビリティ',
            'デリバリケイパビリティ',
            'テクニカルケイパビリティ',
            'リーダーシップケイパビリティ'
        ]
        
        for name in capability_names:
            # 基準値からの変動を加える
            variance = random.uniform(-base_variance, base_variance)
            value = base_value + variance
            
            # 0.0〜1.0の範囲に収める
            value = max(0.0, min(1.0, value))
            
            # 小数点第2位まで丸める
            capabilities[name] = round(value, 2)
        
        return capabilities
    
    def generate_data(self, num_records):
        """
        サンプルデータを生成
        
        Args:
            num_records (int): 生成するレコード数
            
        Returns:
            list: サンプルデータのリスト
        """
        data = []
        month_format = self.settings.get('month_format', "%Y/%m")
        
        for i in range(num_records):
            # 稼働開始月を生成
            work_start_month = self._generate_work_start_month()
            
            # 稼働終了月を生成（条件により設定されない場合がある）
            work_end_month = self._generate_work_end_month(work_start_month)
            
            # 相関を考慮したケイパビリティ値を生成
            capabilities = self._generate_correlated_capabilities()
            
            record = {
                '社員ID': self._generate_employee_id(i),
                '稼働開始月': work_start_month.strftime(month_format),
                '稼働終了月': work_end_month if work_end_month else '',
                'ビジネスケイパビリティ': capabilities['ビジネスケイパビリティ'],
                'デリバリケイパビリティ': capabilities['デリバリケイパビリティ'],
                'テクニカルケイパビリティ': capabilities['テクニカルケイパビリティ'],
                'リーダーシップケイパビリティ': capabilities['リーダーシップケイパビリティ']
            }
            
            data.append(record)
        
        return data
    
    def save_to_csv(self, data, output_file):
        """
        データをCSVファイルに保存
        
        Args:
            data (list): 保存するデータ
            output_file (str): 出力ファイルパス
        """
        if not data:
            raise ValueError("保存するデータがありません")
        
        # 出力ディレクトリが存在しない場合は作成
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        headers = list(data[0].keys())
        
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"CSVファイルを出力しました: {output_file}")
        print(f"レコード数: {len(data)}件")
    
    def get_output_config(self):
        """
        出力設定を取得
        
        Returns:
            dict: 出力設定（file, records）
        """
        return self.config.get('output', {})
