"""
サンプルデータ生成プログラム
2段階データ生成: Respondents → VendorEvaluations
"""

import sys
import json
from pathlib import Path
from data_generator import SurveyDataGenerator
import yaml


def check_config_file(config_dir, filename):
    """
    指定された設定ファイルの存在確認
    
    Args:
        config_dir: 設定ファイルディレクトリのパス
        filename: ファイル名
        
    Returns:
        Path: ファイルのPath、存在しない場合はNone
    """
    config_path = Path(config_dir) / filename
    if config_path.exists():
        return config_path
    return None


def get_sample_size(default=100, prompt_message=None):
    """
    サンプル数の入力を取得
    
    Args:
        default: デフォルト値
        prompt_message: プロンプトメッセージ（Noneの場合はデフォルトメッセージ）
    
    Returns:
        int: サンプル数
    """
    if prompt_message is None:
        prompt_message = f"\n生成するサンプル数を入力してください (デフォルト: {default}): "
    
    while True:
        try:
            sample_input = input(prompt_message).strip()
            if sample_input == "":
                return default
            sample_size = int(sample_input)
            if sample_size > 0:
                return sample_size
            else:
                print("1以上の数値を入力してください。")
        except ValueError:
            print("数値を入力してください。")


def print_statistics(stats: dict, config_file_name: str):
    """データ生成統計の表示"""
    print("\n" + "-"*70)
    print(f"生成データ統計 ({config_file_name})")
    print("-"*70)
    print(f"総サンプル数: {stats['total_samples']}件")
    print(f"総カラム数: {stats['total_columns']}列")
    print("-" * 70)


