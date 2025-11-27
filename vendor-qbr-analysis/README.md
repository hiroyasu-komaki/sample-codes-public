# ベンダーQBR評価分析システム

## 概要
複数ベンダーの保守運用サービスに対するユーザー評価を収集・分析し、客観的かつ公平な評価に基づいてベンダーの優劣を判定するシステム。

## フォルダ構成

```
vendor_qbr_analysis/
├── main.py                          # メインエントリポイント
├── data/                            # データフォルダ
│   └── vendor-evaluation.csv        # 入力データ
├── config/                          # 設定ファイル
│   ├── config.yaml                  # メイン設定
│   └── vendor_schema.yaml           # データスキーマ定義
├── modules/                         # 分析モジュール
│   ├── __init__.py
│   ├── data_loader.py               # データ読み込み
│   ├── data_cleansing.py            # データクレンジング
│   ├── bias_analysis.py             # バイアス分析・スコア補正
│   ├── vendor_evaluation.py         # ベンダー総合評価
│   ├── statistical_tests.py         # 統計的検定
│   ├── segment_analysis.py          # セグメント分析
│   ├── visualization.py             # 可視化
│   ├── report_generator.py          # レポート出力
│   └── utils.py                     # ユーティリティ関数
└── output/                          # 出力フォルダ
    ├── csv/                         # CSV出力
    ├── figures/                     # グラフ出力
    └── reports/                     # レポート出力
```

## セットアップ

```bash
# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 必要なパッケージのインストール
pip install -r requirements.txt

# データファイルの配置（vendor-evaluation.csv を data/ フォルダに配置）
```

## 実行方法

```bash
python3 main.py
```

## 評価項目構造

### 大分類（4カテゴリ）
1. **パフォーマンス** (35%) - インシデント対応、SLA達成率など5項目
2. **技術レベル** (30%) - 専門性、トラブルシューティングなど5項目
3. **ビジネス理解** (20%) - プロセス理解、影響度考慮など5項目
4. **改善提案** (15%) - 提案品質、革新性など5項目

## 主要機能

### 分析機能
- データクレンジング（欠損値処理、異常値除外）
- 回答者バイアス補正（Z-score標準化）
- ベンダー総合評価（重み付けスコア計算）
- 統計的検定（ANOVA、Tukey HSD、効果量）
- セグメント分析（評価者群、部門、利用頻度、インシデント経験）

### 可視化
- レーダーチャート（総合評価 + カテゴリ別詳細）
- ヒートマップ（全20項目 × 4ベンダー）
- 箱ひげ図（補正前後比較）
- Z-score分布図
- ポジショニングマップ（6組み合わせ × raw/weighted版）
- Rank Flow Chart（セグメント別ベンダーランキング推移）

### 出力
- **CSV**: 分析結果データ（20種類以上）
- **PNG**: グラフ画像（15種類以上）
- **PDF**: 統合レポート（8ページ、全グラフ含む）
