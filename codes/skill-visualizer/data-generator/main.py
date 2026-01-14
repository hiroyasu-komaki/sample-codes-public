"""
デジタルスキル標準システム - メインプログラム（インタラクティブ版）
エントリポイント - 実行モードを選択可能
"""

import os
import sys
from modules.skill_standard_processor import SkillStandardProcessor
from modules.skill_consolidator import SkillConsolidator


def create_skill_standard_csv_split(processor):
    """
    スキル標準CSVファイルをロール×専門性ごとに分割して生成
    
    Args:
        processor (SkillStandardProcessor): スキル標準プロセッサー
        
    Returns:
        tuple: (DataFrame, 出力ファイルリスト)
    """
    # データ処理
    df = processor.process_data()
    
    # outputディレクトリが存在しない場合は作成
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # ロールと専門性の組み合わせでグループ化して分割保存
    output_files = []
    
    for (role, speciality), group_df in df.groupby(['ロール', '専門性']):
        # ファイル名を生成（ロール_専門性.csv）
        # ファイル名に使えない文字を置換
        safe_role = role.replace('/', '_').replace('\\', '_')
        safe_speciality = speciality.replace('/', '_').replace('\\', '_')
        filename = f"{safe_role}_{safe_speciality}.csv"
        output_path = os.path.join(output_dir, filename)
        
        # CSVファイルとして保存
        group_df.to_csv(output_path, index=False, encoding='utf-8')
        output_files.append(output_path)
    
    return df, output_files


def run_data_generation():
    """データ生成処理を実行"""
    print("\n" + "="*60)
    print("📊 Mode 1: Data Generation")
    print("="*60)
    print("Starting CSV generation (split by Role & Speciality)...\n")
    
    # スキル標準プロセッサーの初期化
    print("📂 Initializing processor...")
    processor = SkillStandardProcessor()
    print("✅ Processor initialized\n")
    
    # データサマリーの表示
    summary = processor.get_data_summary()
    print("📊 Data Summary:")
    print(f"   - Roles: {summary['total_roles']}")
    print(f"   - Skills: {summary['total_skills']}")
    print(f"   - Specialities: {summary['total_specialities']}")
    print(f"   - Expected rows: {summary['expected_rows']}\n")
    
    # 分割CSV生成
    print("🔄 Generating split CSV files...")
    df, csv_files = create_skill_standard_csv_split(processor)
    print(f"✅ {len(csv_files)} CSV files created\n")
    
    # データ検証
    print("🔍 Data Validation:")
    if processor.validate_data(df):
        print()
    
    # 結果表示
    print("📋 Result:")
    print(f"   - Total rows: {len(df)}")
    print(f"   - Columns: {list(df.columns)}")
    print(f"   - Generated files: {len(csv_files)}\n")
    
    # 生成されたファイル一覧
    print("📁 Generated Files:")
    for i, file_path in enumerate(csv_files, 1):
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        print(f"   {i:2d}. {filename:<50} ({file_size:,} bytes)")
    
    print("\n" + "="*60)
    print("✨ Data generation completed successfully!")
    print("="*60)
    
    # サンプルデータの表示
    print("\n📄 Sample data (first 5 rows):")
    print(df.head())


def run_data_consolidation():
    """データ統合処理を実行"""
    print("\n" + "="*60)
    print("🔗 Mode 2: Data Consolidation")
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


def show_menu():
    """メニューを表示して選択肢を取得"""
    print("\n" + "="*60)
    print("🚀 Digital Skill Standard System")
    print("="*60)
    print("\nPlease select execution mode:")
    print("  1 - Data Generation only (split CSV files)")
    print("  2 - Data Consolidation only (merge CSV files)")
    print("  Enter - Both (Generation → Consolidation)")
    print("  q - Quit")
    print("-"*60)
    
    choice = input("Your choice: ").strip().lower()
    return choice


def main():
    """メイン実行関数"""
    try:
        # メニュー表示と選択
        choice = show_menu()
        
        if choice == 'q':
            print("\n👋 Exiting...")
            sys.exit(0)
        elif choice == '1':
            # データ生成のみ
            run_data_generation()
        elif choice == '2':
            # データ統合のみ
            run_data_consolidation()
        elif choice == '':
            # 両方実行
            print("\n🔄 Running both operations...")
            run_data_generation()
            print("\n" + "─"*60 + "\n")
            run_data_consolidation()
        else:
            print(f"\n⚠️  Invalid choice: '{choice}'")
            print("Please run again and select 1, 2, Enter, or q")
            sys.exit(1)
        
        print("\n" + "="*60)
        print("✅ All operations completed successfully!")
        print("="*60)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
