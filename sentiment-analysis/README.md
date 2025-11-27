# 感情分析比較検証システム

日本語テキストを3つの異なるモデルで感情分析し、結果を比較するシステムです。

## 概要

このシステムは、以下の3つのアプローチで日本語テキストの感情分析を実行します：

1. **Transformer Model 1** - `jarvisx17/japanese-sentiment-analysis`
2. **Transformer Model 2** - `koheiduck/bert-japanese-finetuned-sentiment`
3. **Dictionary-based Model** - ルールベースの辞書マッチング

各モデルの結果を統一フォーマットで出力し、比較・検証することができます。

## 特徴

- ✅ 3つの異なる感情分析手法の比較
- ✅ 統一された出力フォーマット
- ✅ 文単位での詳細な分析
- ✅ 進捗表示と統計情報の自動生成
- ✅ UTF-8対応の日本語処理

## 必要要件

### Python バージョン
- Python 3.8以上

### 必要なライブラリ

```bash
pip install torch transformers pandas
```

または、以下のコマンドで一括インストール：

```bash
pip install torch==2.0.0 transformers==4.30.0 pandas==2.0.0
```

## ディレクトリ構成

```
project/
│
├── main.py                      # メインプログラム
├── modules/                     # モジュールフォルダ
│   ├── dataloader.py           # データ読み込み
│   ├── text2sentence.py        # テキスト分割
│   ├── model_transformer1.py   # Transformerモデル1
│   ├── model_transformer2.py   # Transformerモデル2
│   └── model_dictionary.py     # 辞書ベースモデル
│
├── txt/                        # 入力テキストファイル（自動生成）
├── csv/                        # 分割された文章（自動生成）
└── out/                        # 分析結果（自動生成）
```

## 使用方法

### 1. セットアップ

```bash
# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 必要なパッケージのインストール
pip install -r requirements.txt

# データファイルの配置（vendor-evaluation.csv を data/ フォルダに配置）
```

### 2. 実行方法

```bash
python3 main.py
```

<br>

## 対話形式での操作

プログラムを実行すると、以下のような対話形式で進行します：

```
============================================================
感情分析比較検証システム（3モデル比較）
============================================================

[Step 1] テキストファイルの選択

利用可能なテキストファイル:
  1. sample.txt
  2. review.txt

分析するファイルを選択してください (1-2): 1
選択されたファイル: txt/sample.txt

[Step 2] テキストを文に分割中...
文の数: 150
分割結果を保存: csv/sample_sentences.csv

[Step 3] 感情分析を実行中...

--- Model 1: Transformer (jarvisx17) ---
  モデルを読み込んでいます...
  処理中: 50/150
  処理中: 100/150
  処理中: 150/150

[Model 1 (Japanese Sentiment Analysis) 統計情報]
総文数: 150

感情分布:
ポジティブ    85
中立         45
ネガティブ    20

平均スコア: 0.2341
...
```

## 出力ファイル

### 分割された文章（csv/）

```csv
sentence_id,sentence
1,このサービスは非常に素晴らしいです
2,対応が遅くて困りました
3,普通の品質だと思います
```

### 分析結果（out/）

各モデルごとに以下のフォーマットでCSVファイルが生成されます：

```csv
sentence_id,sentence,score,positive,negative,sentiment,model_name
1,このサービスは非常に素晴らしいです,0.8542,0.9271,0.0729,ポジティブ,transformer1
2,対応が遅くて困りました,-0.6231,0.1884,0.8115,ネガティブ,transformer1
3,普通の品質だと思います,0.0523,0.5261,0.4738,中立,transformer1
```

## 各モデルの詳細

### Model 1: Transformer (jarvisx17)

- **モデル名**: `jarvisx17/japanese-sentiment-analysis`
- **タイプ**: 事前学習済みTransformerモデル
- **出力**: ポジティブ/ネガティブの確率スコア
- **特徴**: 文脈を考慮した高精度な分析

### Model 2: Transformer (koheiduck)

- **モデル名**: `koheiduck/bert-japanese-finetuned-sentiment`
- **タイプ**: 日本語BERT微調整モデル
- **出力**: ポジティブ/ネガティブの確率スコア
- **特徴**: BERTベースの深層学習モデル

