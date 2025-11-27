# モジュール実装ガイド

## 概要

このドキュメントは、`vendor-qbr-analysis.md`の各章に対応するモジュールの実装ガイドです。

## モジュールと対応する仕様書の章

| モジュール | 対応する章 | 主要機能 |
|-----------|----------|---------|
| `data_loader.py` | 第3章 | データ構造・読み込み |
| `data_cleansing.py` | 第4章 | データクレンジング |
| `bias_analysis.py` | 第5.1-5.2章 | バイアス分析・スコア補正 |
| `vendor_evaluation.py` | 第5.3章 | ベンダー総合評価 |
| `statistical_tests.py` | 第5.4章 | 統計的検定 |
| `segment_analysis.py` | 第5.5章 | セグメント分析 |
| `visualization.py` | 第6章 | 可視化 |
| `report_generator.py` | 第7章 | レポート出力 |

---

## 1. data_loader.py（第3章対応）

### 実装すべき機能

```python
def load_data(filepath: str, config: Dict) -> pd.DataFrame:
    """
    CSVファイルからデータを読み込む
    
    - CSV読み込み
    - エンコーディング処理
    - 基本的なデータ型変換
    """
    pass

def validate_schema(df: pd.DataFrame, schema: dict) -> bool:
    """
    YAMLスキーマに基づいてデータを検証
    
    - 必須カラムの存在確認
    - データ型の確認
    - 値の範囲チェック（1-5）
    """
    pass

def get_basic_statistics(df: pd.DataFrame) -> dict:
    """
    基本統計情報を取得
    
    - レコード数
    - ベンダー別回答数
    - 欠損値の割合
    """
    pass
```

### 参照: vendor-qbr-analysis.md

- 第3章「データ構造」（76-117行目）
- テーブル定義とフィールド仕様

---

## 2. data_cleansing.py（第4章対応）

### 実装すべき機能

```python
def exclude_invalid_responses(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    除外基準に基づいて無効な回答を除外
    
    1. すべて同一評価の除外
    2. 評価ベンダー数不足（1社のみ）の除外
    3. 未回答率50%以上の除外
    4. 標準偏差=0の除外
    """
    pass

def check_all_same_score(row: pd.Series, item_cols: List[str]) -> bool:
    """全項目が同じスコアかチェック"""
    pass

def handle_missing_values(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    欠損値処理
    
    - カテゴリ内平均で補完
    - 補完不可の場合は除外
    """
    pass

def validate_data_quality(df: pd.DataFrame, config: Dict) -> dict:
    """
    データ品質検証
    
    - スコア範囲チェック（1-5）
    - ベンダーIDの整合性
    - タイムスタンプの妥当性
    """
    pass
```

### 参照: vendor-qbr-analysis.md

- 第4章「データクレンジング」（119-139行目）

---

## 3. bias_analysis.py（第5.1-5.2章対応）

### 実装すべき機能

```python
def profile_respondents(df: pd.DataFrame, item_cols: List[str]) -> pd.DataFrame:
    """
    回答者プロファイリング
    
    - 回答者平均スコア
    - 回答者標準偏差
    - 極端値使用率
    - 中央値使用率
    """
    pass

def detect_anomaly_patterns(profile_df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    異常パターン検出
    
    - 標準偏差=0
    - 極端値使用率>80%
    """
    pass

def apply_zscore_normalization(df: pd.DataFrame, item_cols: List[str]) -> pd.DataFrame:
    """
    Z-score標準化（メイン手法）
    
    標準化スコア = (元のスコア - 回答者平均) / 回答者標準偏差
    """
    pass

def apply_rank_conversion(df: pd.DataFrame, item_cols: List[str]) -> pd.DataFrame:
    """
    相対順位化（検証用）
    
    Borda Count方式
    """
    pass

def apply_centering(df: pd.DataFrame, item_cols: List[str]) -> pd.DataFrame:
    """
    中心化（参考用）
    
    中心化スコア = 元のスコア - 回答者平均 + 全体平均
    """
    pass
```

### 参照: vendor-qbr-analysis.md

- 第5.1章「回答者バイアス分析」（144-160行目）
- 第5.2章「スコア補正手法」（162-197行目）

---

## 4. vendor_evaluation.py（第5.3章対応）

### 実装すべき機能

