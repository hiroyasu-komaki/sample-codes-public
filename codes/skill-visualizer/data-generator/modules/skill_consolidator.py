"""
スキルデータ統合モジュール
分割されたCSVファイルを統合して1つのファイルにまとめる
"""

import os
import pandas as pd
from pathlib import Path


class SkillConsolidator:
    """分割されたスキル標準CSVファイルを統合するクラス"""
    
    def __init__(self, input_dir='output', output_dir='output2'):
        """
        初期化
        
        Args:
            input_dir (str): 入力ディレクトリのパス
            output_dir (str): 出力ディレクトリのパス
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.consolidated_df = None
        
    def consolidate_csv_files(self):
        """
        入力ディレクトリ内の全CSVファイルを統合
        
        Returns:
            pd.DataFrame: 統合されたDataFrame
        """
        # 入力ディレクトリの存在確認
        if not os.path.exists(self.input_dir):
            raise FileNotFoundError(f"入力ディレクトリが見つかりません: {self.input_dir}")
        
        # CSVファイルを取得
        csv_files = [f for f in os.listdir(self.input_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise FileNotFoundError(f"CSVファイルが見つかりません: {self.input_dir}")
        
        print(f"📁 Found {len(csv_files)} CSV files")
        
        # データフレームリスト
        df_list = []
        
        # 各CSVファイルを読み込み
        for csv_file in csv_files:
            file_path = os.path.join(self.input_dir, csv_file)
            
            try:
                # CSVファイルを読み込み
                df = pd.read_csv(file_path, encoding='utf-8')
                
                # ファイル名カラムを追加
                df['ファイル名'] = csv_file
                
                df_list.append(df)
                print(f"   ✓ Loaded: {csv_file} ({len(df)} rows)")
                
            except Exception as e:
                print(f"   ✗ Error loading {csv_file}: {e}")
                continue
        
        # 全データフレームを統合
        if df_list:
            self.consolidated_df = pd.concat(df_list, ignore_index=True)
            print(f"\n✅ Consolidated {len(df_list)} files into {len(self.consolidated_df)} rows")
        else:
            raise ValueError("統合可能なデータがありません")
        
        return self.consolidated_df
    
    def save_consolidated_csv(self, output_filename='consolidated_skill_data.csv'):
        """
        統合されたデータをCSVファイルとして保存
        
        Args:
            output_filename (str): 出力ファイル名
            
        Returns:
            str: 出力ファイルのパス
        """
        if self.consolidated_df is None:
            raise ValueError("統合データがありません。先にconsolidate_csv_files()を実行してください")
        
        # 出力ディレクトリが存在しない場合は作成
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📂 Created output directory: {self.output_dir}")
        
        # 出力パス
        output_path = os.path.join(self.output_dir, output_filename)
        
        # カラムの順序を指定
        column_order = [
            'カテゴリー',
            'サブカテゴリー',
            'スキル項目',
            'ロール',
            '専門性',
            'スキルレベル',
            'スキルレベル_数値',
            'ファイル名'
        ]
        
        # カラムの存在確認と並び替え
        existing_columns = [col for col in column_order if col in self.consolidated_df.columns]
        self.consolidated_df = self.consolidated_df[existing_columns]
        
        # CSVファイルとして保存
        self.consolidated_df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"💾 Saved consolidated CSV: {output_path}")
        
        return output_path
    
    def get_summary(self):
        """
        統合データの概要情報を取得
        
        Returns:
            dict: 統合データの概要
        """
        if self.consolidated_df is None:
            return None
        
        return {
            'total_rows': len(self.consolidated_df),
            'total_columns': len(self.consolidated_df.columns),
            'columns': list(self.consolidated_df.columns),
            'unique_files': self.consolidated_df['ファイル名'].nunique() if 'ファイル名' in self.consolidated_df.columns else 0,
            'unique_roles': self.consolidated_df['ロール'].nunique() if 'ロール' in self.consolidated_df.columns else 0,
            'unique_specialities': self.consolidated_df['専門性'].nunique() if '専門性' in self.consolidated_df.columns else 0,
            'unique_skills': self.consolidated_df['スキル項目'].nunique() if 'スキル項目' in self.consolidated_df.columns else 0,
        }
    
    def validate_consolidated_data(self):
        """
        統合データの検証
        
        Returns:
            bool: 検証結果（True: 正常, False: 異常）
        """
        if self.consolidated_df is None:
            print("❌ Error: No consolidated data to validate")
            return False
        
        try:
            # 必須カラムの存在チェック
            required_columns = [
                'カテゴリー', 'サブカテゴリー', 'スキル項目',
                'ロール', '専門性', 'スキルレベル', 'スキルレベル_数値', 'ファイル名'
            ]
            
            missing_columns = [col for col in required_columns if col not in self.consolidated_df.columns]
            if missing_columns:
                print(f"❌ Error: Missing columns: {missing_columns}")
                return False
            
            # NULL値のチェック
            if self.consolidated_df.isnull().any().any():
                null_counts = self.consolidated_df.isnull().sum()
                null_columns = null_counts[null_counts > 0]
                print(f"⚠️  Warning: Found NULL values:")
                for col, count in null_columns.items():
                    print(f"   - {col}: {count} nulls")
                return False
            
            # スキルレベルの値チェック
            valid_levels = {'a', 'b', 'c', 'd', 'z'}
            if 'スキルレベル' in self.consolidated_df.columns:
                invalid_levels = set(self.consolidated_df['スキルレベル'].unique()) - valid_levels
                if invalid_levels:
                    print(f"❌ Error: Invalid skill level values found: {invalid_levels}")
                    return False
            
            print("✅ Data validation passed!")
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {str(e)}")
            return False


def main():
    """メイン実行関数"""
    try:
        print("="*60)
        print("🔗 Skill Data Consolidator")
        print("="*60)
        print("Starting consolidation process...\n")
        
        # コンソリデーターの初期化
        consolidator = SkillConsolidator(input_dir='output', output_dir='output2')
        
        # CSVファイルを統合
        print("🔄 Consolidating CSV files...")
        df = consolidator.consolidate_csv_files()
        
        # 統合データの検証
        print("\n🔍 Data Validation:")
        consolidator.validate_consolidated_data()
        
        # 統合CSVファイルを保存
        print("\n💾 Saving consolidated CSV...")
        output_path = consolidator.save_consolidated_csv('consolidated_skill_data.csv')
        
        # サマリー表示
        summary = consolidator.get_summary()
        print("\n📊 Consolidation Summary:")
        print(f"   - Total rows: {summary['total_rows']}")
        print(f"   - Total columns: {summary['total_columns']}")
        print(f"   - Source files: {summary['unique_files']}")
        print(f"   - Unique roles: {summary['unique_roles']}")
        print(f"   - Unique specialities: {summary['unique_specialities']}")
        print(f"   - Unique skills: {summary['unique_skills']}")
        print(f"   - File size: {os.path.getsize(output_path):,} bytes")
        
        print("\n" + "="*60)
        print("✨ Consolidation completed successfully!")
        print("="*60)
        
        # サンプルデータの表示
        print("\n📄 Sample data (first 5 rows):")
        print(df.head())
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
