#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
プロジェクトデータ生成メインスクリプト
YAML設定に従ってサンプルデータを自動生成し、分析を実行します
"""

import os
from project_data_generator import ProjectDataGenerator
from signal_analyzer import ProjectSignalAnalyzer
from portfolio_analyzer import ProjectPortfolioAnalyzer

def check_existing_data(data_directory: str = "projects") -> bool:
    """
    既存データの確認
    
    Args:
        data_directory (str): データディレクトリのパス
    
    Returns:
        bool: 既存データが存在するかどうか
    """
    if not os.path.exists(data_directory):
        return False
    
    csv_files = [f for f in os.listdir(data_directory) if f.endswith('.csv')]
    return len(csv_files) > 0

def confirm_data_generation() -> bool:
    """
    データ生成の実行確認
    
    Returns:
        bool: データ生成を実行するかどうか
    """
    existing_data = check_existing_data()
    
    if existing_data:
        print("\n⚠️  既存のプロジェクトデータが見つかりました")
        confirm = input("新しいサンプルデータを生成しますか？ (既存データは削除されます) (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            print("✅ 新しいデータを生成します")
            return True
        else:
            print("✅ 既存データを使用して分析を実行します")
            return False
    else:
        print("\n📝 プロジェクトデータが見つかりません")
        confirm = input("新しいサンプルデータを生成しますか？ (Y/n): ").strip().lower()
        
        if confirm in ['', 'y', 'yes']:
            print("✅ 新しいデータを生成します")
            return True
        else:
            print("❌ データが存在しないため、分析を実行できません")
            print("サンプルデータを生成するか、既存のCSVファイルをprojects/フォルダに配置してください")
            exit(1)

def cleanup_existing_data(data_directory: str = "projects"):
    """
    既存データのクリーンアップ
    
    Args:
        data_directory (str): データディレクトリのパス
    """
    if os.path.exists(data_directory):
        for filename in os.listdir(data_directory):
            if filename.endswith('.csv'):
                file_path = os.path.join(data_directory, filename)
                os.remove(file_path)
                print(f"🗑️  削除: {filename}")

def main():
    """メイン処理 - YAML設定に従ってデータを生成し、分析を実行"""
    
    try:
        print("="*60)
        print("🚀 PROJECT DATA GENERATOR & ANALYZER")
        print("="*60)
        
        # データ生成の実行確認
        should_generate = confirm_data_generation()
        
        if should_generate:
            # === データ生成フェーズ ===
            print("\n📝 Loading configuration from config.yaml...")
            generator = ProjectDataGenerator()
            print("✅ Configuration loaded successfully")
            
            # 既存データのクリーンアップ
            print("\n🧹 Cleaning up existing data...")
            cleanup_existing_data()
            
            print("\n🚀 Generating sample datasets for all industries...")
            datasets = generator.generate_sample_datasets()
            
            # 各業界のデータを保存
            total_projects = 0
            for industry, projects in datasets.items():
                filename = f"sample_projects_{industry.lower()}.csv"
                saved_path = generator.save_to_file(projects, filename)
                total_projects += len(projects)
                print(f"✅ {saved_path} ({len(projects)} projects)")
            
            print(f"\n📊 Total: {total_projects} projects across {len(datasets)} industries")
            
            # 最初の業界のサマリーを表示（例として）
            first_industry = list(datasets.keys())[0]
            print(f"\nSample summary for {first_industry}:")
            generator.print_summary(datasets[first_industry])
            
            print("\n✅ Sample data generation completed successfully!")
        
        else:
            print("\n📂 Using existing data for analysis...")
        
        # === 分析フェーズ ===
        print("\n" + "="*60)
        print("🔍 STARTING ANALYSIS PHASE")
        print("="*60)
        
        # ポートフォリオ分析の実行
        print("\n📈 Running Portfolio Analysis...")
        portfolio_analyzer = ProjectPortfolioAnalyzer()
        portfolio_analyzer.run_complete_analysis()
        print("✅ Portfolio analysis completed!")
        
        # シグナル分析の実行
        print("\n🎯 Running Signal Analysis...")
        signal_analyzer = ProjectSignalAnalyzer()
        signal_analyzer.run_complete_signal_analysis()
        print("✅ Signal analysis completed!")
        
        print("\n" + "="*60)
        print("🎉 ALL PROCESSES COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("Generated files:")
        print("  📁 projects/     - Original CSV datasets")
        print("  📁 data/         - Integrated project data")
        print("  📁 png/          - Dendrogram visualizations")
        
    except FileNotFoundError:
        print("❌ Error: config.yaml file not found")
        print("Please make sure config.yaml exists in the proper directory")
    except KeyboardInterrupt:
        print("\n⏹️  プログラムが中断されました")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
