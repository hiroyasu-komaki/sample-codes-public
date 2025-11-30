# ローカルRAG検索システム

- Chromaベクトルデータベースを使用したRAG（Retrieval-Augmented Generation）検索システムです
- **PDF、TXT、MDファイル**から情報を抽出し、自然言語での意味的検索を可能にします。

## 特徴

- 🔍 **自然言語検索**: 日本語・英語対応の意味的検索
- 📚 **マルチフォーマット対応**: PDF、TXT、MDファイルを一括処理
- 💾 **ローカル処理**: インターネット接続不要でプライベート
- ⚡ **高速検索**: Chromaベクトルデータベースによる高速類似検索
- 🎯 **高精度**: sentence-transformersによる多言語埋め込み
- 🔄 **対話型インターフェース**: メニュー形式で簡単操作
- 📊 **動的閾値**: 検索結果に応じた類似度判定
- 🏗️ **モジュラー設計**: 責任分離された3つのモジュール

## 📂 ファイル構成

```
rag-cli-system/
├── main.py                         # メインプログラム（対話型UI）
├── modules/
│   ├── utils.py                    # 共通ユーティリティ
│   ├── database_builder.py         # データベース構築クラス
│   └── database_searcher.py        # データベース検索クラス
├── data/                           # データフォルダ
│   ├── pdf/                        # PDFファイル格納先
│   ├── txt/                        # TXTファイル格納先
│   └── md/                         # MDファイル格納先
├── vectordb/                       # ベクトルデータベース保存先（dataと同列）
├── results/                        # 検索結果保存先（自動作成）
├── requirements.txt                # 必要なライブラリ
└── README.md                       # このファイル
```

## 🏗️ アーキテクチャ

### モジュール構成

このシステムは責任を明確に分離した3つのモジュールで構成されています：

#### 1. **utils.py** - 共通ユーティリティ
- ログ設定
- 出力抑制
- 埋め込みモデル作成
- ドキュメントローダー（PDF/TXT/MD）
- ディレクトリ管理

#### 2. **database_builder.py** - データベース構築
- `DatabaseBuilder`クラス
- ドキュメントの読み込み
- テキストのチャンク分割
- ベクトル化とDB構築
- DB再構築

#### 3. **database_searcher.py** - データベース検索
- `DatabaseSearcher`クラス
- DBの読み込み
- 類似検索の実行
- ファイルタイプ別検索
- 統計情報の取得

### クラス図

```
┌─────────────────┐
│  DatabaseBuilder│
├─────────────────┤
│ + build()       │
│ + rebuild()     │
└────────┬────────┘
         │ uses
         ▼
┌─────────────────┐
│     utils       │
├─────────────────┤
│ + load_docs()   │
│ + embeddings()  │
└─────────────────┘
         ▲
         │ uses
┌────────┴────────┐
│DatabaseSearcher │
├─────────────────┤
│ + load()        │
│ + search()      │
└─────────────────┘
```

## 🚀 セットアップ

### 1. 仮想環境の作成と有効化

```bash
# 仮想環境作成
python3 -m venv venv

# 仮想環境の有効化
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2. 必要なディレクトリの作成

```bash
mkdir -p data/pdf data/txt data/md modules
```

### 3. 依存関係のインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. モジュールの配置

以下のファイルを`modules/`フォルダに配置してください：
- `utils.py`
- `database_builder.py`
- `database_searcher.py`

## 📖 使用方法

### 1. ドキュメントの配置

検索対象のファイルを以下のフォルダに配置してください：

- **PDFファイル**: `data/pdf/` フォルダ
- **TXTファイル**: `data/txt/` フォルダ
- **MDファイル**: `data/md/` フォルダ

### 2. プログラムの起動

```bash
python3 main.py
```

### 3. メニュー操作

プログラムを起動すると、メニューが表示されます：

```
============================================================
🔍 ローカルRAG検索システム (対話型・拡張版)
Powered by Chroma Vector Database
対応フォーマット: PDF / TXT / MD
============================================================
📁 PDFフォルダ: data/pdf
📁 TXTフォルダ: data/txt
📁 MDフォルダ: data/md
💾 データベースフォルダ: vectordb

============================================================
📋 メニュー
============================================================
1. ベクトルデータベースを再構築
2. ベクトルデータベースを検索
9. プログラムを終了
============================================================

