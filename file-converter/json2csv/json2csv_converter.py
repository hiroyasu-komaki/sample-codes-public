import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

class JsonToCsvConverter:
    """
    JSONファイルからデータを読み込み、ユーザーの選択に基づいてCSVファイルに変換するクラス。
    """

    def __init__(self, json_dir_path: str = 'json', csv_dir_path: str = 'csv'):
        """
        コンバータを初期化します。

        :param json_dir_path: JSONファイルの入力ディレクトリパス
        :param csv_dir_path: CSVファイルの出力ディレクトリパス
        """
        self.json_dir = Path(json_dir_path)
        self.csv_dir = Path(csv_dir_path)
        self._ensure_dirs()

    def _ensure_dirs(self):
        """
        入力/出力ディレクトリが存在することを確認し、なければ作成します。
        """
        self.json_dir.mkdir(exist_ok=True)
        self.csv_dir.mkdir(exist_ok=True)
        print(f"✅ ディレクトリ構成を確認/作成しました。Input: {self.json_dir}, Output: {self.csv_dir}")

    def _list_json_files(self) -> List[Path]:
        """
        JSONディレクトリ内のJSONファイルを一覧表示し、リストを返します。
        """
        json_files = sorted(list(self.json_dir.glob('*.json')))
        
        if not json_files:
            print(f"⚠️ {self.json_dir} フォルダにJSONファイルが見つかりませんでした。")
        else:
            print("\n📄 検出されたJSONファイル:")
            for i, file in enumerate(json_files):
                print(f"  [{i+1}] {file.name}")
        
        return json_files

    def _select_json_file(self, json_files: List[Path]) -> Optional[Path]:
        """
        ユーザーにJSONファイルを選択させます。
        """
        if not json_files:
            return None
        
        while True:
            try:
                choice = input("\n> 処理するJSONファイルの番号を入力してください (例: 1): ")
                file_index = int(choice) - 1
                if 0 <= file_index < len(json_files):
                    selected_file = json_files[file_index]
                    print(f"✅ ファイル '{selected_file.name}' を選択しました。")
                    return selected_file
                else:
                    print("❌ 無効な番号です。リストから選択してください。")
            except ValueError:
                print("❌ 無効な入力です。番号を入力してください。")

    def _select_json_key(self, data: Dict[str, Any]) -> Optional[str]:
        """
        JSONデータの第一階層のキーを一覧表示し、ユーザーに選択させます。
        """
        keys = list(data.keys())
        if not keys:
            print("⚠️ JSONファイルにデータキーが見つかりませんでした。")
            return None

        print("\n🔑 JSONデータの第一階層キー:")
        print("  [0] 全てのキー (それぞれ別ファイルに出力)")
        for i, key in enumerate(keys):
            print(f"  [{i+1}] {key}")

        while True:
            choice = input("\n> 処理するキーの番号を入力してください (デフォルト: 0 - 全て): ")
            if not choice:
                return None # デフォルト (全て)
            
            try:
                key_index = int(choice)
                if key_index == 0:
                    return None # 全て
                elif 1 <= key_index <= len(keys):
                    selected_key = keys[key_index - 1]
                    print(f"✅ キー '{selected_key}' を選択しました。")
                    return selected_key
                else:
                    print("❌ 無効な番号です。リストから選択するか、Enterで全てを選択してください。")
            except ValueError:
                print("❌ 無効な入力です。番号を入力するか、Enterを押してください。")

    def _convert_data_to_csv(self, data: List[Dict[str, Any]], key_name: str, base_filename: Path):
        """
        指定されたデータリストをCSVファイルに変換し保存します。
        
        :param data: CSVに変換するデータリスト
        :param key_name: CSVファイル名に使用するキー名
        :param base_filename: 元のJSONファイル名 (拡張子なし)
        """
        if not data:
            print(f"⚠️ キー '{key_name}' にデータがありませんでした。スキップします。")
            return
        
        if not isinstance(data, List) or not data or not isinstance(data[0], Dict):
            print(f"⚠️ キー '{key_name}' のデータはCSV変換可能なリスト形式ではありません。スキップします。")
            return

        # CSVファイル名を作成 (例: application_layer_view_data_projects.csv)
        # csv_filename = f"{base_filename.stem}_{key_name}.csv"
        csv_filename = f"{key_name}.csv"
        csv_path = self.csv_dir / csv_filename
        
        # ヘッダー (データリストの最初の辞書のキーを使用)
        fieldnames = list(data[0].keys())

        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # ヘッダーを書き込む
                writer.writeheader()
                
                # データを書き込む
                writer.writerows(data)

            print(f"✅ キー '{key_name}' のデータを {csv_path} に変換し保存しました。")
        except Exception as e:
            print(f"❌ CSVファイル {csv_path.name} の書き込み中にエラーが発生しました: {e}")

    def convert_interactive(self):
        """
        ユーザーと対話しながら、JSONファイルの選択とキーの選択を行い、CSVに変換します。
        """
        # １）JSONファイルの一覧表示と選択
        json_files = self._list_json_files()
        selected_json_path = self._select_json_file(json_files)
        
        if not selected_json_path:
            return

        try:
            with open(selected_json_path, 'r', encoding='utf-8') as f:
                data: Dict[str, Any] = json.load(f)
        except Exception as e:
            print(f"❌ ファイル {selected_json_path.name} の読み込み中にエラーが発生しました: {e}")
            return

        # ２）３）４）JSONキーの一覧表示と選択
        selected_key = self._select_json_key(data)
        
        # ５）CSVファイルの生成
        base_filename = selected_json_path.stem
        if selected_key:
            # 単一キーの指定がある場合
            key_data = data.get(selected_key)
            if key_data and isinstance(key_data, List):
                 self._convert_data_to_csv(key_data, selected_key, selected_json_path)
            elif key_data and isinstance(key_data, Dict):
                 # 辞書の場合はリストに変換して処理（例: statsキー）
                 self._convert_data_to_csv([key_data], selected_key, selected_json_path)
            else:
                 print(f"⚠️ キー '{selected_key}' のデータは変換可能な形式ではありません。")
        else:
            # キーの指定がない場合 (全ての第一階層キーを処理)
            print("\n➡️ 全ての第一階層キーに対してCSV変換を実行します...")
            for key, key_data in data.items():
                if isinstance(key_data, List):
                    self._convert_data_to_csv(key_data, key, selected_json_path)
                elif isinstance(key_data, Dict):
                    # 辞書の場合はリストに変換して処理
                    self._convert_data_to_csv([key_data], key, selected_json_path)
                else:
                    print(f"⚠️ キー '{key}' はリスト/辞書型ではないためスキップします。")
            
        print("\n✨ 処理が完了しました。")

# 実行例 (main.pyから呼び出されるため、ここでは実行しません)
# if __name__ == '__main__':
#     # NOTE: このファイル構造をシミュレートするには、'json'フォルダと'csv'フォルダ、
#     # および'json'フォルダ内にJSONファイルが必要です。
#     converter = JsonToCsvConverter(json_dir_path='.', csv_dir_path='csv_output')
#     converter.convert_interactive()