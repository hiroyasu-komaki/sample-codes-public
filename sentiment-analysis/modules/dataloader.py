# dataloader.py
import os

def list_text_files(directory):
    """
    指定ディレクトリ内のテキストファイルをリストアップ
    """
    if not os.path.exists(directory):
        return []
    
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    return files

def select_file(files):
    """
    ユーザーにファイルを選択させる
    """
    print("\n利用可能なテキストファイル:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file}")
    
    while True:
        try:
            choice = int(input(f"\n分析するファイルを選択してください (1-{len(files)}): "))
            if 1 <= choice <= len(files):
                return os.path.join("txt", files[choice - 1])
            else:
                print(f"1から{len(files)}の間で選択してください")
        except ValueError:
            print("数字を入力してください")

