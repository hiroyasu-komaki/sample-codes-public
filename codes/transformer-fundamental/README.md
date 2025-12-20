# Transformer Attention 可視化プログラム

このプログラムは、TransformerのAttentionメカニズムを擬似的に可視化します。

## 📁 ディレクトリ構成

```
.
├── main.py                    # メインエントリポイント
├── modules/                   # モジュールディレクトリ
│   ├── __init__.py           # パッケージ初期化
│   └── transformer.py        # Transformerクラス
├── requirements.txt          # 必要なライブラリ
└── output/                   # 出力画像（実行後に作成）
    ├── attention_understanding.png
    ├── attention_generation.png
    └── attention_generation_detail.png
```

## 環境構築

### 仮想環境を作成
python3 -m venv venv

### 仮想環境を有効化（macOS/Linux）
source venv/bin/activate


## 🚀 インストール

### 1. 必要なライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. プログラムの実行

```bash
python main.py
```

または

```bash
python3 main.py
```

## 📊 出力される可視化

### 1. attention_understanding.png
- 文章理解のプロセス
- 各単語が他の単語にどれだけ注目しているかをヒートマップで表示
- 例文：「私が公園を歩いているとき向こうから犬が歩いてきた。私はその犬を見た。」

### 2. attention_generation.png
- 文章生成のプロセス
- 「犬について教えて」という入力から「犬は哺乳類です」を生成する各ステップ
- Causal Masking（未来を見ない制約）を表現

### 3. attention_generation_detail.png
- 1つの生成ステップの詳細
- Query-Key-Valueの仕組み
- 重み付け平均の計算過程
- 次の単語の予測確率

## 🧠 学習できる内容

- Transformerの基本的な動作原理
- Self-Attentionメカニズム
- Query、Key、Valueの役割
- 文章生成の自己回帰的プロセス
- Causal Maskingの重要性

## 📝 ライセンス

このプログラムは教育目的で作成されています。
自由に使用・改変してください。

## 🔧 カスタマイズ

`modules/transformer.py`の`SimpleTransformer`クラスを編集することで、
以下のカスタマイズが可能です：

- 異なる文章での可視化
- Attentionスコアの計算ロジックの変更
- 出力画像のスタイル変更

## 📚 参考資料

- "Attention Is All You Need" (Vaswani et al., 2017)
- https://arxiv.org/abs/1706.03762
