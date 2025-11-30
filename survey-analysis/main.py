"""
IT部門サービス満足度アンケート分析プログラム
データ生成と前処理を統合したメインプログラム
"""

import sys
import os
import pandas as pd
import yaml
from pathlib import Path

from modules.data_generator import SurveyDataGenerator
from modules.data_preprocess import DataPreprocessor
from modules.data_analyser import SurveyDataAnalyser
from modules.report_generator import SurveyReportGenerator
from modules import util


def load_config(config_file='config/config.yaml'):
    """
    設定ファイルの読み込み
    
    Args:
        config_file: 設定ファイルのパス
        
    Returns:
        dict: 設定情報
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"\n❌ エラー: {config_file} が見つかりません")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラー: 設定ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)


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


def generate_data(config):
    """サンプルデータの生成"""
    util.print_header("サンプルデータ生成")
    
    # 設定から値を取得
    sample_size = config['data_generation']['default_sample_size']
    survey_questions_file = config['files']['survey_questions']
    output_file = config['files']['sample_data']
    csv_dir = config['directories']['csv']
    
    try:
        print(f"\n設定読込: {survey_questions_file}")
        generator = SurveyDataGenerator(survey_questions_file)
        
        print(f"データ生成中... ({sample_size}件)")
        df = generator.generate_sample_data(n=sample_size)
        
        # 保存
        os.makedirs(csv_dir, exist_ok=True)
        generator.save_to_csv(df, output_file)
        
        # 統計表示
        stats = generator.get_statistics(df)
        util.print_statistics(stats, "生成データ統計")
        
        util.print_success(f"データ生成完了: {output_file}")
        return output_file
        
    except FileNotFoundError:
        util.print_error(f"{survey_questions_file} が見つかりません")
        return None
    except Exception as e:
        util.print_error(str(e))
        import traceback
        traceback.print_exc()
        return None


def preprocess_data(input_file: str, config):
    """データ前処理の実行"""
    util.print_header("データ前処理実行")
    
    print(f"\n設定読込: {config['files']['survey_questions']}")
    print(f"処理中...")
    
    try:
        # 前処理実行
        survey_questions_file = config['files']['survey_questions']
        preprocessor = DataPreprocessor(survey_questions_file)
        
        # データ読み込み
        preprocessor.load_data(input_file)
        
        # 前処理パイプライン実行
        processed_data = preprocessor.preprocess_pipeline()
        
        # 結果保存
        output_dir = config['directories']['output']
        csv_dir = config['directories']['csv']
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(csv_dir, exist_ok=True)
        
        preprocessed_file = config['files']['preprocessed_data']
        
        preprocessor.save_processed_data(preprocessed_file)
        
        # レポートはoutディレクトリに固定パスで保存
        preprocessor.save_report('out/preprocessing_report.json')
        
        # サマリー表示
        util.print_preprocessing_summary(preprocessor)
        
        util.print_success(f"データ前処理完了: {preprocessed_file}")
        
        return preprocessed_file
        
    except Exception as e:
        util.print_error(f"前処理中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_data(input_file: str, config):
    """データ分析の実行"""
    util.print_header("データ分析実行")
    
    print(f"\n設定読込: {config['files']['survey_questions']}")
    print(f"分析中...")
    
    try:
        # 分析実行
        survey_questions_file = config['files']['survey_questions']
        main_config_file = 'config/config.yaml'
        
        analyser = SurveyDataAnalyser(
            config_file=survey_questions_file,
            main_config_file=main_config_file
        )
        
        # データ読み込み
        analyser.load_data(input_file)
        
        # 分析パイプライン実行
        analysis_results = analyser.analysis_pipeline()
        
        # 結果保存
        output_dir = config['directories']['output']
        os.makedirs(output_dir, exist_ok=True)
        
        analysis_results_file = 'out/analysis_results.json'
        analyser.save_analysis_results(analysis_results_file)
        
        util.print_success(f"データ分析完了: {analysis_results_file}")
        
        return analysis_results_file
        
    except Exception as e:
        util.print_error(f"分析中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_reports(analysis_results_file: str, config):
    """レポート生成の実行"""
    util.print_header("レポート生成実行")
    
    print(f"\nレポート生成中...")
    
    try:
        # 分析結果の読み込み
        import json
        with open(analysis_results_file, 'r', encoding='utf-8') as f:
            analysis_results = json.load(f)
        
        # レポート生成器の初期化
        generator = SurveyReportGenerator(
            analysis_results=analysis_results,
            config_file='config/config.yaml'
        )
        
        # 全レポート生成
        reports_dir = config['directories']['reports']
        generated_files = generator.generate_all_reports(output_dir=reports_dir)
        
        # Noneチェックを追加
        if generated_files is None:
            generated_files = {}
        
        # 生成されたファイルを表示
        if generated_files:
            print("\n生成されたレポート:")
            for file_type, filepath in generated_files.items():
                print(f"  - {file_type}: {filepath}")
            
            util.print_success(f"レポート生成完了: {reports_dir}")
        else:
            print("\n⚠️  警告: レポートファイルが生成されませんでした")
        
        return reports_dir
        
    except Exception as e:
        util.print_error(f"レポート生成中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None



def main():
    """メイン処理"""
    print("\n" + "="*70)
    print("IT部門サービス満足度アンケート")
    print("データ生成・前処理・分析・レポート生成プログラム")
    print("="*70)
    
    # 設定ファイルの読み込み
    config = load_config()
    
    # データ生成の確認
    generate = get_yes_no_input("\nサンプルデータを生成しますか？ (Y/N): ")
    
    data_file = config['files']['sample_data']
    
    if generate:
        # データ生成
        generated_file = generate_data(config)
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
    
    # データ前処理の確認
    do_preprocess = get_yes_no_input("\nデータ前処理を実行しますか？ (Y/N): ")
    
    preprocessed_file = None
    if do_preprocess:
        preprocessed_file = preprocess_data(data_file, config)
        if preprocessed_file is None:
            print("\nデータ前処理に失敗しました。")
            return 1
        
        print(f"\n前処理済みデータ: {preprocessed_file}")
    else:
        # 既存の前処理済みファイルを確認
        preprocessed_file = config['files']['preprocessed_data']
        if not os.path.exists(preprocessed_file):
            print(f"\n⚠️  前処理をスキップしましたが、前処理済みファイルが見つかりません: {preprocessed_file}")
            print("分析を実行するには、前処理を実行する必要があります。")
            print("\n前処理をスキップしました。")
            return 0
        print("\n前処理をスキップしました。")
        print(f"既存の前処理済みデータを使用します: {preprocessed_file}")
    
    # データ分析の確認
    do_analysis = get_yes_no_input("\nデータ分析を実行しますか？ (Y/N): ")
    
    analysis_results_file = None
    if do_analysis:
        analysis_results_file = analyze_data(preprocessed_file, config)
        if analysis_results_file is None:
            print("\nデータ分析に失敗しました。")
            return 1
        
        print(f"\n分析結果: {analysis_results_file}")
    else:
        # 既存の分析結果ファイルを確認
        analysis_results_file = 'out/analysis_results.json'
        if not os.path.exists(analysis_results_file):
            print(f"\n⚠️  分析をスキップしましたが、分析結果ファイルが見つかりません: {analysis_results_file}")
            print("レポート生成を実行するには、分析を実行する必要があります。")
            print("\n分析をスキップしました。")
            return 0
        print("\n分析をスキップしました。")
        print(f"既存の分析結果を使用します: {analysis_results_file}")
    
    # レポート生成の確認
    do_report = get_yes_no_input("\nレポートを生成しますか？ (Y/N): ")
    
    if do_report:
        reports_dir = generate_reports(analysis_results_file, config)
        if reports_dir is None:
            print("\nレポート生成に失敗しました。")
            return 1
        
        print(f"\nレポート: {reports_dir}")
    else:
        print("\nレポート生成をスキップしました。")
    
    print("\n" + "="*70)
    print("すべての処理が完了しました。")
    print("="*70 + "\n")
    
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