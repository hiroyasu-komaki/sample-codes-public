import csv
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

class Csv2CsvConverter:
    """
    CSVファイルの統合変換クラス。
    元のCSVを読み込み、ヘッダ変換・新規項目追加・レイアウト変更を一度に実行します。
    """

    def __init__(self, 
                 in_dir_path: str = 'in', 
                 out_dir_path: str = 'out',
                 config_dir_path: str = 'config'):
        """
        コンバータを初期化します。

        :param in_dir_path: 入力CSVファイルのディレクトリパス
        :param out_dir_path: 出力CSVファイルのディレクトリパス
        :param config_dir_path: 設定ファイル（YAML）のディレクトリパス
        """
        self.in_dir = Path(in_dir_path)
        self.out_dir = Path(out_dir_path)
        self.config_dir = Path(config_dir_path)
        self._ensure_dirs()

    def _ensure_dirs(self):
        """
        必要なディレクトリが存在することを確認し、なければ作成します。
        """
        self.in_dir.mkdir(exist_ok=True)
        self.out_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        print(f"✅ ディレクトリ構成を確認/作成しました。")
        print(f"   Input: {self.in_dir}")
        print(f"   Output: {self.out_dir}")
        print(f"   Config: {self.config_dir}")

    def _load_config(self, config_path: Path) -> Optional[Tuple[List[str], List[str], List[Dict[str, Any]]]]:
        """
        YAML設定ファイルを読み込み、ヘッダ情報とマッピングを取得します。

        :param config_path: 設定ファイルのパス
        :return: (入力ヘッダリスト, 出力ヘッダリスト, マッピングリスト) のタプル、エラー時はNone
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            if not config:
                print(f"⚠️ {config_path.name} が空または無効です。")
                return None
            
            # 入力ヘッダを取得
            input_headers = config.get('input_headers', [])
            if not input_headers:
                print(f"⚠️ {config_path.name} に 'input_headers' が見つかりません。")
                return None
            
            # 出力ヘッダを取得
            output_headers = config.get('output_headers', [])
            if not output_headers:
                print(f"⚠️ {config_path.name} に 'output_headers' が見つかりません。")
                return None
            
            # マッピング情報を取得
            header_mapping = config.get('header_mapping', [])
            if not header_mapping:
                print(f"⚠️ {config_path.name} に 'header_mapping' が見つかりません。")
                return None
            
            # マッピングの検証
            if not isinstance(header_mapping, list):
                print(f"⚠️ {config_path.name} の 'header_mapping' はリスト形式である必要があります。")
                return None
                
            return (input_headers, output_headers, header_mapping)
            
        except yaml.YAMLError as e:
            print(f"❌ YAML解析エラー ({config_path.name}): {e}")
            return None
        except Exception as e:
            print(f"❌ 設定ファイル読み込みエラー ({config_path.name}): {e}")
            return None

    def _find_config_for_csv(self, csv_filename: str) -> Optional[Path]:
        """
        CSVファイルに対応する設定ファイルを検索します。
        命名規則: <csv_name>.yaml または <csv_name>_config.yaml または default.yaml

        :param csv_filename: CSVファイル名（拡張子なし）
        :return: 設定ファイルのパス、見つからない場合はNone
        """
        # パターン1: <csv_name>.yaml（優先）
        config_path1 = self.config_dir / f"{csv_filename}.yaml"
        if config_path1.exists():
            return config_path1
            
        # パターン2: <csv_name>_config.yaml
        config_path2 = self.config_dir / f"{csv_filename}_config.yaml"
        if config_path2.exists():
            return config_path2
            
        # パターン3: default.yaml（デフォルト設定）
        default_config = self.config_dir / "default.yaml"
        if default_config.exists():
            print(f"ℹ️ {csv_filename}.csv 専用の設定が見つからないため、default.yaml を使用します。")
            return default_config
            
        return None

    def convert_all(self):
        """
        inディレクトリ内の全てのCSVファイルを処理し、
        ヘッダ変換・新規項目追加・レイアウト変更を行ってoutディレクトリに保存します。
        """
        csv_files = list(self.in_dir.glob('*.csv'))

        if not csv_files:
            print(f"⚠️ {self.in_dir} フォルダにCSVファイルが見つかりませんでした。")
            return

        print(f"\n📄 {len(csv_files)} 個のCSVファイルを検出しました。変換を開始します。\n")

        for csv_file in csv_files:
            try:
                self._convert_single_file(csv_file)
            except Exception as e:
                print(f"❌ ファイル {csv_file.name} の処理中にエラーが発生しました: {e}\n")

        print("✨ すべてのファイルの変換が完了しました。")

    def _convert_single_file(self, csv_path: Path):
        """
        単一のCSVファイルを読み込み、ヘッダ変換・新規項目追加・レイアウト変更を実行します。

        :param csv_path: 処理対象のCSVファイルのパス
        """
        print(f"🔄 処理中: {csv_path.name}")
        
        # 対応する設定ファイルを検索
        config_path = self._find_config_for_csv(csv_path.stem)
        
        if not config_path:
            print(f"⚠️ {csv_path.name} に対応する設定ファイルが見つかりません。スキップします。\n")
            return
            
        # 設定ファイルを読み込み
        config_result = self._load_config(config_path)
        
        if not config_result:
            print(f"⚠️ 有効な設定情報が取得できませんでした。スキップします。\n")
            return
        
        input_headers, output_headers, header_mapping = config_result
        
        print(f"   📋 設定ファイル: {config_path.name}")
        
        # CSVファイルを読み込み
        rows: List[Dict[str, Any]] = []
        actual_headers: List[str] = []
        
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                actual_headers = reader.fieldnames or []
                
                for row in reader:
                    rows.append(row)
                    
        except Exception as e:
            print(f"❌ CSVファイル読み込みエラー: {e}\n")
            return
        
        if not rows:
            print(f"⚠️ {csv_path.name} にデータが見つかりませんでした。スキップします。\n")
            return
        
        print(f"   📝 入力ヘッダ数: {len(actual_headers)}")
        print(f"   📝 出力ヘッダ数: {len(output_headers)}")
        
        # 実際のCSVヘッダと設定ファイルの入力ヘッダを検証
        if actual_headers != input_headers:
            print(f"   ⚠️ 警告: CSVのヘッダと設定ファイルの input_headers が一致しません。")
            print(f"      実際のCSV: {', '.join(actual_headers[:5])}{'...' if len(actual_headers) > 5 else ''}")
            print(f"      設定ファイル: {', '.join(input_headers[:5])}{'...' if len(input_headers) > 5 else ''}")
            print(f"      設定ファイルのマッピングを使用して変換を試みます。")
        
        # マッピング情報を処理
        print(f"   🔄 変換内容:")
        
        # 既存フィールドと新規フィールドを分類
        existing_fields = []
        new_fields = []
        
        for mapping in header_mapping:
            input_field = mapping.get('input')
            output_field = mapping.get('output')
            default_value = mapping.get('default_value', '')
            
            if input_field is None or input_field == 'null':
                new_fields.append({
                    'output': output_field,
                    'default': default_value,
                    'description': mapping.get('description', '')
                })
            else:
                existing_fields.append({
                    'input': input_field,
                    'output': output_field
                })
        
        print(f"      既存フィールド変換: {len(existing_fields)} 個")
        print(f"      新規フィールド追加: {len(new_fields)} 個")
        
        if new_fields:
            print(f"   ➕ 新規追加フィールド:")
            for field in new_fields:
                default_display = f"(デフォルト値: '{field['default']}')" if field['default'] else "(空)"
                print(f"      - {field['output']} {default_display}")
        
        # 出力CSVファイルを作成
        output_path = self.out_dir / csv_path.name
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=output_headers)
                writer.writeheader()
                
                # データ行を書き込み
                for row in rows:
                    new_row = {}
                    
                    # output_headersの順序に従って値を設定
                    for output_header in output_headers:
                        # マッピングを検索
                        value = None
                        
                        # 既存フィールドから検索
                        for field in existing_fields:
                            if field['output'] == output_header:
                                value = row.get(field['input'], '')
                                break
                        
                        # 新規フィールドから検索
                        if value is None:
                            for field in new_fields:
                                if field['output'] == output_header:
                                    value = field['default']
                                    break
                        
                        # 値が見つからない場合は空文字
                        if value is None:
                            value = ''
                        
                        new_row[output_header] = value
                    
                    writer.writerow(new_row)
                    
        except Exception as e:
            print(f"❌ CSV書き込みエラー: {e}\n")
            return
        
        print(f"   ✅ 変換完了: {output_path}")
        print(f"   📊 {len(rows)} 行のデータを変換しました。\n")