### Model 3: Dictionary-based

- **タイプ**: ルールベースの辞書マッチング
- **手法**: 
  - ポジティブ/ネガティブ単語リスト
  - 強調表現の検出（「非常に」「とても」など）
  - 否定表現の考慮（「ない」「ません」など）
- **特徴**: 軽量・高速だが文脈理解は限定的

## 感情判定の基準

全モデル共通の閾値：

```
スコア > 0.2    → ポジティブ
スコア < -0.2   → ネガティブ
-0.2 ≤ スコア ≤ 0.2 → 中立
```

スコアは-1.0（完全ネガティブ）〜 1.0（完全ポジティブ）の範囲で計算されます。

## 出力カラムの説明

| カラム名 | 説明 | 範囲 |
|---------|------|------|
| `sentence_id` | 文章の連番ID | 1, 2, 3, ... |
| `sentence` | 分析対象の文章 | テキスト |
| `score` | 総合感情スコア | -1.0 〜 1.0 |
| `positive` | ポジティブスコア | 0.0 〜 1.0 |
| `negative` | ネガティブスコア | 0.0 〜 1.0 |
| `sentiment` | 感情ラベル | ポジティブ/中立/ネガティブ |
| `model_name` | 使用モデル名 | transformer1/transformer2/dictionary |

**注意**: 辞書ベースモデルでは `positive` と `negative` は `None` になります。

## トラブルシューティング

### モデルのダウンロードエラー

初回実行時、Transformerモデルが自動ダウンロードされます。ネットワーク接続を確認してください。

```bash
# キャッシュをクリアして再試行
rm -rf ~/.cache/huggingface/
python main.py
```

### メモリ不足エラー

大量のテキストを処理する場合、メモリ不足が発生することがあります：

```python
# model_transformer1.py または model_transformer2.py 内で
# バッチサイズを調整
if (idx + 1) % 10 == 0:  # 処理ごとにメモリ解放
    torch.cuda.empty_cache()
```

### 文字化けが発生する場合

出力CSVファイルはUTF-8 BOM付きで保存されていますが、エディタによっては文字化けする場合があります：

```python
# encoding指定を変更
df.to_csv(output_path, index=False, encoding='utf-8')  # BOMなし
```

## パフォーマンス

処理速度の目安（CPUの場合）：

- **Dictionary-based**: 1000文 / 約5秒
- **Transformer Model 1**: 1000文 / 約3-5分
- **Transformer Model 2**: 1000文 / 約3-5分

GPUを使用する場合は大幅に高速化されます。

## GPU対応

GPUを使用する場合は、各Transformerモデルファイルに以下を追加：

```python
# model_transformer1.py の analyze_with_transformer1() 内
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# 推論時
inputs = {k: v.to(device) for k, v in inputs.items()}
```

## カスタマイズ

### 感情判定閾値の変更

各モデルファイル内の閾値を変更できます：

```python
# 例: より厳密な判定にする場合
if total_score > 0.5:  # 0.2 → 0.5 に変更
    sentiment = 'ポジティブ'
elif total_score < -0.5:  # -0.2 → -0.5 に変更
    sentiment = 'ネガティブ'
```

### 辞書の追加

`model_dictionary.py` 内の単語リストを編集：

```python
POSITIVE_WORDS = [
    '良い', '素晴らしい', '最高', ...,
    '追加したい単語'  # ここに追加
]
```

<br>

## ライセンスと注意事項

### このプロジェクトのコード
- ライセンス：MIT License（または好きなライセンス）
- 自由に使用・改変・再配布が可能です

### 使用している機械学習モデル
1. **jarvisx17/japanese-sentiment-analysis**
   - ライセンス：MIT License
   - 出典：https://huggingface.co/jarvisx17/japanese-sentiment-analysis

2. **koheiduck/bert-japanese-finetuned-sentiment**
   - 出典：https://huggingface.co/koheiduck/bert-japanese-finetuned-sentiment
   - ライセンス情報が明記されていないため、使用する場合は自己責任でお願いします
   - モデルは実行時に自動ダウンロードされます（本リポジトリには含まれていません）

### 免責事項
本プロジェクトは教育・研究目的で作成されています。
使用する機械学習モデルのライセンスについては、各モデルの配布元をご確認ください。