```python
def aggregate_by_category(df: pd.DataFrame, context: AnalysisContext) -> pd.DataFrame:
    """
    大分類レベルの集計
    
    - 平均スコア
    - 標準偏差
    - 95%信頼区間
    """
    pass

def calculate_weighted_scores(category_scores: pd.DataFrame, weights: Dict) -> pd.DataFrame:
    """
    重み付け総合スコア
    
    総合スコア = Σ(大分類スコア × ウェイト)
    
    推奨ウェイト:
    - パフォーマンス: 35%
    - 技術レベル: 30%
    - ビジネス理解: 20%
    - 改善提案: 15%
    """
    pass

def calculate_composite_scores(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    複合評価スコア
    
    最終評価スコア = 標準化スコア×0.5 + 順位スコア×0.3 + 生スコア×0.2
    """
    pass

def calculate_reliability_coefficient(n_respondents: int, threshold: int = 20) -> float:
    """
    信頼性係数
    
    信頼性係数 = min(1.0, √(評価者数 / 20))
    """
    pass
```

### 参照: vendor-qbr-analysis.md

- 第5.3章「ベンダー総合評価」（199-236行目）

---

## 5. statistical_tests.py（第5.4章対応）

### 実装すべき機能

```python
def perform_anova(df: pd.DataFrame, category: str) -> dict:
    """
    分散分析（ANOVA）
    
    帰無仮説: 全ベンダーの平均スコアは等しい
    有意水準: α = 0.05
    """
    pass

def perform_tukey_hsd(df: pd.DataFrame, category: str) -> pd.DataFrame:
    """
    多重比較（Tukey HSD検定）
    
    どのペア間に有意差があるか検証
    """
    pass

def calculate_effect_sizes(df: pd.DataFrame, vendor_pairs: List) -> pd.DataFrame:
    """
    効果量（Cohen's d）
    
    d = (平均1 - 平均2) / 統合標準偏差
    
    解釈:
    - |d| < 0.2: 効果小
    - 0.2 ≤ |d| < 0.5: 効果中
    - |d| ≥ 0.5: 効果大
    """
    pass

def create_significance_table(test_results: dict) -> pd.DataFrame:
    """統計的有意差テーブルの作成"""
    pass
```

### 参照: vendor-qbr-analysis.md

- 第5.4章「統計的検定」（238-265行目）

---

## 6. segment_analysis.py（第5.5章対応）

### 実装すべき機能

```python
def classify_respondents(profile_df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    評価者を分類
    
    - 厳格評価者: 平均スコア < 3.0
    - 標準評価者: 3.0 ≤ 平均スコア ≤ 4.0
    - 寛容評価者: 平均スコア > 4.0
    """
    pass

def analyze_by_respondent_group(df: pd.DataFrame, profile_df: pd.DataFrame) -> pd.DataFrame:
    """評価者群別分析"""
    pass

def analyze_by_attribute(df: pd.DataFrame, attribute: str) -> pd.DataFrame:
    """
    属性別分析
    
    - 部門別
    - 利用頻度別
    - インシデント経験有無別
    """
    pass

def perform_chi_square_test(df: pd.DataFrame, attribute: str) -> dict:
    """
    カイ二乗検定
    
    属性とベンダー選好に関連があるか検証
    """
    pass
```

### 参照: vendor-qbr-analysis.md

- 第5.5章「セグメント分析」（267-292行目）

---

## 7. visualization.py（第6章対応）

### 実装すべき機能

#### 必須グラフ

```python
def plot_radar_chart(data: pd.DataFrame, context: AnalysisContext) -> None:
    """
    レーダーチャート（4大分類比較）
    
    - 軸: 4大分類
    - プロット: 4社のベンダー
    - サイズ: 600×600px
    """
    pass

def plot_heatmap(data: pd.DataFrame, context: AnalysisContext) -> None:
    """
    ヒートマップ（詳細項目）
    
    - 行: 詳細項目（20項目）
    - 列: 4社のベンダー
    - 色: 低→中→高（赤→黄→緑）
    """
    pass

def plot_boxplot_with_significance(data: pd.DataFrame, significance: pd.DataFrame, context: AnalysisContext) -> None:
    """
    箱ひげ図＋有意差マーク
    
    - 箱: Q1-Q3（IQR）
    - 有意差: ***, **, *, ns
    """
    pass

def plot_positioning_map(data: pd.DataFrame, context: AnalysisContext) -> None:
    """
    ポジショニングマップ
    
    - X軸: パフォーマンススコア
    - Y軸: 改善提案スコア
    - バブルサイズ: 評価者数
    """
    pass
```

