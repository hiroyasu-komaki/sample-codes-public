# sample-codes-public リポジトリガイド

複数のデータ分析・処理プロジェクトを含む総合リポジトリです。各プロジェクトは独立した機能を提供します。

---

## 📁 プロジェクト一覧

### 1. **data-generator** - サンプルデータ生成プログラム
YAML設定ファイルに基づいたサンプルデータを自動生成するツール
- **用途**: テストデータやサンプルデータの効率的な生成
- **言語**: Python
- **セットアップ**: `pip install -r requirements.txt`
- **実行**: `python main.py`

---

### 2. **ppm-dashboardapp** - IT Portfolio Dashboard
ITポートフォリオ管理ダッシュボードアプリケーション
- **機能**:
  - IT Portfolio Dashboard - 予算配分とROI分析
  - Project View - プロジェクト鳥瞰図
  - Application Layer View - アプリケーション鳥瞰図
- **技術**: Vanilla JavaScript (ES6+), Tailwind CSS, JSON
- **セットアップ**: `npm install` / `npm run dev`

---

### 3. **project-cluster** - Project Portfolio Analyzer
プロジェクトポートフォリオの生成と分析システム
- **機能**:
  - 自動データ生成（5業界対応）
  - ポートフォリオ分析と類似度分析
  - デンドログラム・t-SNE散布図可視化
- **言語**: Python
- **実行**: `python main.py`
- **出力**: CSV, PNG（デンドログラム）

---

### 4. **read-docs** - 情報検索・フィルタリングシステム
複数の手法を使用した文書検索・フィルタリングシステム
- **検索手法**: TF-IDF, Word2Vec, BERT
- **言語**: Python
- **セットアップ**: `pip install -r requirements.txt`
- **実行**: `python main.py`
- **出力**: テキスト, JSON, CSV形式

---

### 5. **sentiment-analysis** - 感情分析比較検証システム
日本語テキストの3モデル感情分析システム
- **モデル**:
  - jarvisx17/japanese-sentiment-analysis (Transformer)
  - koheiduck/bert-japanese-finetuned-sentiment
  - 辞書ベースモデル
- **言語**: Python
- **必要な環境**: Python 3.8以上, PyTorch, Transformers
- **実行**: `python main.py`

---

### 6. **skill/skilldata-generator** - Digital Skill Standard System
YAMLベースのマスターデータからスキルデータセットを生成
- **機能**:
  - スキル標準CSV生成
  - 10種類の戦略的サンプルデータ生成
  - データ統合・検証
- **言語**: Python
- **実行**: `python main.py`
- **出力**: CSV, YAML形式

---

### 7. **skill/skilldata_visualizer** - Skill Data Analyzer
スキルデータの可視化・分析ツール
- **分析機能**:
  - 個人プロファイル分析（レーダーチャート）
  - 組織分析（箱ひげ図）
  - スキル標準作成
- **言語**: Python
- **セットアップ**: `pip install pandas matplotlib seaborn numpy`

---

### 8. **survey-analysis** - IT部門サービス満足度アンケート分析
統計アプローチに基づく包括的なアンケートデータ分析システム
- **機能**:
  - サンプルデータ自動生成
  - 統計的分析（平均、分散、相関分析）
  - 詳細レポート生成
- **言語**: Python
- **実行**: `python main.py`
- **出力**: CSV, TXT形式

---

### 9. **vendor-qbr-analysis** - ベンダーQBR評価分析システム
ベンダー評価の包括的な分析・可視化システム
- **分析ステップ**:
  - データクレンジング
  - バイアス分析
  - ベンダー総合評価
  - 統計的検定
  - セグメント分析
  - 可視化・レポート生成
- **言語**: Python
- **実行**: `python main.py --config config/config.yaml`
- **出力**: CSV, PDF, PNG形式
- **関連ドキュメント**: MODULE_GUIDE.md - モジュール実装ガイド

---

### 10. **wordcloud** - WordCloud生成ツール
日本語・英語テキストからWordCloudを自動生成
- **対応形式**: .txt, .csv, .md
- **言語**: Python
- **セットアップ**: 
  ```bash
  pip install -r requirements.txt
  # 日本語対応（オプション）
  brew install mecab mecab-ipadic
  ```
- **実行**: `python main.py`
- **出力**: PNG画像

---

## 🚀 クイックスタート

### 1. リポジトリをクローン
```bash
git clone <repository-url>
cd sample-codes-public
```

### 2. 各プロジェクトのセットアップ
```bash
# 特定のプロジェクトに移動
cd <project-folder>

# 仮想環境作成（Python系プロジェクト）
python -m venv venv
source venv/bin/activate  # Linux/macOS: venv\Scripts\activate (Windows)

# 依存関係インストール
pip install -r requirements.txt  # Python系
# または
npm install  # JavaScript系
```

### 3. プロジェクトを実行
各プロジェクトの README を参照してください

---

## 📊 プロジェクト比較表

| プロジェクト | 言語 | 主要機能 | 出力形式 |
|-----------|------|--------|--------|
| data-generator | Python | データ生成 | CSV, JSON |
| ppm-dashboardapp | JavaScript | ポートフォリオ管理 | Web UI |
| project-cluster | Python | ポートフォリオ分析 | CSV, PNG |
| read-docs | Python | 文書検索 | TXT, JSON, CSV |
| sentiment-analysis | Python | 感情分析 | CSV, TXT |
| skilldata-generator | Python | スキルデータ生成 | CSV |
| skilldata_visualizer | Python | スキル可視化 | PNG |
| survey-analysis | Python | アンケート分析 | CSV, TXT |
| vendor-qbr-analysis | Python | ベンダー評価分析 | CSV, PDF, PNG |
| wordcloud | Python | WordCloud生成 | PNG |

---

## 📋 共通要件

### Python プロジェクト
- **Python バージョン**: 3.7以上推奨
- **仮想環境**: venv 推奨

### JavaScript プロジェクト
- **Node.js**: 14以上
- **npm**: 6以上

---

## 🔧 セットアップのトラブルシューティング

### Python モジュールが見つからない
```bash
# 仮想環境が有効になっているか確認
which python

# requirements.txt をもう一度実行
pip install -r requirements.txt
```

### 日本語フォント関連のエラー（matplotlib利用時）
```bash
# macOS
brew install font-noto-cjk

# Linux
sudo apt-get install fonts-noto-cjk
```

### npm のビルドエラー
```bash
# キャッシュをクリア
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 ライセンス

各プロジェクトは MIT License の下で公開されています。詳細は各プロジェクトの README を参照してください。

---

## 🤝 貢献について

- バグ報告・機能リクエスト: Issues で共有
- コード変更: Pull Request で提案
- 詳細な貢献ガイドラインは各プロジェクトの README を参照

---

**最終更新**: 2025年11月28日  
**バージョン**: 1.0.0