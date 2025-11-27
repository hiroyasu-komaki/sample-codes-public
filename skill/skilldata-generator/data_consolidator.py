"""
データ統合モジュール
サンプルデータを統合して1つのファイルにまとめる
"""

import os
import pandas as pd
from typing import List, Optional
from pathlib import Path


class DataConsolidator:
    """
    サンプルデータを統合するクラス
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        データ統合クラスを初期化
        
        Args:
            output_dir (str): 出力ディレクトリのパス
        """
        self.output_dir = output_dir
        self.samples_dir = os.path.join(output_dir, "samples")
    
    def consolidate_all_data(self) -> Optional[str]:
        """
        全サンプルデータを統合して1つのCSVファイルを作成
            
        Returns:
            Optional[str]: 統合ファイルのパス（失敗時はNone）
        """
        try:
            consolidated_data = []
            file_info = []
            
            # サンプルデータの読み込み
            sample_files = self._get_sample_files()
            for file_path in sample_files:
                source_name = self._extract_source_name(file_path)
                sample_df = self._load_csv_with_source(file_path, source_name)
                
                if sample_df is not None:
                    consolidated_data.append(sample_df)
                    file_info.append({
                        'source': source_name,
                        'file_name': os.path.basename(file_path),
                        'rows': len(sample_df)
                    })
            
            if not consolidated_data:
                print("❌ No data files found to consolidate")
                return None
            
            # データの統合
            consolidated_df = pd.concat(consolidated_data, ignore_index=True)
            
            # 統合ファイルの保存
            consolidated_path = os.path.join(self.output_dir, "consolidated_skill_data.csv")
            consolidated_df.to_csv(consolidated_path, index=False, encoding='utf-8')
            
            # 統合情報の表示
            self._display_consolidation_summary(file_info, consolidated_df, consolidated_path)
            
            return consolidated_path
            
        except Exception as e:
            print(f"❌ Error during data consolidation: {str(e)}")
            return None
    
    def _get_sample_files(self) -> List[str]:
        """
        サンプルファイルのパス一覧を取得
        
        Returns:
            List[str]: サンプルファイルパスのリスト
        """
        sample_files = []
        
        if not os.path.exists(self.samples_dir):
            return sample_files
        
        # CSVファイルのみを対象とし、番号順にソート
        for file_name in sorted(os.listdir(self.samples_dir)):
            if file_name.endswith('.csv'):
                file_path = os.path.join(self.samples_dir, file_name)
                sample_files.append(file_path)
        
        return sample_files
    
    def _load_csv_with_source(self, file_path: str, source_name: str) -> Optional[pd.DataFrame]:
        """
        CSVファイルを読み込み、ソース情報を追加
        
        Args:
            file_path (str): CSVファイルのパス
            source_name (str): ソース名
            
        Returns:
            Optional[pd.DataFrame]: 読み込んだデータ（失敗時はNone）
        """
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # ファイル名を最後の列として追加（拡張子除去）
            file_name = os.path.basename(file_path)
            file_name_without_ext = os.path.splitext(file_name)[0]
            df['ファイル名'] = file_name_without_ext
            
            return df
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to load {file_path}: {str(e)}")
            return None
    
    def _extract_source_name(self, file_path: str) -> str:
        """
        ファイルパスからソース名を抽出
        
        Args:
            file_path (str): ファイルパス
            
        Returns:
            str: ソース名
        """
        file_name = os.path.basename(file_path)
        
        # sample_XXX_strategy.csv の形式からstrategy部分を抽出
        if file_name.startswith('sample_') and file_name.endswith('.csv'):
            parts = file_name[:-4].split('_')  # .csvを除去して分割
            if len(parts) >= 3:
                # sample_001_engineer_focused -> engineer_focused
                strategy = '_'.join(parts[2:])
                return f"sample_{strategy}"
        
        # デフォルト
        return file_name[:-4] if file_name.endswith('.csv') else file_name
    
    def _display_consolidation_summary(self, file_info: List[dict], 
                                     consolidated_df: pd.DataFrame, 
                                     output_path: str):
        """
        統合結果のサマリーを表示
        
        Args:
            file_info (List[dict]): ファイル情報のリスト
            consolidated_df (pd.DataFrame): 統合データ
            output_path (str): 出力ファイルパス
        """
        print("\n" + "="*60)
        print("📊 Data Consolidation Summary")
        print("="*60)
        
        print(f"📁 Output file: {output_path}")
        print(f"📈 Total consolidated rows: {len(consolidated_df):,}")
        print(f"📄 Source files included: {len(file_info)}")
        
        print("\n📋 File breakdown:")
        for info in file_info:
            print(f"   • {info['file_name']}: {info['rows']:,} rows ({info['source']})")
        
        # データソース別の集計
        source_counts = consolidated_df['データソース'].value_counts()
        print("\n📊 Data distribution by source:")
        for source, count in source_counts.items():
            percentage = (count / len(consolidated_df)) * 100
            print(f"   • {source}: {count:,} rows ({percentage:.1f}%)")
        
        print("="*60)
    
    def validate_consolidated_data(self, consolidated_path: str) -> bool:
        """
        統合データの整合性を検証
        
        Args:
            consolidated_path (str): 統合ファイルのパス
            
        Returns:
            bool: 検証結果
        """
        try:
            df = pd.read_csv(consolidated_path, encoding='utf-8')
            
            # 必須列の存在確認
            required_columns = [
                'データソース', 'ファイル名', 'カテゴリー', 'サブカテゴリー', 
                'スキル項目', 'ロール', '専門性', 'スキルレベル', 'スキルレベル_数値'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            
            # NULL値のチェック
            if df[required_columns].isnull().any().any():
                print("❌ Found NULL values in required columns")
                return False
            
            # データソースの一意性チェック
            unique_sources = df['データソース'].nunique()
            if unique_sources < 1:  # サンプルデータが最低1つ
                print("❌ Insufficient data sources")
                return False
            
            print("✅ Consolidated data validation passed!")
            return True
            
        except Exception as e:
            print(f"❌ Error validating consolidated data: {str(e)}")
            return False