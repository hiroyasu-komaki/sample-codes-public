# Skill Data Analyzer

スキルデータを可視化・分析するPythonツール。個人のスキルプロファイルのレーダーチャート作成、組織全体のスキル分布分析、スキル標準の作成が可能です。

## 📋 目次

- [機能](#機能)
- [必要な環境](#必要な環境)
- [インストール](#インストール)
- [使用方法](#使用方法)
- [出力例](#出力例)
- [CSVファイル形式](#csvファイル形式)
- [プロジェクト構成](#プロジェクト構成)

## ✨ 機能

### 1. 個人プロファイル分析 (`individual`)
- **レーダーチャート**: カテゴリー別の平均スキルレベルを円形チャートで可視化
- **スキル項目チャート**: カテゴリー別のスキル項目を横棒グラフで詳細表示
- 個人のスキルセット全体を一目で把握可能

### 2. 組織分析 (`group`)
- **箱ひげ図**: 組織全体のスキル分布を統計的に可視化
- **カテゴリー別分析**: 組織の強み・弱みカテゴリーを特定
- **スキルバラツキ分析**: チーム内のスキル格差を可視化
- 組織レベルでのスキル充足度評価

### 3. スキル標準作成 (`standard`)
- 標準的なスキルレベル基準をレーダーチャートで作成
- スキル評価の統一基準として活用可能

## 🔧 必要な環境

- **Python**: 3.7以上
- **OS**: Windows、macOS、Linux対応

### 必須ライブラリ
```
pandas>=1.3.0
matplotlib>=3.3.0
seaborn>=0.11.0
numpy>=1.20.0
```

### オプションライブラリ
```
plotly>=5.0.0  # インタラクティブグラフ（将来の拡張用）
```

## 🚀 インストール

### 1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/skill-data-analyzer.git
cd skill-data-analyzer
```

### 2. 仮想環境の作成（推奨）
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
```

### 3. 依存関係のインストール
```bash
pip install pandas matplotlib seaborn numpy
```

### 4. ディレクトリ構成の準備
```bash
mkdir -p input output output2
```

## 📖 使用方法

### 基本コマンド

```bash
# ヘルプの表示
python main.py -h

# 組織分析（推奨：最初に実行）
python main.py group

# 特定個人のレーダーチャート作成
python main.py individual --person sample_001_engineer_focused

# スキル標準レーダーチャート作成
python main.py standard
```

### 実行手順

1. **CSVファイルの配置**
   ```
   input/consolidated_skill_data.csv
   ```

2. **組織分析の実行**
   ```bash
   python main.py group
   ```
   - 出力先: `output2/`ディレクトリ
   - 組織全体のスキル分布が箱ひげ図で可視化

3. **個人分析の実行**
   ```bash
   python main.py individual --person [個人名]
   ```
   - 出力先: `output/`ディレクトリ
   - 個人のレーダーチャートとスキル項目チャートを生成

## 📊 出力例

### 組織分析の出力
- `organization_skill_sufficiency_by_category.png` - カテゴリー別箱ひげ図
- `organization_skill_sufficiency_by_skill.png` - スキル項目別統合箱ひげ図
- コンソールに統計情報と強み・弱み分析結果を表示

### 個人分析の出力
- `[個人名].png` - 個人のレーダーチャート
- `[個人名]_skills.png` - カテゴリー別スキル項目チャート

### スキル標準の出力
- `output/skill_standard_radar.png` - 標準スキルレベルのレーダーチャート

## 📄 CSVファイル形式

入力CSVファイル（`input/consolidated_skill_data.csv`）は以下の形式である必要があります：

| カラム名 | 型 | 説明 | 例 |
|---------|---|------|-----|
| カテゴリー | 文字列 | スキルの大分類 | "プログラミング" |
| サブカテゴリー | 文字列 | スキルの中分類 | "フロントエンド" |
| スキル項目 | 文字列 | 具体的なスキル | "React.js" |
| ロール | 文字列 | 職種・役割 | "フロントエンドエンジニア" |
| 専門性 | 文字列 | 専門分野 | "Webアプリケーション開発" |
| スキルレベル | 文字列 | レベル表記 | "中級" |
| スキルレベル_数値 | 数値 | 数値レベル(0-5) | 3 |
| ファイル名 | 文字列 | 個人識別子 | "sample_001_engineer_focused" |

### サンプルデータ形式
```csv
カテゴリー,サブカテゴリー,スキル項目,ロール,専門性,スキルレベル,スキルレベル_数値,ファイル名
プログラミング,フロントエンド,React.js,フロントエンドエンジニア,Webアプリケーション開発,中級,3,sample_001_engineer_focused
プログラミング,バックエンド,Python,バックエンドエンジニア,API開発,上級,4,sample_002_backend_specialist
```

## 📁 プロジェクト構成

```
skill-data-analyzer/
├── main.py                 # メインエントリポイント
├── data_loader.py          # CSVデータの読み込み・前処理
├── individual_analyzer.py  # 個人レーダーチャート分析
├── group_analyzer.py       # 組織分析（箱ひげ図）
├── standard_analyzer.py    # スキル標準レーダーチャート
├── utils.py               # 共通ユーティリティ
├── input/                 # 入力ファイル配置
│   └── consolidated_skill_data.csv
├── output/               # 個人分析結果
└── output2/              # 組織分析結果
```

### 各モジュールの役割

- **`main.py`**: コマンドライン引数の解析とメイン処理の実行
- **`data_loader.py`**: CSVファイルの読み込み、データ検証、前処理
- **`individual_analyzer.py`**: 個人のスキルプロファイルをレーダーチャートで可視化
- **`group_analyzer.py`**: 組織全体のスキル分布を箱ひげ図で分析
- **`standard_analyzer.py`**: スキル標準レベルのレーダーチャート作成
- **`utils.py`**: 日本語フォント設定、システム情報取得などの共通機能

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は`LICENSE`ファイルをご覧ください。

