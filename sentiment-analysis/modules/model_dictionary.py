# model_dictionary.py
# シンプルな辞書ベースの感情分析
import pandas as pd
import os

# 感情辞書の定義
POSITIVE_WORDS = [
    '良い', '素晴らしい', '最高', '満足', '嬉しい', '楽しい', '快適', '便利',
    '親切', '丁寧', '優秀', '安心', '感謝', 'おすすめ', '好き', '美味しい',
    '綺麗', '素敵', '完璧', '最適', '快適', 'スムーズ', '効果的', '魅力的',
    '優れる', '充実', '満足', '感動', '幸せ', '喜ぶ', '助かる', '良好',
    '高品質', '適切', '十分', '豊富', '改善', '向上', '成功', '達成'
]

NEGATIVE_WORDS = [
    '悪い', 'ダメ', '最悪', '不満', '残念', '困る', '嫌', 'つまらない',
    '不快', '遅い', '高い', '不便', '面倒', '複雑', '難しい', '問題',
    '失敗', 'ミス', 'エラー', '故障', '不安', '心配', '危険', '不適切',
    '不十分', '欠ける', '少ない', '劣る', '悲しい', '怒る', 'イライラ',
    '後悔', '不愉快', '苦痛', '疲れる', '無駄', '改悪', '低品質'
]

# 強調表現
INTENSIFIERS = ['非常に', 'とても', 'かなり', 'すごく', '大変', '本当に', '実に', 'めちゃくちゃ']
NEGATIONS = ['ない', 'ません', 'ず', 'ぬ', '無い']

def analyze_with_dictionary(csv_path):
    """
    辞書ベースで感情分析を実行
    """
    # CSVファイルを読み込み
    df = pd.read_csv(csv_path)
    
    print("  辞書ベース分析を実行中...")
    
    # 各文を分析
    results = []
    for idx, row in df.iterrows():
        sentence = row['sentence']
        score = calculate_sentiment_score(sentence)
        
        # 感情判定（統一閾値：0.2）
        if score > 0.2:
            sentiment = 'ポジティブ'
        elif score < -0.2:
            sentiment = 'ネガティブ'
        else:
            sentiment = '中立'
        
        results.append({
            'sentiment_score': score,
            'sentiment': sentiment
        })
        
        # 進捗表示
        if (idx + 1) % 100 == 0:
            print(f"  処理中: {idx + 1}/{len(df)}")
    
    # 結果を追加（統一フォーマット）
    df['score'] = [r['sentiment_score'] for r in results]
    df['positive'] = None  # 辞書ベースでは個別スコアなし
    df['negative'] = None  # 辞書ベースでは個別スコアなし
    df['sentiment'] = [r['sentiment'] for r in results]
    df['model_name'] = 'dictionary'
    
    # 統計情報を表示
    print("\n[Dictionary-based 統計情報]")
    print(f"総文数: {len(df)}")
    print("\n感情分布:")
    print(df['sentiment'].value_counts())
    print(f"\n平均スコア: {df['score'].mean():.4f}")
    print(f"最大スコア: {df['score'].max():.4f}")
    print(f"最小スコア: {df['score'].min():.4f}")
    
    # 結果を保存
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    output_path = os.path.join("out", f"{base_name}_dictionary.csv")
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    return output_path

def calculate_sentiment_score(text):
    """
    テキストから感情スコアを計算
    """
    # ポジティブ・ネガティブ単語のカウント
    positive_count = sum(1 for word in POSITIVE_WORDS if word in text)
    negative_count = sum(1 for word in NEGATIVE_WORDS if word in text)
    
    # 強調表現の検出
    has_intensifier = any(intensifier in text for intensifier in INTENSIFIERS)
    intensifier_weight = 1.5 if has_intensifier else 1.0
    
    # 否定表現の検出（簡易版）
    has_negation = any(negation in text for negation in NEGATIONS)
    
    # スコア計算
    if has_negation:
        # 否定がある場合、ポジティブとネガティブを反転
        score = (negative_count - positive_count) * intensifier_weight * 0.3
    else:
        score = (positive_count - negative_count) * intensifier_weight * 0.3
    
    # -1.0 〜 1.0 の範囲に正規化
    score = max(-1.0, min(1.0, score))
    
    return score