# WordCloud生成ツール

日本語・英語テキストから美しいWordCloudを自動生成するPythonツールです。

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
├── README.md                 # このファイル
├── .gitignore               # Git除外設定
├── in/                      # 入力ファイル格納フォルダ
│   ├── sample.txt
│   ├── data.csv
│   └── document.md
└── out/                     # 出力ファイル格納フォルダ
    ├── sample_wordcloud.png
    ├── data_wordcloud.png
    └── document_wordcloud.png
```

## 🚀 クイックスタート

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

## 📖 使用方法

### 基本的な使い方

1. `in/`フォルダに処理したいテキストファイル（`.txt`, `.csv`, `.md`）を配置
2. `python main.py`を実行
3. `out/`フォルダに生成されたWordCloud（PNG形式）が保存されます

### カスタマイズ

`main.py`の`wordcloud_params`を編集することでWordCloudをカスタマイズできます：

```python
wordcloud_params = {
    'width': 1200,              # 幅
    'height': 600,              # 高さ
    'background_color': 'white', # 背景色
    'max_words': 150,           # 最大単語数
    'colormap': 'viridis',      # カラーマップ
    'relative_scaling': 0.5,    # 文字サイズの相対スケール
    'min_font_size': 10         # 最小フォントサイズ
}
```

## 🔧 依存ライブラリ

- **wordcloud**: WordCloud生成
- **matplotlib**: グラフ表示・画像保存
- **numpy**: 数値計算
- **pillow**: 画像処理
- **mecab-python3**: 日本語形態素解析（オプション）
- **nltk**: 英語テキスト処理（オプション）
- **pandas**: データ処理

## 📄 ライセンス

MIT License
