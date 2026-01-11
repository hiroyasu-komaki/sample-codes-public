#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サンプルデータ生成ツール - メインエントリポイント

YAMLファイルでデータ定義を読み込み、CSV形式でサンプルデータを出力します。
"""

from modules.sample_data_generator import SampleDataGenerator


def main():
    """メイン処理"""
    try:
        # データ生成器を初期化
        print("サンプルデータ生成ツールを起動しています...")
        generator = SampleDataGenerator()
        
        # YAMLファイルから出力設定を読み込む
        output_config = generator.get_output_config()
        output_file = output_config.get('file', 'csv/sample_data.csv')
        num_records = output_config.get('records', 100)
        
        # csvフォルダのパスを確保
        if not output_file.startswith('csv/'):
            output_file = f'csv/{output_file}'
        
        # データを生成
        print(f"\n{num_records}件のサンプルデータを生成中...")
        data = generator.generate_data(num_records)
        
        # CSVファイルに保存
        generator.save_to_csv(data, output_file)
        
        # サンプルデータの表示
        print("\n" + "=" * 60)
        print("サンプルデータ（最初の5件）")
        print("=" * 60)
        for i, record in enumerate(data[:5], 1):
            print(f"\n【{i}件目】")
            for key, value in record.items():
                print(f"  {key}: {value}")
        
        print("\n" + "=" * 60)
        print("処理が正常に完了しました")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
