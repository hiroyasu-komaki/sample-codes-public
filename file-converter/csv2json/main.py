from csv2json_converter import CsvToJsonConverter

def main():
    """
    プログラムのエントリポイント。CSV-to-JSON変換を実行します。
    """
    print("--- CSV to JSON Generator 起動 ---")
    
    # CsvToJsonConverterをインスタンス化し、変換処理を実行
    # 入力は 'csv' フォルダ、出力は 'json_output' フォルダとします
    converter = CsvToJsonConverter(csv_dir_path='csv', json_dir_path='json')
    converter.convert_all()
    
    print("--- CSV to JSON Generator 終了 ---")

if __name__ == "__main__":
    main()