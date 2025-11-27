# text2sentence.py
import re
import pandas as pd
import os

def split_text_to_sentences(text_file_path):
    """
    テキストファイルを文に分割してCSVに保存
    """
    # テキストファイルを読み込み
    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 文に分割（句点、感嘆符、疑問符で分割）
    sentences = re.split(r'[。！？\n]+', text)
    
    # 空白文を除外
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # データフレームに変換
    df = pd.DataFrame({
        'sentence_id': range(1, len(sentences) + 1),
        'sentence': sentences
    })
    
    # CSVファイルとして保存
    base_name = os.path.splitext(os.path.basename(text_file_path))[0]
    csv_path = os.path.join("csv", f"{base_name}_sentences.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"文の数: {len(sentences)}")
    
    return csv_path
