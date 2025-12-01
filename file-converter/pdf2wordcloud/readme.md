# PDF to Wordcloud Generator

PDFファイルからテキストを抽出し、Wordcloud（ワードクラウド）を生成するPythonプログラムです。

## 機能

- PDFファイルからテキストを抽出してTXTファイルに保存
- テキストファイルからWordcloudを生成してPNG画像として保存
- CSVファイルでストップワードをカスタマイズ可能

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
├── pdf_extractor.py
├── wordcloud_generator.py
├── stopwords.csv
├── requirements.txt
├── README.md
├── venv/         # 仮想環境（自動作成）
├── pdf/          # PDFファイルを配置（自動作成）
├── txt/          # 抽出されたテキストファイル（自動作成）
└── png/          # 生成されたWordcloud画像（自動作成）
```

**注意:** `venv/` フォルダは仮想環境なので、Gitにコミットしないでください（.gitignoreに追加推奨）。

## 使い方

### 1. PDFファイルの配置

`pdf/` フォルダに処理したいPDFファイルを配置します。

```bash
cp your_document.pdf pdf/
```

### 2. ストップワードの設定（オプション）

`stopwords.csv` を編集して、Wordcloudから除外したい単語を設定します。
デフォルトでは日本語の一般的な助詞・接続詞が設定されています。

カンマ区切りで単語を追加できます：

```csv
の,に,は,を,た,が,あなたの除外単語1,あなたの除外単語2
```

### 3. プログラムの実行

仮想環境を有効化した状態で実行します。

```bash
python3 main.py
```

### 4. 仮想環境の終了（作業終了時）

```bash
deactivate
```

### 5. 結果の確認

- `txt/` フォルダに抽出されたテキストファイルが保存されます
- `png/` フォルダに生成されたWordcloud画像が保存されます

## 日本語PDFの処理

日本語のPDFファイルを処理する場合、Wordcloud生成時に日本語フォントの指定が必要です。

`wordcloud_generator.py` の `generate_wordcloud` メソッド内の `font_path` パラメータを編集してください：

### macOSの場合

```python
wordcloud = WordCloud(
    width=800,
    height=600,
    background_color='white',
    stopwords=self.stopwords,
    font_path='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',  # 日本語フォント
    collocations=False
).generate(text)
```

### Windowsの場合

```python
font_path='C:\\Windows\\Fonts\\msgothic.ttc'  # MS ゴシック
```

### Linuxの場合

```python
font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'  # Noto Sans CJK
```

## モジュール説明

### main.py
エントリポイント。フォルダの作成、PDFExtractorとWordCloudGeneratorの呼び出しを行います。

### pdf_extractor.py
PDFファイルからテキストを抽出するクラス `PDFExtractor` を提供します。

**主なメソッド：**
- `extract_text_from_pdf(pdf_path)`: 指定されたPDFからテキストを抽出
- `save_text_to_file(text, output_path)`: テキストをファイルに保存
- `extract_all()`: pdf/フォルダ内のすべてのPDFを処理

### wordcloud_generator.py
テキストファイルからWordcloudを生成するクラス `WordCloudGenerator` を提供します。

**主なメソッド：**
- `load_stopwords(stopwords_file)`: CSVファイルからストップワードを読み込み
- `read_text_file(txt_path)`: テキストファイルを読み込み
- `generate_wordcloud(text, output_path)`: Wordcloudを生成して保存
- `generate_all()`: txt/フォルダ内のすべてのテキストファイルを処理

## トラブルシューティング

### PDFからテキストが抽出できない場合

- PDFが画像のみで構成されている場合、テキスト抽出はできません
- スキャンされたPDFの場合は、OCR処理が必要です

### Wordcloudが生成されない場合

- テキストファイルが空でないか確認してください
- 日本語の場合、適切なフォントが指定されているか確認してください
- ストップワードが多すぎて単語が残っていない可能性があります