選択してください (1/2/9): 
```

#### メニューオプション

**1. ベクトルデータベースを再構築**
- `DatabaseBuilder`が全ファイルを読み込み
- ベクトルデータベースを新規作成
- メニューに戻る

**2. ベクトルデータベースを検索**
- `DatabaseSearcher`が既存DBを読み込み
- 検索モードへ移行

**9. プログラムを終了**
- プログラムを終了

### 4. 検索の実行

検索モードでは以下の操作が可能です：

```
🔍 検索ワードを入力してください (メニューに戻る: 'menu', 終了: 'exit'): 
```

- **検索ワード入力**: 自由に検索
- **`menu`**: メインメニューに戻る
- **`exit`**: プログラムを終了

## 🎯 動的閾値の仕組み

各検索で返される結果のスコア分布に基づいて、自動的に閾値が計算されます：

- **高類似度閾値** = 最小スコア + (スコア範囲 × 0.33)
- **中類似度閾値** = 最小スコア + (スコア範囲 × 0.67)

この仕組みにより、検索クエリごとに最適な分類が行われます。

## 💾 検索結果の保存

検索結果は自動的に `results/` フォルダにテキストファイルとして保存されます。

### ファイル名形式
```
search_YYYYMMDD_HHMMSS_クエリ名.txt
```

例: `search_20241127_143022_Deep_Learning.txt`

## 📊 ファイルタイプ別のアイコン

検索結果には、ファイルタイプに応じたアイコンが表示されます：

- 📕 **PDF**: PDFドキュメント
- 📝 **TXT**: テキストファイル
- 📋 **MD**: Markdownファイル

## 🔧 技術仕様

### ベクトル処理
- **ベクトルデータベース**: Chroma
- **埋め込みモデル**: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- **距離メトリック**: L2距離（ユークリッド距離）
- **類似度判定**: 動的閾値による3段階分類

### ドキュメント処理
- **PDFローダー**: PyPDFLoader（ページ単位で読み込み）
- **TXTローダー**: TextLoader（UTF-8エンコーディング）
- **MDローダー**: TextLoader（Markdown構造を保持）

### テキスト分割
- **チャンクサイズ**: 1000文字（デフォルト）
- **オーバーラップ**: 200文字（デフォルト）
- **分割方式**: RecursiveCharacterTextSplitter

## 💡 使用例

### 初回起動時

1. プログラムを起動: `python3 main.py`
2. メニューで `1` を選択（データベース再構築）
3. `DatabaseBuilder`がドキュメントを読み込み
4. ベクトル化とDB構築が実行される
5. メニューに戻る
6. メニューで `2` を選択（検索モード）
7. `DatabaseSearcher`で検索モードへ
8. 自由に検索を実行
9. `menu` でメニューに戻る、または `exit` で終了

### 2回目以降の起動

1. プログラムを起動: `python3 main.py`
2. メニューで `2` を選択（既存データベース使用）
3. `DatabaseSearcher`が既存DBを読み込み
4. すぐに検索モードが起動
5. 検索を実行

### ファイル追加後

1. 新しいファイルを `data/pdf/`, `data/txt/`, `data/md/` に追加
2. プログラムを起動
3. メニューで `1` を選択（データベース再構築）
4. `DatabaseBuilder`が新ファイルを含めて再構築
5. メニューに戻る
6. メニューで `2` を選択（検索モード）

## 🏗️ 拡張性

### カスタムパラメータ

各クラスは柔軟なパラメータを受け付けます：

```python
# DatabaseBuilder
builder = DatabaseBuilder(
    pdf_folder="data/pdf",
    txt_folder="data/txt",
    md_folder="data/md",
    db_folder="vectordb",
    chunk_size=1000,        # カスタマイズ可能
    chunk_overlap=200,       # カスタマイズ可能
    collection_name="rag_documents",
    verbose=True
)

# DatabaseSearcher
searcher = DatabaseSearcher(
    db_folder="vectordb",
    collection_name="rag_documents",
    verbose=True
)
```

### 新機能の追加

モジュラー設計により、以下のような拡張が容易です：

- 新しいファイルフォーマットの追加（utils.pyに関数追加）
- 別の埋め込みモデルの使用（utils.pyで変更）
- カスタム検索フィルターの実装（database_searcher.py）
- バッチ処理機能（database_builder.py）

## 📋 requirements.txt

```
# コアRAGライブラリ
langchain>=0.1.0
langchain-community>=0.0.20

# ベクトルデータベース
chromadb>=0.4.0

# 埋め込みモデル
sentence-transformers>=2.2.0
transformers>=4.21.0
torch>=1.13.0

# PDFファイル処理
pypdf>=3.0.0

# その他
numpy>=1.24.0
tqdm>=4.64.0
```

## 📜 ライセンス

このプロジェクトはMITライセンスの下で公開されています。