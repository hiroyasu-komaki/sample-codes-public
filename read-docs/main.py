from read_docs import read_docs_excel

def main():
    """
    メインエントリポイント
    Excelファイルを読み込んでCSV形式で出力します
    """
    print("=" * 60)
    print("業務棚卸しスプレッドシート処理開始")
    print("=" * 60)
    
    # Excelファイル読み込みとCSV出力
    read_docs_excel()
    
    print("\n" + "=" * 60)
    print("処理完了")
    print("=" * 60)

if __name__ == "__main__":
    main()
