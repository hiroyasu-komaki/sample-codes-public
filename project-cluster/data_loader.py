#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
from typing import List, Dict, Optional
import glob
import logging
from pathlib import Path

class DataLoader:
    """プロジェクトデータ読み込みクラス"""
    
    def __init__(self, data_directory: str = "projects"):
        """
        初期化
        
        Args:
            data_directory (str): データディレクトリのパス
        """
        self.data_directory = data_directory
        self._setup_logging()
        
    def _setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_all_csv_files(self) -> pd.DataFrame:
        """
        projectsフォルダ内のすべてのCSVファイルを読み込み統合
        
        Returns:
            pd.DataFrame: 統合されたプロジェクトデータ
        """
        if not os.path.exists(self.data_directory):
            raise FileNotFoundError(f"データディレクトリが見つかりません: {self.data_directory}")
        
        # CSVファイルのパスを取得
        csv_pattern = os.path.join(self.data_directory, "*.csv")
        csv_files = glob.glob(csv_pattern)
        
        if not csv_files:
            raise FileNotFoundError(f"CSVファイルが見つかりません: {self.data_directory}")
        
        self.logger.info(f"発見されたCSVファイル数: {len(csv_files)}")
        
        # 全CSVファイルを読み込み
        dataframes = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8')
                
                # ファイル名から業界情報を抽出（sample_projects_healthcare.csv -> healthcare）
                filename = Path(csv_file).stem
                if 'sample_projects_' in filename:
                    industry = filename.replace('sample_projects_', '').title()
                    df['source_industry'] = industry
                else:
                    df['source_industry'] = 'Unknown'
                
                df['source_file'] = Path(csv_file).name
                dataframes.append(df)
                
                self.logger.info(f"読み込み完了: {csv_file} ({len(df)} レコード)")
                
            except Exception as e:
                self.logger.error(f"ファイル読み込みエラー: {csv_file} - {e}")
                continue
        
        if not dataframes:
            raise ValueError("読み込み可能なCSVファイルがありません")
        
        # DataFrameを統合
        combined_df = pd.concat(dataframes, ignore_index=True)
        self.logger.info(f"統合データ: {len(combined_df)} レコード, {len(combined_df.columns)} カラム")
        
        return combined_df
    
    def load_specific_files(self, file_patterns: List[str]) -> pd.DataFrame:
        """
        指定されたパターンのファイルのみを読み込み
        
        Args:
            file_patterns (List[str]): ファイルパターンのリスト（例: ['*healthcare*', '*finance*']）
        
        Returns:
            pd.DataFrame: 統合されたプロジェクトデータ
        """
        dataframes = []
        
        for pattern in file_patterns:
            csv_pattern = os.path.join(self.data_directory, f"{pattern}.csv")
            csv_files = glob.glob(csv_pattern)
            
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file, encoding='utf-8')
                    
                    # ファイル名から業界情報を抽出
                    filename = Path(csv_file).stem
                    if 'sample_projects_' in filename:
                        industry = filename.replace('sample_projects_', '').title()
                        df['source_industry'] = industry
                    else:
                        df['source_industry'] = 'Unknown'
                    
                    df['source_file'] = Path(csv_file).name
                    dataframes.append(df)
                    
                    self.logger.info(f"読み込み完了: {csv_file} ({len(df)} レコード)")
                    
                except Exception as e:
                    self.logger.error(f"ファイル読み込みエラー: {csv_file} - {e}")
                    continue
        
        if not dataframes:
            raise ValueError("指定されたパターンに一致するファイルが見つかりません")
        
        combined_df = pd.concat(dataframes, ignore_index=True)
        self.logger.info(f"統合データ: {len(combined_df)} レコード")
        
        return combined_df
    
    def get_data_info(self, df: pd.DataFrame) -> Dict:
        """
        データ情報の取得
        
        Args:
            df (pd.DataFrame): プロジェクトデータ
        
        Returns:
            Dict: データ情報
        """
        info = {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict(),
        }
        
        # 業界別の分布
        if 'source_industry' in df.columns:
            info['industry_distribution'] = df['source_industry'].value_counts().to_dict()
        
        # カテゴリー別の分布
        if 'category' in df.columns:
            info['category_distribution'] = df['category'].value_counts().to_dict()
        
        # 部門別の分布
        if 'department' in df.columns:
            info['department_distribution'] = df['department'].value_counts().to_dict()
        
        return info
    
    def print_data_summary(self, df: pd.DataFrame):
        """
        データ概要の表示
        
        Args:
            df (pd.DataFrame): プロジェクトデータ
        """
        info = self.get_data_info(df)
        
        print("\n" + "="*70)
        print("DATA LOADING SUMMARY")
        print("="*70)
        print(f"Total Records: {info['total_records']}")
        print(f"Total Columns: {info['total_columns']}")
        
        if 'industry_distribution' in info:
            print("\nIndustry Distribution:")
            for industry, count in info['industry_distribution'].items():
                print(f"  {industry}: {count}")
        
        if 'category_distribution' in info:
            print("\nCategory Distribution:")
            for category, count in info['category_distribution'].items():
                print(f"  {category.replace('_', ' ')}: {count}")
        
        print("\nMissing Values:")
        missing_values = {k: v for k, v in info['missing_values'].items() if v > 0}
        if missing_values:
            for column, count in missing_values.items():
                print(f"  {column}: {count}")
        else:
            print("  なし")
        
        print(f"\nColumns: {', '.join(info['columns'][:10])}{'...' if len(info['columns']) > 10 else ''}")
        print("="*70)
    
    def validate_data_structure(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        データ構造の検証
        
        Args:
            df (pd.DataFrame): プロジェクトデータ
        
        Returns:
            Dict[str, bool]: 検証結果
        """
        validation_results = {}
        
        # 必須カラムの確認
        required_basic_columns = [
            'project_id', 'project_name', 'category', 'start_date', 'department'
        ]
        
        required_portfolio_columns = [
            'strategic_alignment', 'risk', 'urgency', 'importance',
            'budget', 'duration', 'roi', 'stakeholders', 'complexity'
        ]
        
        required_signal_columns = [
            'system_database_access', 'technology_stack', 'middleware_library',
            'vendor_partner', 'skill_set', 'procurement_contract',
            'master_data', 'end_user', 'launch_timing', 'regulatory_deadline'
        ]
        
        # 基本属性の検証
        validation_results['basic_attributes_complete'] = all(
            col in df.columns for col in required_basic_columns
        )
        
        # ポートフォリオ属性の検証
        validation_results['portfolio_attributes_complete'] = all(
            col in df.columns for col in required_portfolio_columns
        )
        
        # シグナル属性の検証
        validation_results['signal_attributes_complete'] = all(
            col in df.columns for col in required_signal_columns
        )
        
        # データ型の検証
        validation_results['valid_data_types'] = True
        try:
            # 数値カラムの確認
            numeric_columns = ['strategic_alignment', 'risk', 'urgency', 'importance',
                             'budget', 'duration', 'roi', 'stakeholders']
            for col in numeric_columns:
                if col in df.columns:
                    pd.to_numeric(df[col], errors='raise')
        except:
            validation_results['valid_data_types'] = False
        
        # 重複データの確認
        validation_results['no_duplicates'] = not df['project_id'].duplicated().any()
        
        return validation_results
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        データのクリーニング
        
        Args:
            df (pd.DataFrame): 元のデータ
        
        Returns:
            pd.DataFrame: クリーニング後のデータ
        """
        cleaned_df = df.copy()
        
        # 重複行の削除
        initial_count = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates(subset=['project_id'])
        
        if len(cleaned_df) < initial_count:
            self.logger.warning(f"重複行を削除: {initial_count - len(cleaned_df)}行")
        
        # 数値カラムの型変換
        numeric_columns = ['strategic_alignment', 'risk', 'urgency', 'importance',
                          'budget', 'duration', 'roi', 'stakeholders']
        
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        
        # 欠損値の処理（基本的には警告のみ）
        missing_count = cleaned_df.isnull().sum().sum()
        if missing_count > 0:
            self.logger.warning(f"欠損値が検出されました: {missing_count}個")
        
        return cleaned_df

# 使用例とテスト用の関数
def test_data_loader():
    """データローダーのテスト"""
    try:
        loader = DataLoader()
        
        # 全CSVファイルの読み込み
        df = loader.load_all_csv_files()
        
        # データ概要の表示
        loader.print_data_summary(df)
        
        # データ構造の検証
        validation = loader.validate_data_structure(df)
        print("\nValidation Results:")
        for key, result in validation.items():
            status = "✓" if result else "✗"
            print(f"  {status} {key}: {result}")
        
        # データクリーニング
        cleaned_df = loader.clean_data(df)
        print(f"\nData cleaning completed: {len(cleaned_df)} records")
        
        return cleaned_df
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        return None

if __name__ == "__main__":
    test_data_loader()