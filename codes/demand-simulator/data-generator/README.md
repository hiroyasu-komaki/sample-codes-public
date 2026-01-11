# サンプルデータ生成ツール

YAMLファイルでデータ定義を読み込み、サンプルデータをCSV形式で出力するツールです。

## 必要要件

- Python 3.8以上

## セットアップ

### 0. 仮想環境
```
# 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化（macOS/Linux）
source venv/bin/activate

# 仮想環境を有効化（Windows）
venv\Scripts\activate
```

### 1. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

<br>

## 使い方

### 基本的な使い方

YAMLファイルで設定を行い、プログラムを実行するだけです。

```bash
python sample_data_generator.py
```

### 設定ファイル（data_definition.yaml）

```yaml
# データ項目の定義
fields:
  - 案件ID
  - 案件名
  - 初期投資金額
  - 運用費
  - システム利用開始時期

# 出力設定
output:
  file: sample_data.csv  # 出力ファイル名
  records: 100           # 生成するレコード数
```

レコード数や出力ファイル名を変更したい場合は、YAMLファイルを編集してください。

例：
```yaml
output:
  file: output_data.csv  # 出力ファイル名を変更
  records: 500           # 500件生成に変更
```

## データ定義ファイル（YAML）

`data_definition.yaml` でデータ項目と生成設定を定義します。

### フィールド定義

```yaml
fields:
  - 案件ID
  - 案件名
  - 初期投資金額
  - 運用費
  - システム利用開始時期
```

### 出力設定

```yaml
output:
  file: sample_data.csv  # 出力ファイル名
  records: 100           # 生成するレコード数
```

### 詳細設定（オプション）

```yaml
settings:
  # 初期投資金額の範囲（単位：万円）
  initial_investment:
    min: 100
    max: 50000
  
  # 運用費の割合（初期投資金額に対する比率）
  operation_cost_ratio:
    min: 0.05
    max: 0.20
  
  # システム利用開始時期の範囲
  start_date:
    from_days_ago: 365  # 過去1年前から
    to_days_ahead: 730  # 未来2年後まで
```

## 生成されるデータの仕様

### 案件ID
- フォーマット: `PRJ0001`, `PRJ0002`, ...
- 4桁のゼロパディング連番

### 案件名
- ランダムに生成されるプロジェクト名
- 例: "次世代販売管理システム構築プロジェクト"

### 初期投資金額
- 範囲: 100万円〜5億円
- キリの良い数字で生成

### 運用費
- 初期投資金額の5〜20%程度
- キリの良い数字で生成

### システム利用開始時期
- フォーマット: `YYYY/MM/DD`
- 範囲: 現在から過去1年〜未来2年

## 出力例

```csv
案件ID,案件名,初期投資金額,運用費,システム利用開始時期
PRJ0001,次世代販売管理システム構築プロジェクト,15000,2250,2025/03/15
PRJ0002,DX推進会計システム導入プロジェクト,8500,1020,2024/11/20
PRJ0003,クラウドECサイト開発プロジェクト,3200,512,2026/06/10
```

## ファイル構成

```
.
├── sample_data_generator.py  # メインプログラム
├── data_definition.yaml      # データ定義ファイル
├── requirements.txt          # 必要なライブラリ
├── README.md                 # このファイル
└── sample_data.csv          # 出力ファイル（実行後に生成）
```

## カスタマイズ

生成されるデータをカスタマイズしたい場合は、`sample_data_generator.py` の以下のメソッドを修正してください：

- `_generate_project_name()`: 案件名の生成ロジック
- `_generate_initial_investment()`: 初期投資金額の範囲
- `_generate_operation_cost()`: 運用費の計算方法
- `_generate_start_date()`: システム利用開始時期の範囲
