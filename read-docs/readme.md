# 情報検索・フィルタリングシステム

複数の手法（TF-IDF、Word2Vec、BERT）を使用した文書検索・フィルタリングシステムです。実行結果は自動的にテキストファイル、JSON、CSV形式で保存されます。

## セットアップ

```bash
# 仮想環境を作成
python3 -m venv venv

# 仮想環境をアクティベート
source venv/bin/activate

# 必要なパッケージ
pip install -r requirements.txt
```

## プログラムを実行

```
python3 main.py
```

## 📁 ファイル構成

```
project/
├── main.py                  # メイン実行ファイル（更新）
├── result_writer.py         # 結果出力クラス（変更なし）
├── search_methods/          # 検索クラス用フォルダ（新規）
│   ├── __init__.py          # パッケージ初期化ファイル
│   ├── base_search.py       # 基底検索クラス（移動）
│   ├── tfidf_search.py      # TF-IDF検索クラス（移動）
│   ├── word2vec_search.py   # Word2Vec検索クラス（移動）
│   └── bert_search.py       # BERT検索クラス（移動）
├── in/                      # 入力文書フォルダ
│   ├── document1.txt
│   ├── document2.md
│   └── ...
└── results/                 # 出力結果フォルダ
```

<br>

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。