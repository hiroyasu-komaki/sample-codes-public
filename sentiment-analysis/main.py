import os
from modules.dataloader import list_text_files, select_file
from modules.text2sentence import split_text_to_sentences
from modules.model_transformer1 import analyze_with_transformer1
from modules.model_transformer2 import analyze_with_transformer2
from modules.model_dictionary import analyze_with_dictionary

def main():
    print("=" * 60)
    print("感情分析比較検証システム（3モデル比較）")
    print("=" * 60)
    
    # 必要なフォルダを作成
    os.makedirs("txt", exist_ok=True)
    os.makedirs("csv", exist_ok=True)
    os.makedirs("out", exist_ok=True)
    
    # Step 1: テキストファイルをリストアップ
    print("\n[Step 1] テキストファイルの選択")
    text_files = list_text_files("txt")
    
    if not text_files:
        print("エラー: txtフォルダにテキストファイルが見つかりません")
        return
    
    selected_file = select_file(text_files)
    print(f"選択されたファイル: {selected_file}")
    
    # Step 2: テキストを文に分割してCSVに保存
    print("\n[Step 2] テキストを文に分割中...")
    csv_path = split_text_to_sentences(selected_file)
    print(f"分割結果を保存: {csv_path}")
    
    # Step 3: 3つのモデルで感情分析
    print("\n[Step 3] 感情分析を実行中...")
    
    # Model 1: Transformer (jarvisx17)
    print("\n--- Model 1: Transformer (jarvisx17) ---")
    model1_output = analyze_with_transformer1(csv_path)
    print(f"結果を保存: {model1_output}")
    
    # Model 2: Transformer (koheiduck)
    print("\n--- Model 2: Transformer (koheiduck) ---")
    model2_output = analyze_with_transformer2(csv_path)
    print(f"結果を保存: {model2_output}")
    
    # Model 3: Dictionary-based
    print("\n--- Model 3: Dictionary-based ---")
    model3_output = analyze_with_dictionary(csv_path)
    print(f"結果を保存: {model3_output}")
    
    print("\n" + "=" * 60)
    print("全ての処理が完了しました！")
    print("=" * 60)

if __name__ == "__main__":
    main()