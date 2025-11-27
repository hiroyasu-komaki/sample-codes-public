import pandas as pd
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def analyze_with_transformer2(csv_path):
    """
    Transformerモデル2(Kohoku BERT)で感情分析を実行
    """
    # CSVファイルを読み込み
    df = pd.read_csv(csv_path)
    
    # モデルとトークナイザーの読み込み
    print("  モデルを読み込んでいます...")
    model_name = "koheiduck/bert-japanese-finetuned-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    # 各文を分析
    results = []
    for idx, row in df.iterrows():
        sentence = row['sentence']
        
        # トークン化
        inputs = tokenizer(
            sentence,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        # 推論
        with torch.no_grad():
            outputs = model(**inputs)
            scores = torch.nn.functional.softmax(outputs.logits, dim=1)
        
        positive_score = scores[0][1].item()
        negative_score = scores[0][0].item()
        
        # スコアを-1〜1の範囲に変換（統一形式）
        total_score = positive_score - negative_score
        
        # 感情判定（統一閾値：0.2）
        if total_score > 0.2:
            sentiment = 'ポジティブ'
        elif total_score < -0.2:
            sentiment = 'ネガティブ'
        else:
            sentiment = '中立'
        
        results.append({
            'positive_score': positive_score,
            'negative_score': negative_score,
            'total_score': total_score,
            'sentiment': sentiment
        })
        
        # 進捗表示
        if (idx + 1) % 50 == 0:
            print(f"  処理中: {idx + 1}/{len(df)}")
    
    # 結果を追加（統一フォーマット）
    df['score'] = [r['total_score'] for r in results]
    df['positive'] = [r['positive_score'] for r in results]
    df['negative'] = [r['negative_score'] for r in results]
    df['sentiment'] = [r['sentiment'] for r in results]
    df['model_name'] = 'transformer2'
    
    # 統計情報を表示
    print("\n[Transformer Model 2 統計情報]")
    print(f"総文数: {len(df)}")
    print("\n感情分布:")
    print(df['sentiment'].value_counts())
    print(f"\n平均トータルスコア: {df['score'].mean():.4f}")
    print(f"平均ポジティブスコア: {df['positive'].mean():.4f}")
    print(f"平均ネガティブスコア: {df['negative'].mean():.4f}")
    
    # 結果を保存
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    output_path = os.path.join("out", f"{base_name}_transformer2.csv")
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    return output_path