# IT部門サービス満足度アンケート分析システム

## 概要

IT部門が提供するサービスに対する従業員の満足度を分析するシステムです。
アンケートデータの生成、前処理、統計分析、レポート生成までを一貫して実行できます。

**主な機能:**
- サンプルデータの自動生成
- データの前処理（エンコーディング、標準化、欠損値処理、代表性検証）
- 統計分析（記述統計、相関分析、IPA分析、属性別分析）
- グラフとレポートの自動生成（箱ひげ図、ヒートマップ、IPAマトリックス）

## フォルダ構成

```
survey-analysis/
├── main.py                          # メインプログラム
├── config/
│   ├── config.yaml                  # システム設定ファイル
│   └── survey_questions.yaml        # アンケート項目定義
├── modules/
│   ├── data_generator.py            # サンプルデータ生成
│   ├── data_preprocess.py           # データ前処理
│   ├── data_analyser.py             # データ分析
│   ├── report_generator.py          # レポート生成
│   └── util.py                      # ユーティリティ関数
├── csv/
│   ├── survey_sample_data.csv       # 生成されたサンプルデータ
│   └── survey_preprocessed_data.csv # 前処理済みデータ
├── out/
│   ├── preprocessing_report.json    # 前処理レポート
│   └── analysis_results.json        # 分析結果
├── reports/
│   ├── detailed_report.md           # 詳細レポート（画像埋め込み）
│   └── graphs/                      # グラフ画像
│       ├── satisfaction_distribution.png
│       ├── satisfaction_ranking.png
│       ├── correlation_heatmap.png
│       ├── attribute_comparison_*.png
│       └── ipa_matrix.png
├── docs/
│   ├── DATA_PREPROCESSING.md        # データ前処理の詳細
│   ├── DATA_ANALYZING.md            # データ分析の詳細
│   └── IMPLEMENTATION_LOGIC_EXTENDED.md  # 実装ロジックの説明
├── requirements.txt                 # 依存パッケージ
└── README.md                        # このファイル
```

## セットアップ

```bash
# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 必要なパッケージのインストール
pip install -r requirements.txt

# ディレクトリの作成（初回のみ）
mkdir -p csv out reports
```

## 実行方法

```bash
# メインプログラムの実行
python3 main.py
```

**実行フロー:**
1. サンプルデータを生成するか選択（Y/N）
2. データ前処理を実行するか選択（Y/N）
3. データ分析を実行するか選択（Y/N）
4. レポートを生成するか選択（Y/N）

各ステップは個別にスキップ可能で、既存のファイルを利用して次のステップから実行できます。

## 出力ファイル

### CSVファイル
- `csv/survey_sample_data.csv` - 生成されたサンプルデータ（100件）
- `csv/survey_preprocessed_data.csv` - 前処理済みデータ（90件、76列）

### 分析結果
- `out/preprocessing_report.json` - 前処理の詳細レポート
- `out/analysis_results.json` - 統計分析結果（JSON形式）

### レポート
- `reports/detailed_report.md` - 詳細レポート（Markdown形式、画像埋め込み）
- `reports/graphs/*.png` - 各種グラフ（8個）

## 分析機能

### 1. 記述統計
- 平均値、中央値、標準偏差
- 95%信頼区間
- 満足度分布

### 2. 相関分析
- 総合満足度との相関係数
- 項目間の相関マトリックス
- 有意性検定（p値）

### 3. 属性別分析
- 部署別、職位別、勤続年数別、ITスキル別
- 箱ひげ図による分布の可視化

### 4. IPA分析（重要度-満足度分析）
- 4象限分類（維持、最優先改善、改善検討、過剰品質）
- 優先度ランキング

## グラフ出力

すべてのグラフは300dpiの高解像度PNG形式で出力されます：

1. **満足度分布** - 全体的な満足度の分布を可視化
2. **満足度ランキング** - 項目別の満足度を箱ひげ図で比較
3. **相関ヒートマップ** - 項目間の相関関係を可視化
4. **属性別比較** - 各属性グループの満足度分布（箱ひげ図）
5. **IPAマトリックス** - 重要度と満足度の2軸マトリックス

## ドキュメント

詳細な実装内容については以下のドキュメントを参照してください：

- [データ前処理の詳細](docs/DATA_PREPROCESSING.md) - 前処理の各ステップと効果
- [データ分析の詳細](docs/DATA_ANALYZING.md) - 分析手法と実装詳細
- [実装ロジックの説明](docs/IMPLEMENTATION_LOGIC_EXTENDED.md) - コードの設計思想と実装詳細

## 依存パッケージ

- Python 3.8以上
- pandas
- numpy
- PyYAML
- scipy
- matplotlib
- seaborn

詳細は `requirements.txt` を参照してください。

## 設定のカスタマイズ

### サンプルサイズの変更
`config/config.yaml`:
```yaml
data_generation:
  default_sample_size: 100  # お好みの数に変更
```

### 母集団分布の調整
`config/config.yaml`の`population_distribution`セクションで、実際の組織の従業員分布に合わせて調整できます。

### 分析パラメータ
`config/config.yaml`:
```yaml
analysis:
  confidence_level: 0.95      # 信頼区間
  significance_level: 0.05    # 有意水準
```

## トラブルシューティング

### 日本語フォントが表示されない場合
グラフの日本語が文字化けする場合は、以下のフォントがインストールされているか確認してください：

- **Mac**: Hiragino Kaku Gothic ProN（標準搭載）
- **Windows**: Yu Gothic または Meiryo（標準搭載）
- **Linux**: IPAexGothic または Noto Sans CJK JP

### データ生成で同じデータが生成される
`modules/data_generator.py`の`np.random.seed(42)`を変更するか、コメントアウトしてください。

## ライセンス

MIT License