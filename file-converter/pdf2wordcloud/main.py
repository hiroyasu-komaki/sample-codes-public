"""
PDFからWordcloudを作成するメインプログラム
"""
import os
from pdf_extractor import PDFExtractor
from wordcloud_generator import WordCloudGenerator


def main():
    # フォルダの作成
    os.makedirs('pdf', exist_ok=True)
    os.makedirs('txt', exist_ok=True)
    os.makedirs('png', exist_ok=True)
    
    # PDFからテキストを抽出
    print("PDFファイルからテキストを抽出中...")
    pdf_extractor = PDFExtractor('pdf', 'txt')
    pdf_extractor.extract_all()
    
    # テキストからWordcloudを生成
    print("Wordcloudを生成中...")
    wordcloud_gen = WordCloudGenerator('txt', 'png', 'stopwords.csv')
    wordcloud_gen.generate_all()
    
    print("処理が完了しました。")


if __name__ == "__main__":
    main()