def load_respondents_json(json_dir='json'):
    """
    respondents.jsonを読み込む
    
    Args:
        json_dir: JSONディレクトリのパス
        
    Returns:
        tuple: (回答者データのリスト, 回答者数)
    """
    json_path = Path(json_dir) / 'respondents.json'
    
    if not json_path.exists():
        raise FileNotFoundError(f"respondents.jsonが見つかりません: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        respondents = json.load(f)
    
    return respondents, len(respondents)


def get_vendor_count(config_file):
    """
    vendor-evaluation.yamlからベンダー数を取得
    
    Args:
        config_file: YAML設定ファイルのパス
        
    Returns:
        int: ベンダー数
    """
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    enums = config.get('enums', {})
    vendor_enum = enums.get('vendorId', {})
    vendor_values = vendor_enum.get('values', [])
    
    return len(vendor_values)


def generate_respondents_data(config_dir='yml', json_dir='json', output_dir_csv='csv', output_dir_json='json'):
    """
    ステップ1: 回答者データの生成
    
    Returns:
        tuple: (成功フラグ, 回答者数)
    """
    print("\n" + "="*70)
    print("【ステップ1】回答者マスターデータ生成")
    print("="*70)
    
    # respondents.yamlの確認
    respondents_yaml = check_config_file(config_dir, 'respondents.yaml')
    if respondents_yaml is None:
        print(f"\n❌ エラー: {config_dir}/respondents.yaml が見つかりません")
        return False, 0
    
    print(f"\n✓ 設定ファイル確認: {respondents_yaml}")
    
    # 既存のrespondents.jsonの確認
    json_path = Path(json_dir) / 'respondents.json'
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_respondents = json.load(f)
            existing_count = len(existing_respondents)
            
            print(f"\n⚠ 既存の回答者データが見つかりました:")
            print(f"  - ファイル: {json_path}")
            print(f"  - 回答者数: {existing_count}人")
            
            regenerate = input("\n回答者マスターを再生成しますか？ (y/n): ").strip().lower()
            if regenerate != 'y':
                print(f"\n既存の回答者データ({existing_count}人)を使用します。")
                return True, existing_count
        except Exception as e:
            print(f"\n⚠ 既存ファイルの読み込みに失敗しました: {e}")
            print("新規生成を続行します。")
    
    # サンプル数入力
    sample_size = get_sample_size(default=10, prompt_message="\n生成する回答者数を入力してください (デフォルト: 10): ")
    
    try:
        print(f"\n設定読込: {respondents_yaml}")
        generator = SurveyDataGenerator(respondents_yaml)
        
        print(f"データ生成中... ({sample_size}件)")
        df = generator.generate_sample_data(n=sample_size)
        
        csv_file = generator.save_to_csv(df, output_dir=output_dir_csv)
        json_file = generator.save_to_json(df, output_dir=output_dir_json)
        
        stats = generator.get_statistics(df)
        print_statistics(stats, respondents_yaml.stem)
        
        print(f"\n✓ 回答者データ生成完了:")
        print(f"  - CSV:  {csv_file}")
        print(f"  - JSON: {json_file}")
        
        return True, sample_size
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def generate_vendor_evaluation_data(config_dir='yml', json_dir='json', output_dir_csv='csv', output_dir_json='json'):
    """
    ステップ2: ベンダー評価データの生成
    
    Returns:
        bool: 成功フラグ
    """
    print("\n\n" + "="*70)
    print("【ステップ2】ベンダー評価データ生成")
    print("="*70)
    
    # vendor-evaluation.yamlの確認
    vendor_yaml = check_config_file(config_dir, 'vendor-evaluation.yaml')
    if vendor_yaml is None:
        print(f"\n❌ エラー: {config_dir}/vendor-evaluation.yaml が見つかりません")
        return False
    
    print(f"\n✓ 設定ファイル確認: {vendor_yaml}")
    
    try:
        # respondents.jsonの読み込み
        respondents_json_path = Path(json_dir) / 'respondents.json'
        print(f"\n回答者データ読込: {respondents_json_path}")
        respondents, respondent_count = load_respondents_json(json_dir)
        print(f"✓ 回答者数: {respondent_count}人")
        
        # ベンダー数の取得
        vendor_count = get_vendor_count(vendor_yaml)
        print(f"✓ ベンダー数: {vendor_count}社")
        
        # 総サンプル数の計算と表示
        total_samples = respondent_count * vendor_count
        print(f"\n生成される評価データ総数: {respondent_count} (回答者) × {vendor_count} (ベンダー) = {total_samples}件")
        
        # 確認プロンプト
        confirm = input(f"\n{total_samples}件の評価データを生成しますか？ (y/n): ").strip().lower()
        if confirm != 'y':
            print("生成をキャンセルしました。")
            return False
        
        # データ生成（respondents.jsonを渡す）
        print(f"\n設定読込: {vendor_yaml}")
        generator = SurveyDataGenerator(vendor_yaml, respondents_json_path=respondents_json_path)
        
        print(f"データ生成中... ({total_samples}件)")
        df = generator.generate_sample_data(n=total_samples)
        
        csv_file = generator.save_to_csv(df, output_dir=output_dir_csv)
        json_file = generator.save_to_json(df, output_dir=output_dir_json)
        
        stats = generator.get_statistics(df)
        print_statistics(stats, vendor_yaml.stem)
        
        print(f"\n✓ ベンダー評価データ生成完了:")
        print(f"  - CSV:  {csv_file}")
        print(f"  - JSON: {json_file}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ エラー: {e}")
        return False
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メイン処理"""
    print("\n" + "="*70)
    print("ベンダー評価サンプルデータ生成プログラム")
    print("="*70)
    print("\n処理フロー:")
    print("  1. 回答者マスターデータ生成 (respondents.yaml)")
    print("  2. ベンダー評価データ生成 (vendor-evaluation.yaml)")
    print("="*70)
    
    # ステップ1: 回答者データ生成
    success, respondent_count = generate_respondents_data()
    if not success:
        print("\n処理を中断しました。\n")
        return 1
    
    # ステップ2: ベンダー評価データ生成
    success = generate_vendor_evaluation_data()
    if not success:
        print("\n処理を中断しました。\n")
        return 1
    
    print("\n" + "="*70)
    print("全ての処理が正常に完了しました！")
    print("="*70)
    print()
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