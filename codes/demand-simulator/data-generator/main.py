#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サンプルデータ生成ツール - メインエントリポイント

YAMLファイルでデータ定義を読み込み、CSV形式でサンプルデータを出力します。
需要データ（案件データ）または供給データ（社員データ）を選択して生成できます。
"""

from modules.demand_data_generator import DemandDataGenerator
from modules.supply_data_generator import SupplyDataGenerator


def select_data_type():
    """
    生成するデータタイプをユーザーに選択させる
    
    Returns:
        str: 'demand' または 'supply'
    """
    print("\n" + "=" * 60)
    print("サンプルデータ生成ツール")
    print("=" * 60)
    print("\n生成するデータタイプを選択してください:")
    print("  1: 需要データ（案件データ）")
    print("  2: 供給データ（社員データ）")
    print()
    
    while True:
        choice = input("選択してください (1 または 2): ").strip()
        if choice == '1':
            return 'demand'
        elif choice == '2':
            return 'supply'
        else:
            print("無効な選択です。1 または 2 を入力してください。")


def generate_demand_data():
    """需要データ（案件データ）を生成"""
    print("\n需要データ（案件データ）を生成します...")
    
    # データ生成器を初期化
    generator = DemandDataGenerator('config/data_definition_demand.yaml')
    
    # YAMLファイルから出力設定を読み込む
    output_config = generator.get_output_config()
    output_file = output_config.get('file', 'demand_data.csv')
    num_records = output_config.get('records', 100)
    
    # csvフォルダのパスを確保
    if not output_file.startswith('csv/'):
        output_file = f'csv/{output_file}'
    
    # データを生成
    print(f"\n{num_records}件のサンプルデータを生成中...")
    data = generator.generate_data(num_records)
    
    # CSVファイルに保存
    generator.save_to_csv(data, output_file)
    
    return data


def generate_supply_data():
    """供給データ（社員データ）を生成"""
    print("\n供給データ（社員データ）を生成します...")
    
    # データ生成器を初期化
    generator = SupplyDataGenerator('config/data_definition_supply.yaml')
    
    # YAMLファイルから出力設定を読み込む
    output_config = generator.get_output_config()
    output_file = output_config.get('file', 'supply_data.csv')
    num_records = output_config.get('records', 50)
    
    # csvフォルダのパスを確保
    if not output_file.startswith('csv/'):
        output_file = f'csv/{output_file}'
    
    # データを生成
    print(f"\n{num_records}件のサンプルデータを生成中...")
    data = generator.generate_data(num_records)
    
    # CSVファイルに保存
    generator.save_to_csv(data, output_file)
    
    return data


def display_sample_data(data, data_type):
    """
    サンプルデータを表示
    
    Args:
        data (list): 表示するデータ
        data_type (str): データタイプ（'demand' または 'supply'）
    """
    data_type_label = "需要データ（案件データ）" if data_type == 'demand' else "供給データ（社員データ）"
    
    print("\n" + "=" * 60)
    print(f"{data_type_label} - サンプル（最初の5件）")
    print("=" * 60)
    
    for i, record in enumerate(data[:5], 1):
        print(f"\n【{i}件目】")
        for key, value in record.items():
            print(f"  {key}: {value}")


def main():
    """メイン処理"""
    try:
        # データタイプを選択
        data_type = select_data_type()
        
        # 選択されたデータタイプに応じて生成
        if data_type == 'demand':
            data = generate_demand_data()
        else:  # supply
            data = generate_supply_data()
        
        # サンプルデータの表示
        display_sample_data(data, data_type)
        
        print("\n" + "=" * 60)
        print("処理が正常に完了しました")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\nエラー: {e}")
        print("必要な設定ファイルが見つかりません。")
        return 1
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
