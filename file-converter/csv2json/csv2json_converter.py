import csv
import json
import ast
from pathlib import Path
from typing import List, Dict, Any

class CsvToJsonConverter:
    """
    CSVファイルからプロジェクトデータを読み込み、JSONファイルに変換するクラス。
    配列フィールド（tags, projects等）を正しく復元します。
    """

    def __init__(self, csv_dir_path: str = 'csv', json_dir_path: str = 'json_output'):
        """
        コンバータを初期化します。

        :param csv_dir_path: CSVファイルの入力ディレクトリパス
        :param json_dir_path: JSONファイルの出力ディレクトリパス
        """
        self.csv_dir = Path(csv_dir_path)
        self.json_out_dir = Path(json_dir_path)
        self._ensure_dirs()

    def _ensure_dirs(self):
        """
        出力ディレクトリが存在することを確認し、なければ作成します。
        """
        self.json_out_dir.mkdir(exist_ok=True)
        print(f"✅ ディレクトリ構成を確認/作成しました。Input: {self.csv_dir}, Output: {self.json_out_dir}")

    def _parse_value(self, value: str) -> Any:
        """
        文字列値を適切な型に変換します。
        
        :param value: 変換対象の文字列
        :return: 変換後の値（配列、数値、または文字列）
        """
        if not isinstance(value, str):
            return value
        
        value = value.strip()
        
        # 空文字列の処理
        if not value:
            return value
        
        # 配列形式の文字列を検出して変換
        # 例: "['React', 'Next.js']" -> ["React", "Next.js"]
        if value.startswith('[') and value.endswith(']'):
            try:
                parsed = ast.literal_eval(value)
                if isinstance(parsed, list):
                    return parsed
            except (ValueError, SyntaxError):
                # パースできない場合は文字列のまま
                pass
        
        # 辞書形式の文字列を検出して変換（将来の拡張用）
        if value.startswith('{') and value.endswith('}'):
            try:
                parsed = ast.literal_eval(value)
                if isinstance(parsed, dict):
                    return parsed
            except (ValueError, SyntaxError):
                pass
        
        # 数値への変換を試みる
        if value.isdigit():
            return int(value)
        
        try:
            return float(value)
        except ValueError:
            pass
        
        # 真偽値への変換
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # 変換できない場合は文字列のまま返す
        return value

    def convert_all(self):
        """
        csvディレクトリ内の全てのCSVファイルをJSONに変換します。
        """
        csv_files = list(self.csv_dir.glob('*.csv'))

        if not csv_files:
            print(f"⚠️ {self.csv_dir} フォルダにCSVファイルが見つかりませんでした。")
            return

        print(f"📄 {len(csv_files)} 個のCSVファイルを検出しました。変換を開始します。")

        for csv_file in csv_files:
            try:
                self._convert_single_file(csv_file)
            except Exception as e:
                print(f"❌ ファイル {csv_file.name} の処理中にエラーが発生しました: {e}")

        print("✨ すべてのファイルの変換が完了しました。")

    def _convert_single_file(self, csv_path: Path):
        """
        単一のCSVファイルを読み込み、プロジェクトデータをJSONとして保存します。
        配列フィールドを正しく復元します。

        :param csv_path: 処理対象のCSVファイルのパス
        """
        projects_data: List[Dict[str, Any]] = []

        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # 各フィールドの値を適切な型に変換
                converted_row = {}
                for key, value in row.items():
                    converted_row[key] = self._parse_value(value)
                
                projects_data.append(converted_row)

        if not projects_data:
            print(f"⚠️ {csv_path.name} に有効なプロジェクトデータが見つかりませんでした。スキップします。")
            return

        # JSONの第一階層のキーをCSVファイル名（拡張子なし）にする
        root_key = csv_path.stem 
        
        json_output: Dict[str, Any] = {
            root_key: projects_data 
        }

        # JSONファイル名を作成
        json_filename = csv_path.stem + '.json'
        json_path = self.json_out_dir / json_filename

        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_output, jsonfile, ensure_ascii=False, indent=2)

        print(f"✅ {csv_path.name} を {json_path} に変換し保存しました。")
        print(f"   📊 {len(projects_data)} 件のレコードを変換しました。")