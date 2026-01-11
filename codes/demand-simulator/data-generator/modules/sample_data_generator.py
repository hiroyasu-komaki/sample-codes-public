#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サンプルデータ生成モジュール
YAMLファイルでデータ定義を読み込み、CSV形式でサンプルデータを出力します
"""

import yaml
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


class SampleDataGenerator:
    """サンプルデータ生成クラス"""
    
    def __init__(self, config_file='config/data_definition.yaml'):
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
    
    def _generate_project_id(self, index):
        """案件IDを生成"""
        # ID形式の設定をYAMLに追加することも可能
        id_format = self.settings.get('project_id_format', {})
        prefix = id_format.get('prefix', 'PRJ')
        digits = id_format.get('digits', 4)
        return f"{prefix}{index + 1:0{digits}d}"
    
    def _generate_project_name(self, index):
        """案件名を生成"""
        # プロジェクト名の選択肢をYAMLから取得
        naming = self.settings.get('project_naming', {})
        prefixes = naming.get('prefixes', ["次世代", "新規", "既存", "統合", "クラウド", "AI活用", "DX推進"])
        systems = naming.get('systems', [
            "販売管理システム", "在庫管理システム", "顧客管理システム", 
            "会計システム", "人事システム", "ECサイト", "基幹システム"
        ])
        actions = naming.get('actions', ["構築", "刷新", "移行", "導入", "開発"])
        
        prefix = random.choice(prefixes)
        system = random.choice(systems)
        action = random.choice(actions)
        
        return f"{prefix}{system}{action}プロジェクト"
    
    def _generate_initial_investment(self):
        """初期投資金額を生成（単位：千円）"""
        # YAMLから設定値を取得
        inv_config = self.settings.get('initial_investment', {})
        min_amount = inv_config.get('min', 10000)
        max_amount = inv_config.get('max', 500000)
        rounding = self.settings.get('rounding', {})
        
        # 範囲内でランダムに生成
        amount = random.randint(min_amount, max_amount)
        
        # キリの良い数字にする（YAMLから閾値と丸め単位を取得）
        thresholds = rounding.get('thresholds', [
            {'max': 1000, 'unit': 50},
            {'max': 10000, 'unit': 100},
            {'max': float('inf'), 'unit': 1000}
        ])
        
        for threshold in thresholds:
            if amount < threshold['max']:
                unit = threshold['unit']
                amount = (amount // unit) * unit
                break
        
        return amount
    
    def _generate_operation_cost(self, initial_investment):
        """運用費を生成（初期投資の設定された範囲%程度）"""
        # YAMLから運用費の割合を取得
        ratio_config = self.settings.get('operation_cost_ratio', {})
        min_ratio = ratio_config.get('min', 0.05)
        max_ratio = ratio_config.get('max', 0.20)
        
        ratio = random.uniform(min_ratio, max_ratio)
        cost = int(initial_investment * ratio)
        
        # キリの良い数字にする
        rounding = self.settings.get('rounding', {})
        cost_thresholds = rounding.get('thresholds', [
            {'max': 100, 'unit': 10},
            {'max': float('inf'), 'unit': 50}
        ])
        
        for threshold in cost_thresholds:
            if cost < threshold['max']:
                unit = threshold['unit']
                cost = (cost // unit) * unit
                break
        
        return cost
    
    def _generate_start_date(self):
        """システム利用開始時期を生成"""
        # YAMLから日付範囲を取得
        date_config = self.settings.get('start_date', {})
        from_days_ago = date_config.get('from_days_ago', 365)
        to_days_ahead = date_config.get('to_days_ahead', 730)
        
        base_date = datetime.now()
        days_offset = random.randint(-from_days_ago, to_days_ahead)
        start_date = base_date + timedelta(days=days_offset)
        
        # 日付フォーマットもYAMLから取得可能に
        date_format = self.settings.get('date_format', "%Y/%m/%d")
        return start_date.strftime(date_format)
    
    def _generate_activity_period(self):
        """活動開始月と活動終了月を生成"""
        # YAMLから活動期間の設定を取得
        activity_config = self.settings.get('activity_period', {})
        start_from_days_ago = activity_config.get('start_from_days_ago', 730)
        start_to_days_ahead = activity_config.get('start_to_days_ahead', 365)
        duration_min_months = activity_config.get('duration_min_months', 3)
        duration_max_months = activity_config.get('duration_max_months', 24)
        
        # 活動開始月を生成
        base_date = datetime.now()
        days_offset = random.randint(-start_from_days_ago, start_to_days_ahead)
        start_month = base_date + timedelta(days=days_offset)
        
        # 活動期間（月数）をランダムに決定
        duration_months = random.randint(duration_min_months, duration_max_months)
        
        # 活動終了月を計算（開始月 + 期間）
        # 月の加算を正確に行うため、年と月を分けて計算
        end_year = start_month.year
        end_month = start_month.month + duration_months
        
        # 12月を超える場合の処理
        while end_month > 12:
            end_month -= 12
            end_year += 1
        
        end_month_date = datetime(end_year, end_month, 1)
        
        # 月フォーマットを取得
        month_format = self.settings.get('month_format', "%Y/%m")
        
        return (
            start_month.strftime(month_format),
            end_month_date.strftime(month_format)
        )
    
    def generate_data(self, num_records):
        """
        サンプルデータを生成
        
        Args:
            num_records (int): 生成するレコード数
            
        Returns:
            list: サンプルデータのリスト
        """
        data = []
        headers = self.config.get('fields', [])
        
        for i in range(num_records):
            # 活動期間を生成
            activity_start, activity_end = self._generate_activity_period()
            
            record = {
                '案件ID': self._generate_project_id(i),
                '案件名': self._generate_project_name(i),
                '活動開始月': activity_start,
                '活動終了月': activity_end,
                '初期投資金額': self._generate_initial_investment(),
                '運用費': 0,  # 後で設定
                'システム利用開始時期': self._generate_start_date()
            }
            # 運用費を初期投資金額に基づいて設定
            record['運用費'] = self._generate_operation_cost(record['初期投資金額'])
            
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
