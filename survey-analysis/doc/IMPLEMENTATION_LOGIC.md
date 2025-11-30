# 実装ロジックの説明

## 目次

1. [システムアーキテクチャ](#システムアーキテクチャ)
2. [モジュール構成](#モジュール構成)
3. [設定ファイルの設計](#設定ファイルの設計)
4. [データフロー](#データフロー)
5. [主要な設計判断](#主要な設計判断)
6. [実装の詳細](#実装の詳細)

---

## システムアーキテクチャ

### 全体構成

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│  - エントリーポイント                                     │
│  - ユーザーインタラクション                                │
│  - ワークフロー制御                                       │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                   ↓
┌─────────────────┐              ┌─────────────────────┐
│ data_generator  │              │ data_preprocess     │
│  - サンプルデータ  │              │  - データ前処理       │
│    生成          │              │  - エンコーディング   │
│  - 統計計算      │              │  - 標準化           │
└─────────────────┘              └─────────────────────┘
        ↓                                   ↓
┌─────────────────────────────────────────────────────────┐
│                      util.py                            │
│  - 統計表示                                               │
│  - 前処理サマリー表示                                      │
│  - 共通ユーティリティ                                      │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                   ↓
┌─────────────────┐              ┌─────────────────────┐
│  config.yaml    │              │ survey_questions.   │
│  - システム設定   │              │   yaml              │
│  - パス設定      │              │  - アンケート項目     │
│  - パラメータ    │              │  - データ属性        │
└─────────────────┘              └─────────────────────┘
```

---

## モジュール構成

### 1. main.py

**役割**: エントリーポイント、ワークフロー制御

**主要な関数:**

```python
def load_config(config_file: str) -> dict:
    """
    設定ファイルの読み込み
    
    設計思想: Fail Fast原則
    - 設定ファイルが存在しない場合は即座に終了
    - デフォルト設定で誤魔化さない
    """

def generate_data(config: dict) -> str:
    """
    サンプルデータの生成
    
    処理フロー:
    1. SurveyDataGeneratorインスタンス化
    2. サンプルデータ生成
    3. CSV保存
    4. 統計表示（util.print_statisticsを使用）
    """

def preprocess_data(input_file: str, config: dict) -> str:
    """
    データ前処理の実行
    
    処理フロー:
    1. DataPreprocessorインスタンス化
    2. データ読み込み
    3. 前処理パイプライン実行
    4. 結果保存
    5. サマリー表示（util.print_preprocessing_summaryを使用）
    """

def main():
    """
    メインワークフロー
    
    1. 設定ファイル読み込み
    2. データ生成（オプション）
    3. データ前処理（オプション）
    """
```

**設計判断:**

1. **Fail Fast原則の採用**
   - 設定ファイルが存在しない場合は即座に終了
   - 誤った状態で実行を続けない

2. **責任の分離**
   - データ生成: `data_generator.py`
   - データ前処理: `data_preprocess.py`
   - 表示: `util.py`

3. **ユーザーインタラクション**
   - 各ステップで実行可否を確認
   - 柔軟なワークフロー制御

---

### 2. modules/data_generator.py

**役割**: サンプルデータの生成

**クラス設計:**

```python
class SurveyDataGenerator:
    def __init__(self, config_file: str):
        """
        設定ファイル（survey_questions.yaml）を読み込み
        アンケート項目の定義を取得
        """
    
    def generate_sample_data(self, n: int = 100) -> pd.DataFrame:
        """
        サンプルデータ生成
        
        処理:
        1. respondent_id生成
        2. 回答者属性生成（ランダム）
        3. サービス利用状況生成（ランダム）
        4. 満足度評価生成（ランダム）
        5. 重要度評価生成（ランダム）
        6. 改善要望生成（ランダム）
        7. 欠損値の挿入（5%の確率）
        """
    
    def get_statistics(self, df: pd.DataFrame) -> dict:
        """
        統計情報の計算
        
        設計変更:
        - 以前: ハードコードされた項目リスト
        - 現在: YAMLから動的に取得
        
        返り値:
        {
            'total_samples': 100,
            'satisfaction_ratings': {...},  # 満足度評価の統計
            'importance_ratings': {...}     # 重要度評価の統計
        }
        """
```

**設計判断:**

1. **YAMLベースの設定**
   - 項目の追加・変更がYAMLファイルの編集のみで可能
   - ハードコードを完全に排除

2. **統計情報の分離**
   - 満足度評価と重要度評価を別々に管理
   - 拡張性の確保

---

### 3. modules/data_preprocess.py

**役割**: データの前処理

**クラス設計:**

```python
class DataPreprocessor:
    def __init__(self, config_file: str):
        """
        設定ファイル（survey_questions.yaml）を読み込み
        各項目のデータ属性（data_type、encoding、preprocessingなど）を取得
        """
    
    def load_data(self, file_path: str):
        """データ読み込み"""
    
    def identify_data_types(self) -> dict:
        """
        データ型の識別
        
        YAMLのdata_type属性から取得:
        - numeric: 数値型
        - ordinal: 順序カテゴリカル
        - nominal: 名義カテゴリカル
        - multi_choice: 複数選択
        """
    
    def encode_ordinal_variables(self, columns: list) -> dict:
        """
        順序エンコーディング
        
        YAMLのencoding.orderマッピングを使用
        例: {'一般職': 1, '主任・係長': 2, ...}
        """
    
    def encode_nominal_variables(self, columns: list) -> dict:
        """
        One-hotエンコーディング
        
        pd.get_dummiesを使用してダミー変数を生成
        """
    
    def expand_multiple_choice(self, columns: list) -> dict:
        """
        複数選択の二値展開
        
        カンマ区切りの文字列を分割し、各選択肢を二値変数に
        """
    
    def handle_missing_values(self, numeric_cols: list, strategy: str = 'auto') -> dict:
        """
        欠損値処理
        
        戦略:
        - 欠損率 < 5%: リストワイズ削除
        - 欠損率 ≥ 5%: 平均値補完
        """
    
    def standardize_numeric(self, columns: list, method: str = 'z_score') -> dict:
        """
        数値データの標準化とリスケーリング
        
        処理:
        1. Z-score標準化: (x - μ) / σ
           → 平均=0, 標準偏差=1
        2. リスケーリング: std_value × 1.0 + center
           → 元の範囲、標準偏差=1
        
        生成カラム:
        - *_std: 標準化データ（分析用）
        - *_rescaled: リスケールデータ（直感的理解用）
        """
    
    def preprocess_pipeline(self) -> pd.DataFrame:
        """
        前処理パイプライン
        
        実行順序:
        1. データ型識別
        2. 外れ値検出
        3. エンコーディング
        4. 欠損値処理
        5. 標準化・リスケーリング
        6. データ品質チェック
        """
```

**設計判断:**

1. **YAMLベースの柔軟な設定**
   - 各項目の前処理方法をYAMLで定義
   - コード変更なしで前処理ロジックを調整可能

2. **標準化とリスケーリングの分離**
   - `_std`: 分析用（平均=0, 標準偏差=1）
   - `_rescaled`: 理解用（元の範囲、標準偏差=1）

3. **詳細ログの削除**
   - 詳細はpreprocessing_report.jsonに保存
   - 画面出力は要点のみ

---

### 4. modules/util.py

**役割**: 共通ユーティリティ関数

**主要な関数:**

```python
def print_statistics(stats: dict, title: str = "統計情報"):
    """
    統計情報の標準出力
    
    表示内容:
    - 総サンプル数
    - 満足度評価の統計（平均、標準偏差）
    - 重要度評価の統計（平均、標準偏差）
    """

def print_preprocessing_summary(preprocessor: DataPreprocessor):
    """
    前処理サマリーの標準出力
    
    表示内容:
    - データサイズの変化
    - 満足度評価の前処理前後比較
    - 重要度評価の前処理前後比較
    - エンコーディング・欠損値処理の件数
    """

def print_header(title: str, width: int = 70):
    """ヘッダー表示（=で囲む）"""

def print_success(message: str):
    """成功メッセージ（✓付き）"""

def print_error(message: str):
    """エラーメッセージ（❌付き）"""
```

**設計判断:**

1. **関心の分離**
   - データ処理ロジックと表示ロジックを完全に分離
   - util.pyは表示のみに責任を持つ

2. **統一された出力形式**
   - 全モジュールで同じ形式を使用
   - 保守性の向上

3. **前処理前後の比較表示**
   - 4列構成で前後を並べて表示
   - 前処理の効果を視覚的に確認可能

---

## 設定ファイルの設計

### 1. config.yaml

**役割**: システム全体の設定

```yaml
directories:
  csv: "csv"
  output: "out"

files:
  survey_questions: "config/survey_questions.yaml"
  sample_data: "csv/survey_sample_data.csv"
  preprocessed_data: "csv/survey_preprocessed_data.csv"

data_generation:
  default_sample_size: 100
  missing_rate: 0.05

preprocessing:
  missing_value_strategy: "auto"
  standardization_method: "z_score"
  outlier_detection: true
```

**設計思想:**
- パスとパラメータを一元管理
- 環境に応じた設定変更が容易

---

### 2. survey_questions.yaml

**役割**: アンケート項目とデータ属性の定義

**構造:**

```yaml
項目名:
  question: "質問文"
  type: "single_choice"  # データ生成用
  options: [...]         # データ生成用
  scale: 5               # 1-5のスケール
  labels: [...]          # ラベル
  
  # データ属性（前処理用）
  data_type: "numeric"   # numeric/ordinal/nominal/multi_choice
  
  encoding:              # エンコーディング設定
    method: "ordinal"    # ordinal/one_hot/multi_hot
    order: {...}         # 順序エンコーディングのマッピング
  
  preprocessing:         # 前処理設定
    standardize: true
    handle_missing: "mean"
```

**互換性の維持:**

データ生成とデータ前処理の両方で同じYAMLファイルを使用：
- `type`, `options`: data_generator.pyが使用
- `data_type`, `encoding`, `preprocessing`: data_preprocess.pyが使用

**設計判断:**

1. **単一の設定ファイル**
   - データ生成と前処理の設定を統合
   - 項目定義の一元管理

2. **拡張性**
   - 新しい項目の追加がYAMLの編集のみで可能
   - コード変更不要

3. **明示的な型定義**
   - data_typeで明示的にデータ型を指定
   - 曖昧さを排除

---

## データフロー

### 全体フロー

```
1. データ生成
   config/survey_questions.yaml
            ↓
   data_generator.py
            ↓
   csv/survey_sample_data.csv (100行×23列)
            ↓
   統計計算・表示（util.py）

2. データ前処理
   csv/survey_sample_data.csv
            ↓
   config/survey_questions.yaml
            ↓
   data_preprocess.py
     ├─ エンコーディング
     ├─ 欠損値処理
     └─ 標準化・リスケーリング
            ↓
   csv/survey_preprocessed_data.csv (90行×76列)
            ↓
   out/preprocessing_report.json
            ↓
   サマリー表示（util.py）
```

### カラムの変換フロー

```
元データ（23列）
  ├─ respondent_id (1列) ──────────────────→ そのまま
  │
  ├─ 回答者属性 (4列)
  │   ├─ department ──────── One-hot ─────→ dept_* (5列)
  │   ├─ position ────────── 順序 ────────→ position_encoded (1列)
  │   ├─ years_of_service ── 順序 ────────→ years_of_service_encoded (1列)
  │   └─ it_skill_level ──── 順序 ────────→ it_skill_level_encoded (1列)
  │
  ├─ サービス利用 (3列)
  │   ├─ usage_frequency ─── 順序 ────────→ usage_frequency_encoded (1列)
  │   ├─ main_services ───── 複数選択 ────→ service_* (6列)
  │   └─ inquiry_count ───── 順序 ────────→ inquiry_count_encoded (1列)
  │
  ├─ 満足度評価 (8列) ──────── 標準化 ────→ *_std (8列)
  │                      └── リスケール ──→ *_rescaled (8列)
  │
  ├─ 重要度評価 (4列) ──────── 標準化 ────→ *_std (4列)
  │                      └── リスケール ──→ *_rescaled (4列)
  │
  └─ 改善要望 (3列)
      ├─ most_improvement ─── One-hot ───→ improve_* (5列)
      ├─ additional_services  複数選択 ──→ add_service_* (4列)
      └─ future_relationship  One-hot ───→ future_* (4列)

前処理後データ（76列）
```

---

## 主要な設計判断

### 1. ハードコードの排除

**問題:**
```python
# 以前のコード
names = {
    'overall_satisfaction': '総合満足度',
    'response_speed': '対応スピード',
    # ... 項目が増えるたびに修正が必要
}
```

**解決:**
```python
# 現在のコード
for key, data in stats['satisfaction_ratings'].items():
    print(f"{key:<30} {data['mean']:<8.2f} {data['std']:<8.2f}")
    # YAMLに項目を追加すれば自動的に表示
```

### 2. Fail Fast原則

**問題:**
```python
# 以前のコード
except FileNotFoundError:
    print("デフォルト設定を使用します。")
    return {...}  # 30行以上のハードコード
```

**解決:**
```python
# 現在のコード
except FileNotFoundError:
    print(f"\n❌ エラー: {config_file} が見つかりません")
    sys.exit(1)  # 即座に終了
```

### 3. 標準化とリスケーリングの分離

**要求:**
- 標準化: データを平均=0、標準偏差=1に（分析用）
- リスケール: 元の範囲に戻しつつ標準偏差=1を保持（理解用）

**実装:**
```python
# 標準化
data_std = (data - mean) / std
# → 平均=0, 標準偏差=1

# リスケーリング
center = (max_value + min_value) / 2
data_rescaled = data_std × 1.0 + center
# → 満足度（1-5）: 平均=3.0, 標準偏差=1.0
# → 重要度（1-4）: 平均=2.5, 標準偏差=1.0
```

### 4. 表示ロジックの集約

**問題:**
- 各モジュールでprint文が散在
- 出力形式が統一されていない

**解決:**
- util.pyにすべての表示ロジックを集約
- 統一された出力形式
- 保守性の向上

---

## 実装の詳細

### リスケーリングのロジック

**間違った実装（Min-Max正規化）:**
```python
# これは標準偏差を変えてしまう
rescaled = ((std_value - min) / (max - min)) × range + min_value
# → 標準偏差 ≠ 1.0
```

**正しい実装（標準偏差保持）:**
```python
# 標準偏差=1.0を保つ
center = (original_max + original_min) / 2
rescaled = std_value × 1.0 + center
# → 標準偏差 = 1.0
```

### 欠損値処理の戦略

```python
def handle_missing_values(self, numeric_cols, strategy='auto'):
    for col in numeric_cols:
        missing_count = data[col].isna().sum()
        missing_rate = missing_count / len(data)
        
        if missing_rate < 0.05:
            # リストワイズ削除
            data = data.dropna(subset=[col])
        else:
            # 平均値補完
            mean_value = data[col].mean()
            data[col].fillna(mean_value, inplace=True)
```

### 統計表示の前後比較

```python
def print_preprocessing_summary(preprocessor):
    # 前処理前後を4列で表示
    print(f"{'項目':<35} {'前処理前':<18} {'前処理後（リスケール）':<18}")
    print(f"{'':<35} {'平均':<8} {'標準偏差':<8} {'平均':<8} {'標準偏差':<8}")
    
    for col, info in items:
        before_mean = info['mean']
        before_std = info['std']
        after_mean = processed_data[f'{col}_rescaled'].mean()
        after_std = processed_data[f'{col}_rescaled'].std()
        
        print(f"{col:<35} {before_mean:<8.2f} {before_std:<8.2f} "
              f"{after_mean:<8.2f} {after_std:<8.2f}")
```

---

## まとめ

### 設計原則

1. **設定駆動型**: YAMLファイルで動作を制御
2. **Fail Fast**: エラーは早期に検出して終了
3. **関心の分離**: データ処理と表示を分離
4. **拡張性**: 新機能の追加が容易
5. **保守性**: コードの変更が最小限

### コードの品質

- ハードコードの完全排除
- 統一された出力形式
- 明確な責任分離
- YAMLベースの柔軟な設定

### 今後の拡張

- 分析機能の追加（data_analyser.py）
- レポート生成機能（report_generator.py）
- グラフ出力機能
- Web UIの追加
