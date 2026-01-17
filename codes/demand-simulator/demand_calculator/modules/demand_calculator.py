"""
IT人材需要計算 - 需要計算クラス

プロジェクトデータから各ケイパビリティ別の人材需要を計算します。
"""

import pandas as pd
import yaml
import json
from pathlib import Path
from typing import Dict, Tuple


class DemandCalculator:
    """IT人材需要計算クラス"""
    
    def __init__(self, 
                 config_path: str = 'config/calc_assumptions.yaml',
                 keywords_path: str = 'config/keywords.json'):
        """
        初期化
        
        Args:
            config_path: YAML設定ファイルのパス
            keywords_path: JSONキーワードファイルのパス（必須）
        """
        # YAML設定ファイルを読み込み
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # JSONキーワードファイルを読み込み（必須）
        with open(keywords_path, 'r', encoding='utf-8') as f:
            keywords_data = json.load(f)
        
        # キーワード定義をJSONから取得
        self.tech_keywords = keywords_data['tech_area_keywords']
        self.project_keywords = keywords_data['project_type_keywords']
        
        # その他の設定はYAMLから取得
        self.size_thresholds = self.config['project_size_thresholds']
        self.skill_distribution = self.config['skill_distribution']
        self.operation_params = self.config['operation_parameters']
        self.investment_params = self.config['investment_to_person_months']
    
    def process_csv_file_classify(self, input_path: Path, output_path: Path):
        """
        ステップ1: プロジェクト分類処理
        
        CSVファイルを読み込み、プロジェクト規模・種別・技術領域を判定して
        中間ファイルとして保存します。
        
        Args:
            input_path: 入力CSVファイルのパス
            output_path: 出力CSVファイルのパス（中間ファイル）
        """
        print(f"\n処理中: {input_path.name}")
        print("-" * 80)
        
        # CSVファイルを読み込み
        df = pd.read_csv(input_path, encoding='utf-8-sig')
        
        print(f"  読み込み: {len(df)}件のプロジェクト")
        
        # 各プロジェクトを分類
        classifications = []
        for idx, row in df.iterrows():
            project_name = row.get('案件名', '')
            investment = row.get('初期投資金額', 0)
            
            # プロジェクト規模を判定
            size = self._classify_project_size(investment)
            
            # プロジェクト種別を判定
            project_type = self._classify_project_type(project_name)
            
            # 技術領域を判定
            tech_area = self._classify_tech_area(project_name)
            
            classifications.append({
                'プロジェクト規模': size,
                'プロジェクト種別': project_type,
                '技術領域': tech_area
            })
        
        # 分類結果を元のDataFrameに追加
        classification_df = pd.DataFrame(classifications)
        result_df = pd.concat([df, classification_df], axis=1)
        
        # 中間ファイルとして保存
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"  分類完了: {output_path.name}")
        print(f"    - 規模分布: {classification_df['プロジェクト規模'].value_counts().to_dict()}")
        print(f"    - 種別分布: {classification_df['プロジェクト種別'].value_counts().to_dict()}")
        print(f"    - 技術領域: {classification_df['技術領域'].value_counts().to_dict()}")
    
    def process_csv_file_demand(self, input_path: Path, output_path: Path):
        """
        ステップ2: スキル需要計算
        
        分類済みCSVファイルを読み込み、ケイパビリティ別の需要を計算して
        最終結果として保存します。
        
        Args:
            input_path: 入力CSVファイルのパス（分類済み中間ファイル）
            output_path: 出力CSVファイルのパス（最終結果）
        """
        print(f"\n処理中: {input_path.name}")
        print("-" * 80)
        
        # 分類済みCSVファイルを読み込み
        df = pd.read_csv(input_path, encoding='utf-8-sig')
        
        print(f"  読み込み: {len(df)}件のプロジェクト")
        
        # 各プロジェクトの需要を計算
        demands = []
        for idx, row in df.iterrows():
            # 開発需要を計算
            dev_demand = self._calculate_development_demand(row)
            
            # 運用需要を計算
            ops_demand = self._calculate_operation_demand(row)
            
            demands.append({
                **dev_demand,
                **ops_demand
            })
        
        # 需要計算結果を元のDataFrameに追加
        demand_df = pd.DataFrame(demands)
        result_df = pd.concat([df, demand_df], axis=1)
        
        # 最終結果として保存
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"  需要計算完了: {output_path.name}")
        
        # 集計情報を表示
        total_dev_demand = sum([
            demand_df['開発_ビジネスケイパビリティ(人月)'].sum(),
            demand_df['開発_デリバリケイパビリティ(人月)'].sum(),
            demand_df['開発_テクニカルケイパビリティ(人月)'].sum(),
            demand_df['開発_リーダーシップケイパビリティ(人月)'].sum()
        ])
        total_ops_demand = sum([
            demand_df['運用_ビジネスケイパビリティ(人月)'].sum(),
            demand_df['運用_デリバリケイパビリティ(人月)'].sum(),
            demand_df['運用_テクニカルケイパビリティ(人月)'].sum(),
            demand_df['運用_リーダーシップケイパビリティ(人月)'].sum()
        ])
        
        print(f"    - 開発需要合計: {total_dev_demand:.1f} 人月")
        print(f"    - 運用需要合計: {total_ops_demand:.1f} 人月")
    
    def _classify_project_size(self, investment: float) -> str:
        """
        プロジェクト規模を判定
        
        Args:
            investment: 初期投資金額（千円）
            
        Returns:
            プロジェクト規模（large/medium/small/extra_small）
        """
        # 投資金額から推定人月を計算
        person_months = self._investment_to_person_months(investment)
        
        # 閾値と比較して規模を判定
        if person_months >= self.size_thresholds['large']['min_person_months']:
            return 'large'
        elif person_months >= self.size_thresholds['medium']['min_person_months']:
            return 'medium'
        elif person_months >= self.size_thresholds['small']['min_person_months']:
            return 'small'
        else:
            return 'extra_small'
    
    def _classify_project_type(self, project_name: str) -> str:
        """
        プロジェクト種別を判定（JSONキーワードを使用）
        
        Args:
            project_name: 案件名
            
        Returns:
            プロジェクト種別（新規開発/導入/刷新/移行/その他）
        """
        project_name = str(project_name)
        
        # JSONから読み込んだキーワードでマッチング
        for project_type, keywords in self.project_keywords.items():
            for keyword in keywords:
                if keyword == 'default':
                    continue
                if keyword in project_name:
                    return project_type
        
        # マッチしない場合はデフォルト
        return 'その他'
    
    def _classify_tech_area(self, project_name: str) -> str:
        """
        技術領域を判定（JSONキーワードを使用）
        
        Args:
            project_name: 案件名
            
        Returns:
            技術領域（AI/ML/クラウド/DX・デジタル/従来型）
        """
        project_name = str(project_name)
        
        # JSONから読み込んだキーワードでマッチング
        for tech_area, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword == 'default':
                    continue
                if keyword in project_name:
                    return tech_area
        
        # マッチしない場合はデフォルト
        return '従来型'
    
    def _investment_to_person_months(self, investment: float) -> float:
        """
        投資金額から推定人月を計算
        
        Args:
            investment: 初期投資金額（千円）
            
        Returns:
            推定人月
        """
        labor_cost = investment * self.investment_params['labor_cost_ratio']
        total_person_months = labor_cost / self.investment_params['average_unit_cost']
        in_house_person_months = total_person_months * self.investment_params['in_house_ratio']
        
        return in_house_person_months
    
    def _get_skill_distribution(self, size: str, project_type: str) -> Dict[str, float]:
        """
        スキル配分比率を取得
        
        Args:
            size: プロジェクト規模
            project_type: プロジェクト種別
            
        Returns:
            スキル配分比率の辞書
        """
        key = f"{size}_{project_type}"
        
        if key in self.skill_distribution:
            return self.skill_distribution[key]
        else:
            # デフォルトの配分比率（その他）
            default_key = f"{size}_その他"
            return self.skill_distribution.get(default_key, {
                "ビジネスケイパビリティ": 0.25,
                "デリバリケイパビリティ": 0.25,
                "テクニカルケイパビリティ": 0.40,
                "リーダーシップケイパビリティ": 0.10
            })
    
    def _calculate_development_demand(self, row: pd.Series) -> Dict[str, float]:
        """
        開発需要を計算
        
        Args:
            row: プロジェクトデータの行
            
        Returns:
            ケイパビリティ別の開発需要（人月）
        """
        investment = row.get('初期投資金額', 0)
        size = row.get('プロジェクト規模', 'small')
        project_type = row.get('プロジェクト種別', 'その他')
        
        # 総人月を計算
        total_person_months = self._investment_to_person_months(investment)
        
        # スキル配分比率を取得
        distribution = self._get_skill_distribution(size, project_type)
        
        # 各ケイパビリティの需要を計算
        return {
            '開発_ビジネスケイパビリティ(人月)': total_person_months * distribution.get('ビジネスケイパビリティ', 0),
            '開発_デリバリケイパビリティ(人月)': total_person_months * distribution.get('デリバリケイパビリティ', 0),
            '開発_テクニカルケイパビリティ(人月)': total_person_months * distribution.get('テクニカルケイパビリティ', 0),
            '開発_リーダーシップケイパビリティ(人月)': total_person_months * distribution.get('リーダーシップケイパビリティ', 0)
        }
    
    def _calculate_operation_demand(self, row: pd.Series) -> Dict[str, float]:
        """
        運用需要を計算
        
        Args:
            row: プロジェクトデータの行
            
        Returns:
            ケイパビリティ別の運用需要（人月）
        """
        operation_cost = row.get('運用費', 0)
        
        # 運用費から人月を計算
        labor_cost = operation_cost * self.operation_params['labor_cost_ratio']
        total_person_months = labor_cost / self.operation_params['average_unit_cost']
        
        # 運用フェーズのスキル配分比率（固定）
        # 運用は技術とデリバリが中心
        operation_distribution = {
            'ビジネスケイパビリティ': 0.10,
            'デリバリケイパビリティ': 0.30,
            'テクニカルケイパビリティ': 0.55,
            'リーダーシップケイパビリティ': 0.05
        }
        
        # 各ケイパビリティの需要を計算
        return {
            '運用_ビジネスケイパビリティ(人月)': total_person_months * operation_distribution['ビジネスケイパビリティ'],
            '運用_デリバリケイパビリティ(人月)': total_person_months * operation_distribution['デリバリケイパビリティ'],
            '運用_テクニカルケイパビリティ(人月)': total_person_months * operation_distribution['テクニカルケイパビリティ'],
            '運用_リーダーシップケイパビリティ(人月)': total_person_months * operation_distribution['リーダーシップケイパビリティ']
        }
