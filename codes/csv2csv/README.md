# CSV to CSV Converter（統合版）

CSVファイルのヘッダ変換、新規項目追加、レイアウト変更を一度に実行するPythonプログラムです。

## 主な特徴

✅ **統合処理**: ヘッダ変換・新規項目追加・レイアウト変更を1ステップで完了
✅ **YAML設定駆動**: コード変更不要で柔軟に設定変更可能
✅ **新規フィールド追加**: デフォルト値を指定して新しいカラムを挿入
✅ **カラム順序変更**: 出力時のカラムの並び順を自由に設定
✅ **詳細なログ**: 変換内容を視覚的に表示
✅ **バッチ処理**: 複数のCSVファイルを一度に処理

## ディレクトリ構成

```
.
├── main.py                    # エントリポイント
├── csv2csv_converter.py       # 変換処理の本体
├── in/                        # 入力CSVファイル配置場所
│   └── projects.csv
├── config/                    # 設定ファイル（YAML）配置場所
│   └── projects.yaml
└── out/                       # 出力CSVファイル保存場所（自動作成）
    └── projects.csv
```

## 使用方法

### 1. 入力CSVファイルを配置

`in/` フォルダに変換したいCSVファイルを配置します。

### 2. 設定ファイルを作成

`config/` フォルダに対応するYAML設定ファイルを作成します。

**命名規則**:
- `<csvファイル名>.yaml` （例: `projects.yaml`）
- `<csvファイル名>_config.yaml`
- `default.yaml` （全CSVに適用されるデフォルト設定）

### 3. プログラムを実行

```bash
python main.py
```

### 4. 出力を確認

`out/` フォルダに変換されたCSVファイルが保存されます。

## YAML設定ファイルの書き方

### 基本構造

```yaml
# 入力CSVのヘッダ情報
input_headers:
  - id
  - nameJA
  - nameEN
  - department

# 出力CSVのヘッダ情報（順序も指定）
output_headers:
  - プロジェクトID
  - プロジェクト名（日本語）
  - Project Name (English)
  - tags              # 新規追加フィールド
  - 担当部門

# マッピング情報
header_mapping:
  # 既存フィールドの変換
  - input: id
    output: プロジェクトID
    description: プロジェクトの一意識別子
  
  - input: nameJA
    output: プロジェクト名（日本語）
    description: プロジェクト名の日本語表記
  
  # 新規フィールドの追加
  - input: null
    output: tags
    description: プロジェクトタグ（新規追加）
    default_value: "[]"
```

### マッピングのルール

#### 既存フィールドの変換

```yaml
- input: 元のヘッダ名
  output: 新しいヘッダ名
  description: 説明（任意）
```

#### 新規フィールドの追加

```yaml
- input: null
  output: 新しいヘッダ名
  description: 説明（任意）
  default_value: "デフォルト値"
```

- `input: null` とすることで新規フィールドとして認識されます
- `default_value` で全行に挿入されるデフォルト値を指定します
- `default_value` を省略すると空文字が設定されます

## 実行例

### 入力（in/projects.csv）

```csv
id,nameJA,nameEN,department,status
crm-upgrade,CRMシステムアップグレード,CRM System Upgrade,it,on-track
cloud-migration,クラウドマイグレーション,Cloud Migration,it,delayed
```

### 設定（config/projects.yaml）

```yaml
input_headers:
  - id
  - nameJA
  - nameEN
  - department
  - status

output_headers:
  - プロジェクトID
  - プロジェクト名（日本語）
  - Project Name (English)
  - tags
  - 担当部門
  - ステータスコード

header_mapping:
  - input: id
    output: プロジェクトID
  - input: nameJA
    output: プロジェクト名（日本語）
  - input: nameEN
    output: Project Name (English)
  - input: null
    output: tags
    default_value: "[]"
  - input: department
    output: 担当部門
  - input: status
    output: ステータスコード
```

### 出力（out/projects.csv）

```csv
プロジェクトID,プロジェクト名（日本語）,Project Name (English),tags,担当部門,ステータスコード
crm-upgrade,CRMシステムアップグレード,CRM System Upgrade,[],it,on-track
cloud-migration,クラウドマイグレーション,Cloud Migration,[],it,delayed
```

## 実行時のログ出力

```
============================================================
  CSV to CSV Converter 起動
============================================================
✅ ディレクトリ構成を確認/作成しました。
   Input: in
   Output: out
   Config: config

📄 1 個のCSVファイルを検出しました。変換を開始します。

🔄 処理中: projects.csv
   📋 設定ファイル: projects.yaml
   📝 入力ヘッダ数: 17
   📝 出力ヘッダ数: 22
   🔄 変換内容:
      既存フィールド変換: 17 個
      新規フィールド追加: 5 個
   ➕ 新規追加フィールド:
      - tags (デフォルト値: '[]')
      - projects (デフォルト値: '[]')
      - eolStatus (空)
      - eolDate (空)
      - eolDateEN (空)
   ✅ 変換完了: out/projects.csv
   📊 12 行のデータを変換しました。

✨ すべてのファイルの変換が完了しました。
============================================================
  CSV to CSV Converter 終了
============================================================
```

