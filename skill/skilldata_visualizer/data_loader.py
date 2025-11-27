"""
データローダーモジュール

CSVファイルの読み込み、データの前処理、検証を担当
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any


class DataLoader:
    """スキルデータCSVファイルの読み込みと前処理を担当するクラス"""
    
    def __init__(self, filepath: str):
        """
        Args:
            filepath (str): CSVファイルのパス
        """
        self.filepath = Path(filepath)
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """
        CSVファイルを読み込んでDataFrameを返す
        
        Returns:
            pd.DataFrame: 読み込んだデータ、失敗時はNone
        """
        try:
            # CSVファイル読み込み
            self.df = pd.read_csv(
                self.filepath, 
                encoding='utf-8',
                na_values=['', 'NaN', 'null', 'NULL']
            )
            
            # 基本情報を記録
            self.metadata = {
                'filepath': str(self.filepath),
                'file_size': self.filepath.stat().st_size,
                'shape': self.df.shape,
                'columns': list(self.df.columns),
                'dtypes': dict(self.df.dtypes),
                'memory_usage': self.df.memory_usage(deep=True).sum()
            }
            
            # データ検証
            if not self._validate_data():
                return None
            
            # データ前処理
            self._preprocess_data()
            
            return self.df
            
        except FileNotFoundError:
            print(f"エラー: ファイルが見つかりません: {self.filepath}")
            return None
        except pd.errors.EmptyDataError:
            print(f"エラー: ファイルが空です: {self.filepath}")
            return None
        except pd.errors.ParserError as e:
            print(f"エラー: CSVファイルの解析エラー: {e}")
            return None
        except Exception as e:
            print(f"エラー: データ読み込みエラー: {e}")
            return None
    
    def _validate_data(self) -> bool:
        """
        データの妥当性を検証
        
        Returns:
            bool: 検証結果
        """
        if self.df is None or self.df.empty:
            print("エラー: データが空です")
            return False
        
        # 必要なカラムの存在確認
        required_columns = [
            'カテゴリー', 'サブカテゴリー', 'スキル項目', 
            'ロール', '専門性', 'スキルレベル', 'スキルレベル_数値'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            print(f"エラー: 必要なカラムが不足: {missing_columns}")
            return False
        
        # データ型チェック（警告レベルのメッセージは削除）
        if not pd.api.types.is_numeric_dtype(self.df['スキルレベル_数値']):
            pass  # 後続の前処理で変換するため警告不要
        
        return True
    
    def _preprocess_data(self):
        """データの前処理"""
        
        # 文字列カラムの空白除去
        string_columns = self.df.select_dtypes(include=['object']).columns
        for col in string_columns:
            self.df[col] = self.df[col].astype(str).str.strip()
        
        # スキルレベル_数値の型変換
        if not pd.api.types.is_numeric_dtype(self.df['スキルレベル_数値']):
            self.df['スキルレベル_数値'] = pd.to_numeric(
                self.df['スキルレベル_数値'], 
                errors='coerce'
            )
        
        # 重複行の確認と処理
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            self.df = self.df.drop_duplicates()
        
        # 欠損値の確認（エラーレベルのみ表示）
        missing_values = self.df.isnull().sum()
        if missing_values.sum() > 0:
            critical_missing = missing_values[missing_values > 0]
            if len(critical_missing) > 0:
                print(f"警告: 欠損値を検出しました（合計: {missing_values.sum()}件）")
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        データの概要情報を取得
        
        Returns:
            Dict[str, Any]: データ概要情報
        """
        if self.df is None:
            return {}
        
        summary = {
            'basic_info': {
                'shape': self.df.shape,
                'columns': list(self.df.columns),
                'memory_usage_mb': round(self.df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            },
            'categorical_stats': {},
            'numerical_stats': {},
            'missing_values': dict(self.df.isnull().sum())
        }
        
        # カテゴリカル変数の統計
        categorical_cols = ['カテゴリー', 'サブカテゴリー', '専門性', 'スキルレベル', 'ロール', 'ファイル名']
        for col in categorical_cols:
            if col in self.df.columns:
                summary['categorical_stats'][col] = {
                    'unique_count': self.df[col].nunique(),
                    'top_values': dict(self.df[col].value_counts().head(3))
                }
        
        # 数値変数の統計
        if 'スキルレベル_数値' in self.df.columns:
            summary['numerical_stats']['スキルレベル_数値'] = {
                'mean': round(self.df['スキルレベル_数値'].mean(), 2),
                'std': round(self.df['スキルレベル_数値'].std(), 2),
                'min': self.df['スキルレベル_数値'].min(),
                'max': self.df['スキルレベル_数値'].max(),
                'median': self.df['スキルレベル_数値'].median()
            }
        
        return summary
    
    def filter_data(self, **filters) -> pd.DataFrame:
        """
        データをフィルタリング
        
        Args:
            **filters: フィルタ条件 (カラム名=値)
            
        Returns:
            pd.DataFrame: フィルタリング後のデータ
        """
        if self.df is None:
            return pd.DataFrame()
        
        filtered_df = self.df.copy()
        
        for column, value in filters.items():
            if column in filtered_df.columns:
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[column].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
    
    def get_unique_values(self, column: str) -> list:
        """
        指定カラムのユニークな値を取得
        
        Args:
            column (str): カラム名
            
        Returns:
            list: ユニークな値のリスト
        """
        if self.df is None or column not in self.df.columns:
            return []
        
        return sorted(self.df[column].dropna().unique().tolist())
