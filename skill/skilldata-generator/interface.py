"""
ユーザーインタラクション管理モジュール
スキル標準システムのユーザープロンプトと応答処理を担当
"""

from typing import List


class UserInterface:
    """
    ユーザーとのインタラクションを管理するクラス
    プロンプト表示、入力処理、結果表示などを担当
    """
    
    @staticmethod
    def confirm_csv_generation() -> bool:
        """
        スキル標準CSVファイル生成の確認プロンプトを表示
        
        Returns:
            bool: 生成する場合True、スキップする場合False
        """
        print("\n" + "="*60)
        print("🔧 Skill Standard CSV Generation")
        print("="*60)
        print("Do you want to generate skill_standard.csv?")
        print("(This file contains the base skill matrix - only needed once or when master data changes)")
        print("")
        
        while True:
            try:
                response = input("Generate skill_standard.csv? [y/N]: ").strip().lower()
                
                # 空入力はデフォルトでNo
                if not response:
                    return False
                
                # 肯定的な応答
                if response in ['y', 'yes']:
                    return True
                
                # 否定的な応答
                elif response in ['n', 'no']:
                    return False
                
                # 無効な入力
                else:
                    print("Please enter 'y' for yes or 'n' for no (default: n)")
                    continue
                    
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user.")
                return False
            except Exception as e:
                print(f"Error reading input: {str(e)}")
                return False
    
    @staticmethod
    def display_generation_summary(csv_generated: bool, csv_path: str = None, 
                                 sample_files: List[str] = None, consolidated_path: str = None):
        """
        ファイル生成結果のサマリーを表示
        
        Args:
            csv_generated (bool): CSVファイルが生成されたかどうか
            csv_path (str, optional): 生成されたCSVファイルのパス
            sample_files (List[str], optional): 生成されたサンプルファイルのリスト
            consolidated_path (str, optional): 統合ファイルのパス
        """
        print("\n" + "="*60)
        print("📊 Generation Summary")
        print("="*60)
        
        # メインCSVファイルの結果
        if csv_generated and csv_path:
            print(f"✅ Main CSV file created: {csv_path}")
        else:
            print("⏭️  Main CSV generation skipped")
        
        # サンプルファイルの結果
        if sample_files:
            print(f"✅ Sample data files created: {len(sample_files)} files")
            print(f"   📁 Location: output/samples/")
            print(f"   📄 Files: sample_001.csv ~ sample_{len(sample_files):03d}.csv")
        else:
            print("❌ No sample files generated")
        
        # 統合ファイルの結果
        if consolidated_path:
            print(f"✅ Consolidated data file created: {consolidated_path}")
            print(f"   📁 Contains all generated data in single file")
        else:
            print("⚠️  Data consolidation skipped or failed")
        
        # 総合結果
        total_files = (1 if csv_generated else 0) + (len(sample_files) if sample_files else 0) + (1 if consolidated_path else 0)
        print(f"\n📈 Total files generated: {total_files}")
        print("="*60)
    
    @staticmethod
    def display_sample_generation_progress(current: int, total: int, strategy_name: str):
        """
        サンプルデータ生成の進捗を表示
        
        Args:
            current (int): 現在の処理番号
            total (int): 総数
            strategy_name (str): 現在の戦略名
        """
        percentage = (current / total) * 100
        print(f"🔄 Generating sample {current:2d}/{total} ({percentage:5.1f}%) - {strategy_name}")
    
    @staticmethod
    def display_error(error_message: str):
        """
        エラーメッセージを表示
        
        Args:
            error_message (str): エラーメッセージ
        """
        print("\n" + "="*60)
        print("❌ Error")
        print("="*60)
        print(f"Error: {error_message}")
        print("="*60)
    
    @staticmethod
    def display_startup_message():
        """
        システム起動時のメッセージを表示
        """
        print("\n" + "="*60)
        print("🚀 Digital Skill Standard System")
        print("="*60)
        print("Starting data generation process...")
        print("")
    
    @staticmethod
    def display_completion_message():
        """
        処理完了時のメッセージを表示
        """
        print("\n✨ Process completed successfully!")
        print("You can now use the generated files for analysis and comparison.")
        print("")
