"""
IT部門サービス満足度アンケート分析プログラム
データ生成と分析を統合したメインプログラム
"""

import sys
import os
import pandas as pd
from pathlib import Path


def get_yes_no_input(prompt: str) -> bool:
    """
    Y/N形式の入力を取得
    
    Args:
        prompt: 表示するプロンプト
        
    Returns:
        Yesの場合True、Noの場合False
    """
    while True:
        response = input(prompt).strip().upper()
        if response in ['Y', 'YES']:
            return True
        elif response in ['N', 'NO']:
            return False
        else:
            print("Y または N を入力してください。")


def generate_data():
    """サンプルデータの生成"""
    try:
        from data_generator import SurveyDataGenerator
    except ImportError:
        print("\n❌ エラー: data_generator.py が見つかりません")
        return None
    
    print("\n" + "="*70)
    print("サンプルデータ生成")
    print("="*70)
    
    # デフォルト100件
    sample_size = 100
    
    try:
        print(f"\n設定読込: survey_questions.yaml")
        generator = SurveyDataGenerator()
        
        print(f"データ生成中... ({sample_size}件)")
        df = generator.generate_sample_data(n=sample_size)
        
        # 保存
        output_file = 'survey_sample_data.csv'
        generator.save_to_csv(df, output_file)
        
        # 統計表示
        stats = generator.get_statistics(df)
        print_generation_statistics(stats)
        
        print(f"\n✓ データ生成完了: {output_file}")
        return output_file
        
    except FileNotFoundError:
        print("\n❌ エラー: survey_questions.yaml が見つかりません")
        return None
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        return None


def print_generation_statistics(stats: dict):
    """データ生成統計の表示"""
    print("\n" + "-"*70)
    print("生成データ統計")
    print("-"*70)
    print(f"総サンプル数: {stats['total_samples']}件")
    
    print("\n満足度評価の統計:")
    print(f"{'項目':<25} {'平均':<8} {'標準偏差':<8}")
    print("-" * 70)
    
    names = {
        'overall_satisfaction': '総合満足度',
        'response_speed': '対応スピード',
        'technical_competence': '技術的解決力',
        'explanation_clarity': '説明のわかりやすさ',
        'service_politeness': '対応の丁寧さ',
        'system_stability': 'システムの安定性',
        'security_measures': 'セキュリティ対策',
        'new_system_support': '新システム導入支援'
    }
    
    for key, data in stats['ratings'].items():
        name = names.get(key, key)
        print(f"{name:<25} {data['mean']:<8.2f} {data['std']:<8.2f}")
    
    print("-" * 70)


def analyze_data(data_file: str):
    """データ分析の実行"""
    try:
        from data_analyser import SurveyDataAnalyser
        from report_generator import ReportGenerator
    except ImportError as e:
        print(f"\n❌ エラー: 必要なモジュールが見つかりません: {e}")
        return False
    
    print("\n" + "="*70)
    print("データ分析実行")
    print("="*70)
    
    # データ読込
    try:
        print(f"\nデータ読込中: {data_file}")
        df = pd.read_csv(data_file)
        print(f"✓ {len(df)}件のデータを読み込みました")
    except FileNotFoundError:
        print(f"\n❌ エラー: {data_file} が見つかりません")
        return False
    except Exception as e:
        print(f"\n❌ エラー: データ読込に失敗しました: {e}")
        return False
    
    # 分析実行
    try:
        analyser = SurveyDataAnalyser(df)
        results = analyser.run_full_analysis()
        
        # レポート生成
        print("\nレポート生成中...")
        report_gen = ReportGenerator(results)
        
        # テキストレポート
        txt_file = 'analysis_report.txt'
        report_gen.generate_full_report(txt_file)
        print(f"✓ テキストレポート: {txt_file}")
        
        print("\n" + "="*70)
        print("分析完了！")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ エラー: 分析中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メイン処理"""
    print("\n" + "="*70)
    print("IT部門サービス満足度アンケート")
    print("データ生成・分析プログラム")
    print("="*70)
    
    # データ生成の確認
    generate = get_yes_no_input("\nサンプルデータを生成しますか？ (Y/N): ")
    
    data_file = 'survey_sample_data.csv'
    
    if generate:
        # データ生成
        generated_file = generate_data()
        if generated_file is None:
            print("\nデータ生成に失敗しました。")
            return 1
        data_file = generated_file
    else:
        # 既存のファイルを確認
        if not os.path.exists(data_file):
            print(f"\n❌ エラー: {data_file} が見つかりません")
            print("データを生成するか、データファイルを配置してください。")
            return 1
        print(f"\n既存のデータファイルを使用します: {data_file}")
    
    # データ分析を自動実行
    success = analyze_data(data_file)
    if not success:
        print("\nデータ分析に失敗しました。")
        return 1
    
    print("\n処理が完了しました。\n")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n処理が中断されました。\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
