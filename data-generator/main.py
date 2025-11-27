"""
サンプルデータ生成プログラム
"""

import sys
from pathlib import Path
from data_generator import SurveyDataGenerator


def find_config_files(config_dir='yml'):
    """
    YAMLファイルを検索
    
    Args:
        config_dir: 設定ファイルディレクトリのパス
        
    Returns:
        list: YAMLファイルのPathオブジェクトのリスト
    """
    config_path = Path(config_dir)
    
    if not config_path.exists():
        return []
    
    yaml_files = list(config_path.glob('*.yaml')) + list(config_path.glob('*.yml'))
    return sorted(yaml_files)


def select_config_file(yaml_files):
    """
    設定ファイルを選択
    
    Args:
        yaml_files: YAMLファイルのリスト
        
    Returns:
        Path: 選択されたファイルのPath、またはNone
    """
    if not yaml_files:
        return None
    
    if len(yaml_files) == 1:
        print(f"\n設定ファイル: {yaml_files[0].name}")
        return yaml_files[0]
    
    print("\n利用可能な設定ファイル:")
    print("-" * 70)
    for i, yaml_file in enumerate(yaml_files, 1):
        print(f"{i}. {yaml_file.name}")
    print("-" * 70)
    
    while True:
        try:
            choice = input(f"\n設定ファイルを選択してください (1-{len(yaml_files)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(yaml_files):
                return yaml_files[index]
            else:
                print(f"1から{len(yaml_files)}の間の数値を入力してください。")
        except ValueError:
            print("数値を入力してください。")


def get_sample_size():
    """
    サンプル数の入力を取得
    
    Returns:
        int: サンプル数
    """
    while True:
        try:
            sample_input = input("\n生成するサンプル数を入力してください (デフォルト: 100): ").strip()
            if sample_input == "":
                return 100
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


def main():
    """メイン処理"""
    print("\n" + "="*70)
    print("サンプルデータ生成プログラム (Applications.yaml専用)")
    print("="*70)
    
    yaml_files = find_config_files('yml')
    
    if not yaml_files:
        print("\n❌ エラー: 設定ファイル(.yaml/.yml)が見つかりません")
        print("ymlディレクトリを作成し、設定ファイルを配置してください。")
        return 1
    
    config_file = select_config_file(yaml_files)
    if config_file is None:
        print("\n❌ エラー: 設定ファイルの選択に失敗しました")
        return 1
    
    sample_size = get_sample_size()
    
    try:
        print(f"\n設定読込: {config_file}")
        generator = SurveyDataGenerator(config_file)
        
        print(f"データ生成中... ({sample_size}件)")
        df = generator.generate_sample_data(n=sample_size)
        
        csv_file = generator.save_to_csv(df, output_dir='csv')
        json_file = generator.save_to_json(df, output_dir='json')
        
        stats = generator.get_statistics(df)
        print_statistics(stats, config_file.stem)
        
        print(f"\n✓ データ生成完了:")
        print(f"  - CSV:  {csv_file}")
        print(f"  - JSON: {json_file}")
        print("\n処理が完了しました。\n")
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ エラー: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1


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