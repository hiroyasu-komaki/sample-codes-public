# JSON to Wordcloud Generator

CSVフォルダに格納されたCSVファイルを、JSON形式に変換して出力するPythonプログラムです。

## 機能

- CSVファイルからファイル構造を読み取り、JSONファイルに保存

## 必要要件

- Python 3.8以上

## セットアップ

### 1. 仮想環境の作成（venv使用）

```bash
# 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化（macOS/Linux）
source venv/bin/activate

# 仮想環境を有効化（Windows）
venv\Scripts\activate
```

### 2. 依存ライブラリのインストール

仮想環境を有効化した状態で、必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

### 3. フォルダ構成

プログラムを実行すると、以下のフォルダが自動的に作成されます：

```
project/
├── main.py
├── csv2json_converter.py
├── requirements.txt
├── README.md
├── json/         # JSONファイルを配置（出力）
└── csv/          # CSVファイルを格納（入力）
```

## 使い方

### 1. CSVファイルの配置

`csv/` フォルダに処理したいCSVファイルを配置します。

### 2. プログラムの実行

仮想環境を有効化した状態で実行します。

```bash
python3 main.py
```

### 3. 仮想環境の終了（作業終了時）

```bash
deactivate
```

### 4. 結果の確認

- `json/` フォルダに抽出されたJSONファイルが保存されます

<br>

## モジュール説明

### main.py
エントリポイント。csv2json_converterの呼び出しを行います。

### csv2json_converter.py
CSVファイルからJSONを抽出するクラス

**主なメソッド：**

<br>

## ライセンス

このプロジェクトはオープンソースです。自由に使用・改変できます。
