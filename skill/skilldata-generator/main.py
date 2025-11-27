import os
from skill_standard_processor import SkillStandardProcessor
from user_interface import UserInterface
from sample_data_generator import SampleDataGenerator
from data_consolidator import DataConsolidator


def create_skill_standard_csv(processor):
    """
    スキル標準CSVファイルを生成
    
    Args:
        processor (SkillStandardProcessor): スキル標準プロセッサー
        
    Returns:
        tuple: (DataFrame, 出力パス)
    """
    df = processor.process_data()
    
    # outputディレクトリが存在しない場合は作成
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # CSVファイルとして保存
    output_path = os.path.join(output_dir, 'skill_standard.csv')
    df.to_csv(output_path, index=False, encoding='utf-8')
    return df, output_path


def generate_sample_data(processor, num_samples=10):
    """
    サンプルデータを生成
    
    Args:
        processor (SkillStandardProcessor): スキル標準プロセッサー
        num_samples (int): 生成するサンプル数
        
    Returns:
        List[str]: 生成されたサンプルファイルのパスリスト
    """
    generator = SampleDataGenerator(processor)
    sample_files = generator.generate_samples(num_samples)
    return sample_files


def consolidate_all_data(csv_generated, sample_files):
    """
    全データを統合
    
    Args:
        csv_generated (bool): メインCSVが生成されたかどうか
        sample_files (List[str]): サンプルファイルのリスト
        
    Returns:
        Optional[str]: 統合ファイルのパス
    """
    consolidator = DataConsolidator()
    
    # 統合処理実行
    # consolidated_path = consolidator.consolidate_all_data(include_main_csv=csv_generated)
    consolidator.consolidate_all_data()
    
    if consolidated_path:
        # 統合データの検証
        consolidator.validate_consolidated_data(consolidated_path)
    
    return consolidated_path


def display_data_analysis(processor):
    """
    データ分析結果を表示
    
    Args:
        processor (SkillStandardProcessor): スキル標準プロセッサー
    """
    summary = processor.get_data_summary()
    
    print("\n" + "="*60)
    print("📈 Data Analysis Summary")
    print("="*60)
    print(f"- Total skills: {summary['skills']['total_skills']}")
    print(f"- Categories: {summary['skills']['category_count']}")
    print(f"- Subcategories: {summary['skills']['subcategory_count']}")
    print(f"- Total roles: {summary['master_data']['total_roles']}")
    print(f"- Total specialities: {summary['master_data']['total_specialities']}")
    print(f"- Expected total rows per file: {summary['expected_total_rows']}")
    print("="*60)


def main():
    """
    メイン実行関数
    """
    try:
        # システム起動メッセージ
        UserInterface.display_startup_message()
        
        # スキル標準プロセッサーの初期化
        processor = SkillStandardProcessor()
        
        # 機能2: ユーザープロンプト - skill_standard.csv生成確認
        csv_generated = False
        csv_path = None
        
        if UserInterface.confirm_csv_generation():
            try:
                df, csv_path = create_skill_standard_csv(processor)
                csv_generated = True
                print(f"✅ CSV file has been created successfully at: {csv_path}")
                
                # DataFrameの詳細情報を表示
                print("\nDataFrame info:")
                print(df.info())
                print(f"\nTotal number of rows: {len(df)}")
                print("\nSample of the DataFrame:")
                print(df.head())
                
            except Exception as e:
                UserInterface.display_error(f"Failed to generate main CSV: {str(e)}")
                csv_generated = False
        else:
            print("⏭️  Skipped skill_standard.csv generation")
        
        # 機能1: サンプルデータ生成（必ず実行）
        sample_files = []
        try:
            sample_files = generate_sample_data(processor, num_samples=10)
        except Exception as e:
            UserInterface.display_error(f"Failed to generate sample data: {str(e)}")
        
        # 機能3: データ統合（新機能）
        consolidated_path = None
        try:
            consolidated_path = consolidate_all_data(csv_generated, sample_files)
        except Exception as e:
            UserInterface.display_error(f"Failed to consolidate data: {str(e)}")
        
        # 結果サマリーの表示
        UserInterface.display_generation_summary(csv_generated, csv_path, sample_files, consolidated_path)
        
        # データ分析結果の表示
        display_data_analysis(processor)
        
        # データ検証（メインCSVが生成された場合のみ）
        if csv_generated:
            print("\n" + "="*60)
            print("🔍 Data Validation")
            print("="*60)
            if processor.validate_data(df):
                print("✅ All data validation passed!")
            else:
                print("❌ Data validation failed!")
        
        # 完了メッセージ
        UserInterface.display_completion_message()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        UserInterface.display_error(f"Unexpected error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
