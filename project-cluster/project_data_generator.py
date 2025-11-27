#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import json
import pandas as pd
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import numpy as np
import os
import hashlib
import time

from config_loader import ConfigLoader

class ProjectDataGenerator:
    """設定ファイル駆動型プロジェクトデータ生成クラス"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load_config()
        
        # 設定から各種データを取得
        self.project_categories = self.config_loader.get_project_categories()
        self.industry_modifiers = self.config_loader.get_industry_modifiers()
        self.departments = self.config_loader.get_departments()
        self.complexity_settings = self.config_loader.get_complexity_settings()
        self.generation_settings = self.config_loader.get_generation_settings()
        self.output_settings = self.config_loader.get_output_settings()
        
        # シグナル選択肢の取得
        self.signal_options = self.config.get('signal_options', {})
        
        # ユニークID生成用のベースタイムスタンプ（生成開始時刻）
        self._generation_timestamp = int(time.time() * 1000)  # ミリ秒
        self._project_counter = 0

    def _generate_unique_project_id(self, category: str, industry: str) -> str:
        """
        ユニークなプロジェクトIDを生成
        
        Args:
            category (str): カテゴリー名
            industry (str): 業界名
        
        Returns:
            str: ユニークなプロジェクトID (例: P7A3F2B8)
        """
        self._project_counter += 1
        
        # 複数の要素を組み合わせてユニーク性を確保
        unique_string = f"{self._generation_timestamp}_{self._project_counter}_{category}_{industry}_{random.randint(1000, 9999)}"
        
        # SHA256ハッシュを生成して先頭8文字を使用（十分にユニーク）
        hash_object = hashlib.sha256(unique_string.encode())
        hash_hex = hash_object.hexdigest()[:8].upper()
        
        return f"P{hash_hex}"

    def generate_realistic_projects(self, 
                                  n_projects: Optional[int] = None, 
                                  industry: str = 'Healthcare',
                                  seed: Optional[int] = None) -> List[Dict]:
        """
        リアルなプロジェクトデータを生成
        
        Args:
            n_projects (int, optional): 生成するプロジェクト数
            industry (str): 業界名
            seed (int, optional): ランダムシード
        
        Returns:
            List[Dict]: プロジェクトデータリスト
        """
        # デフォルト値の設定
        if n_projects is None:
            n_projects = self.generation_settings.get('default_project_count', 100)
        
        if seed is None:
            seed = self.generation_settings.get('default_seed')
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # 業界修正値の取得
        if industry not in self.industry_modifiers:
            available_industries = list(self.industry_modifiers.keys())
            raise ValueError(f"未対応の業界です: {industry}. 利用可能: {available_industries}")
        
        industry_mod = self.industry_modifiers[industry]
        projects = []
        
        for i in range(n_projects):
            # カテゴリーをランダム選択
            category = random.choice(list(self.project_categories.keys()))
            category_data = self.project_categories[category]
            
            # 基本データ生成
            project = self._generate_single_project(category, category_data, industry_mod, industry)
            projects.append(project)
        
        return projects

    def _generate_single_project(self, category: str, 
                               category_data: Dict, industry_mod: Dict, industry: str) -> Dict:
        """
        単一プロジェクトの生成
        
        Args:
            category (str): カテゴリー名
            category_data (Dict): カテゴリーデータ
            industry_mod (Dict): 業界修正値
            industry (str): 業界名
        
        Returns:
            Dict: プロジェクトデータ
        """
        
        # 基本情報
        project = {
            'project_id': self._generate_unique_project_id(category, industry),
            'project_name': f'{category.replace("_", " ")} Project {self._project_counter:03d}',
            'category': category,
        }
        
        # 定性指標の生成（範囲はタプルまたはリストで指定）
        project['strategic_alignment'] = random.randint(*self._ensure_range(category_data['strategic_alignment_range']))
        
        base_risk = random.randint(*self._ensure_range(category_data['risk_range']))
        project['risk'] = min(5, max(1, int(base_risk * industry_mod['risk_modifier'])))
        
        project['urgency'] = random.randint(*self._ensure_range(category_data['urgency_range']))
        project['importance'] = random.randint(*self._ensure_range(category_data['importance_range']))
        
        # 定量指標の生成
        project['budget'] = random.randint(*self._ensure_range(category_data['budget_range']))
        project['duration'] = random.randint(*self._ensure_range(category_data['duration_range']))
        
        base_roi = random.randint(*self._ensure_range(category_data['roi_range']))
        project['roi'] = int(base_roi * industry_mod['roi_multiplier'])
        
        # 従来の追加情報
        project['start_date'] = self._generate_start_date()
        project['department'] = self._generate_department()
        project['stakeholders'] = self._generate_stakeholders()
        
        # シグナル項目の生成
        project.update(self._generate_signal_items())
        
        # 複雑度計算
        project['complexity'] = self._calculate_complexity(project)
        
        return project

    def _generate_signal_items(self) -> Dict:
        """
        シグナル項目の生成
        
        Returns:
            Dict: シグナル項目辞書
        """
        signals = {}
        
        # 各シグナル項目をランダムに選択
        for signal_name, options in self.signal_options.items():
            signals[signal_name] = random.choice(options)
        
        return signals

    def _ensure_range(self, range_value):
        """範囲値をタプルに変換"""
        if isinstance(range_value, list):
            return tuple(range_value)
        return range_value

    def _generate_start_date(self) -> str:
        """開始日の生成"""
        date_range = self.generation_settings.get('start_date_range', [-90, 180])
        base_date = datetime.now()
        days_offset = random.randint(*date_range)
        start_date = base_date + timedelta(days=days_offset)
        return start_date.strftime('%Y-%m-%d')

    def _generate_department(self) -> str:
        """部門の生成"""
        return random.choice(self.departments)

    def _generate_stakeholders(self) -> int:
        """ステークホルダー数の生成"""
        stakeholders_range = self.generation_settings.get('stakeholders_range', [3, 15])
        return random.randint(*stakeholders_range)

    def _calculate_complexity(self, project: Dict) -> str:
        """
        複雑度の計算
        
        Args:
            project (Dict): プロジェクトデータ
        
        Returns:
            str: 複雑度（High/Medium/Low）
        """
        weights = self.complexity_settings['weights']
        normalization = self.complexity_settings['normalization']
        thresholds = self.complexity_settings['thresholds']
        
        complexity_score = (
            project['risk'] * weights['risk'] +
            (project['duration'] / normalization['duration_max']) * 5 * weights['duration'] +
            (project['stakeholders'] / normalization['stakeholders_max']) * 5 * weights['stakeholders'] +
            (project['budget'] / normalization['budget_max']) * 5 * weights['budget']
        )
        
        if complexity_score >= thresholds['high']:
            return 'High'
        elif complexity_score >= thresholds['medium']:
            return 'Medium'
        else:
            return 'Low'

    def generate_sample_datasets(self) -> Dict[str, List[Dict]]:
        """
        複数の業界向けサンプルデータセットを生成
        
        Returns:
            Dict[str, List[Dict]]: 業界別データセット
        """
        datasets = {}
        default_count = self.generation_settings.get('default_project_count', 100) // 2  # サンプル用に半分
        seed = self.generation_settings.get('default_seed', 42)
        
        # 各業界で独立したカウンターとタイムスタンプを使用
        for industry in self.industry_modifiers.keys():
            # 業界ごとに新しいタイムスタンプを設定（重複回避）
            self._generation_timestamp = int(time.time() * 1000) + hash(industry) % 10000
            self._project_counter = 0
            
            datasets[industry] = self.generate_realistic_projects(
                n_projects=default_count, 
                industry=industry, 
                seed=seed
            )
        
        return datasets

    def save_to_file(self, projects: List[Dict], 
                    filename: str) -> str:
        """
        CSVファイルに保存
        
        Args:
            projects (List[Dict]): プロジェクトデータ
            filename (str): ファイル名
        
        Returns:
            str: 保存されたファイルパス
        """
        # 出力設定の取得
        default_dir = self.output_settings.get('default_directory', 'projects')
        encoding = self.output_settings.get('file_encoding', 'utf-8')
        include_index = self.output_settings.get('include_index', False)
        
        # ディレクトリの作成
        os.makedirs(default_dir, exist_ok=True)
        
        # ファイルパスの作成
        filepath = os.path.join(default_dir, filename)
        if not filepath.endswith('.csv'):
            filepath += '.csv'
        
        # CSV保存
        df = pd.DataFrame(projects)
        df.to_csv(filepath, index=include_index, encoding=encoding)
        return f"CSV file saved: {filepath}"

    def get_data_summary(self, projects: List[Dict]) -> Dict:
        """
        データ概要の取得
        
        Args:
            projects (List[Dict]): プロジェクトデータ
        
        Returns:
            Dict: データ概要
        """
        df = pd.DataFrame(projects)
        
        summary = {
            'total_projects': len(projects),
            'categories': df['category'].value_counts().to_dict(),
            'departments': df['department'].value_counts().to_dict(),
            'complexity_distribution': df['complexity'].value_counts().to_dict(),
            'budget_stats': {
                'min': int(df['budget'].min()),
                'max': int(df['budget'].max()),
                'mean': round(df['budget'].mean(), 2),
                'median': float(df['budget'].median())
            },
            'roi_stats': {
                'min': int(df['roi'].min()),
                'max': int(df['roi'].max()),
                'mean': round(df['roi'].mean(), 2),
                'median': float(df['roi'].median())
            },
            'duration_stats': {
                'min': int(df['duration'].min()),
                'max': int(df['duration'].max()),
                'mean': round(df['duration'].mean(), 2),
                'median': float(df['duration'].median())
            }
        }
        
        return summary

    def print_summary(self, projects: List[Dict]):
        """
        データ概要の表示
        
        Args:
            projects (List[Dict]): プロジェクトデータ
        """
        summary = self.get_data_summary(projects)
        
        print("\n" + "="*60)
        print("PROJECT DATA SUMMARY")
        print("="*60)
        print(f"Total Projects: {summary['total_projects']}")
        
        print("\nCategory Distribution:")
        for category, count in summary['categories'].items():
            print(f"  {category.replace('_', ' ')}: {count}")
        
        print("\nDepartment Distribution:")
        for dept, count in summary['departments'].items():
            print(f"  {dept}: {count}")
        
        print("\nComplexity Distribution:")
        for complexity, count in summary['complexity_distribution'].items():
            print(f"  {complexity}: {count}")
        
        print(f"\nBudget Statistics (Million Yen):")
        print(f"  Range: {summary['budget_stats']['min']} - {summary['budget_stats']['max']}")
        print(f"  Mean: {summary['budget_stats']['mean']}, Median: {summary['budget_stats']['median']}")
        
        print(f"\nROI Statistics (%):")
        print(f"  Range: {summary['roi_stats']['min']} - {summary['roi_stats']['max']}")
        print(f"  Mean: {summary['roi_stats']['mean']}, Median: {summary['roi_stats']['median']}")
        
        print(f"\nDuration Statistics (Months):")
        print(f"  Range: {summary['duration_stats']['min']} - {summary['duration_stats']['max']}")
        print(f"  Mean: {summary['duration_stats']['mean']}, Median: {summary['duration_stats']['median']}")
        print("="*60)

    def get_available_industries(self) -> List[str]:
        """利用可能な業界一覧を取得"""
        return list(self.industry_modifiers.keys())

    def get_available_categories(self) -> List[str]:
        """利用可能なカテゴリー一覧を取得"""
        return list(self.project_categories.keys())

    def get_config_info(self) -> Dict[str, Any]:
        """現在の設定情報を取得"""
        return {
            'categories_count': len(self.project_categories),
            'industries_count': len(self.industry_modifiers),
            'departments_count': len(self.departments),
            'signal_items_count': len(self.signal_options),
            'available_industries': self.get_available_industries(),
            'available_categories': self.get_available_categories()
        }