#### 補助グラフ

```python
def plot_dumbbell_chart(data: pd.DataFrame, context: AnalysisContext) -> None:
    """ダンベルチャート（補正前後比較）"""
    pass

def plot_stacked_bar(data: pd.DataFrame, context: AnalysisContext) -> None:
    """積み上げ棒グラフ（重み付け内訳）"""
    pass

def plot_respondent_scatter(profile_df: pd.DataFrame, context: AnalysisContext) -> None:
    """回答者傾向散布図"""
    pass

def plot_rank_distribution(data: pd.DataFrame, context: AnalysisContext) -> None:
    """順位分布（積み上げ棒グラフ100%）"""
    pass

def plot_grouped_bars(data: pd.DataFrame, category: str, context: AnalysisContext) -> None:
    """グループ化棒グラフ（詳細項目）"""
    pass

def plot_facet_by_group(data: pd.DataFrame, context: AnalysisContext) -> None:
    """ファセットグラフ（評価者群別）"""
    pass
```

### 参照: vendor-qbr-analysis.md

- 第6章「可視化仕様」（295-436行目）
- カラーパレット、フォント設定含む

---

## 8. report_generator.py（第7章対応）

### 実装すべき機能

```python
def generate_summary_table(results: dict, context: AnalysisContext) -> pd.DataFrame:
    """
    総合評価テーブル
    
    列: ベンダー, 生スコア平均, 標準化スコア, 順位平均, 
        複合スコア, 総合順位, 評価者数, 信頼性係数
    """
    pass

def generate_category_table(results: dict, context: AnalysisContext) -> pd.DataFrame:
    """
    大分類別スコアテーブル
    
    列: ベンダー, パフォーマンス, 技術レベル, 
        ビジネス理解, 改善提案, 加重平均
    """
    pass

def generate_significance_table(test_results: dict) -> pd.DataFrame:
    """統計的有意差テーブル"""
    pass

def create_vendor_report(vendor_id: str, results: dict, context: AnalysisContext) -> str:
    """
    ベンダー個別レポート
    
    - 総合評価
    - 強みTop3
    - 弱みTop3
    - セグメント別評価
    - 統計情報
    - 改善推奨事項
    """
    pass

def export_to_pdf(content: str, filename: str, config: dict) -> None:
    """PDFエクスポート"""
    pass

def generate_executive_summary(results: dict, context: AnalysisContext) -> None:
    """エグゼクティブサマリー生成"""
    pass
```

### 参照: vendor-qbr-analysis.md

- 第7章「出力仕様」（440-553行目）

---

## 実装の優先順位

1. **優先度 高**: 必須機能
   - data_loader.py
   - data_cleansing.py
   - bias_analysis.py（Z-score標準化のみ）
   - vendor_evaluation.py（基本集計）
   - visualization.py（必須グラフ4つ）

2. **優先度 中**: コア機能
   - statistical_tests.py
   - segment_analysis.py
   - report_generator.py（基本レポート）

3. **優先度 低**: 拡張機能
   - bias_analysis.py（順位化、中心化）
   - visualization.py（補助グラフ）
   - report_generator.py（PDF出力）

---

## 開発ワークフロー

1. **ステップ1**: data_loader.py を実装
   - データ読み込みとバリデーション
   - main.pyで動作確認

2. **ステップ2**: data_cleansing.py を実装
   - データクレンジング
   - 除外・補完処理

3. **ステップ3**: bias_analysis.py を実装
   - 回答者プロファイリング
   - Z-score標準化

4. **ステップ4**: vendor_evaluation.py を実装
   - カテゴリ別集計
   - 重み付けスコア計算

5. **ステップ5**: visualization.py を実装
   - 必須グラフ4つ
   - 基本的な可視化

6. **ステップ6**: 統計・セグメント・レポートを実装
   - 順次追加

---

## テストとデバッグ

各モジュール実装後、以下を確認：

```python
# 単体テスト例
if __name__ == "__main__":
    config = utils.load_config()
    df = load_data(config['data']['input_csv'], config)
    print(df.shape)
    print(df.head())
```

---

## 次のステップ

1. このガイドに従って各モジュールを実装
2. main.pyで統合テスト
3. 実データで動作確認
4. 必要に応じて調整
