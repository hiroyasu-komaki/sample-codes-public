# WordCloud生成ツール

日本語・英語テキストからWordCloudを自動生成するPythonツールです。

## 🌟 特徴

- **多言語対応**: 日本語（MeCab使用）・英語（NLTK使用）の自動検出と適切な前処理
- **複数ファイル形式対応**: `.txt`, `.csv`, `.md`ファイルに対応
- **一括処理**: `in`フォルダ内のファイルを自動検出して一括処理
- **高品質出力**: PNG形式（300dpi）で高解像度な画像を生成
- **カスタマイズ可能**: WordCloudのパラメータを簡単に調整可能

## 📁 フォルダ構成

```
wordcloud-generator/
├── main.py                    # メイン実行ファイル
├── WordCloudGenerator.py      # WordCloud生成クラス
├── requirements.txt           # 必要なライブラリ
├── in/                      # 入力ファイル格納フォルダ
└── out/                     # 出力ファイル格納フォルダ
```

## セットアップ

### 1. 環境準備

```bash
# 仮想環境を作成
python -m venv venv
source venv/bin/activate

# 必要なライブラリをインストール
pip install -r requirements.txt
```

### 2. 日本語処理用ライブラリのインストール（オプション）

```bash
brew install mecab mecab-ipadic
pip install mecab-python3
```

### 3. 実行方法

```bash
# 1. inフォルダにテキストファイルを配置
cp your_text_file.txt in/

# 2. WordCloud生成を実行
python main.py

# 3. outフォルダで結果を確認
ls out/
```

## ライセンス

MIT License
