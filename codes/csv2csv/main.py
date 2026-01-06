from csv2csv_converter import Csv2CsvConverter

def main():
    """
    プログラムのエントリポイント。CSV-to-CSV変換を実行します。
    
    処理内容:
    - in/ フォルダのCSVを読み込み
    - ヘッダ変換、新規項目追加、レイアウト変更を一度に実行
    - out/ フォルダに最終形式で出力
    """
    print("=" * 60)
    print("  CSV to CSV Converter 起動")
    print("=" * 60)
    
    # 統合変換実行
    converter = Csv2CsvConverter(
        in_dir_path='in',
        out_dir_path='out',
        config_dir_path='config'
    )
    converter.convert_all()
    
    print("=" * 60)
    print("  CSV to CSV Converter 終了")
    print("=" * 60)

if __name__ == "__main__":
    main()
