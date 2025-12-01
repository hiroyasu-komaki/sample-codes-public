from json2csv_converter import JsonToCsvConverter

def main():
    """
    プログラムのエントリポイント。JSON-to-CSV変換を実行します。
    ユーザーからの入力を受け付け、対話的に処理を進めます。
    """
    print("--- JSON to CSV Generator 起動 (対話モード) ---")
    
    # JsonToCsvConverterをインスタンス化し、対話的な変換処理を実行
    converter = JsonToCsvConverter()
    converter.convert_interactive() # <-- 修正: convert_allからconvert_interactiveに変更
    
    print("--- JSON to CSV Generator 終了 ---")

if __name__ == "__main__":
    main()