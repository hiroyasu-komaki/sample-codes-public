"""
PDFファイルからテキストを抽出するモジュール
"""
import os
from pathlib import Path
import PyPDF2


class PDFExtractor:
    def __init__(self, pdf_folder, txt_folder):
        """
        PDFExtractorの初期化
        
        Args:
            pdf_folder (str): PDFファイルが格納されているフォルダ
            txt_folder (str): テキストファイルを出力するフォルダ
        """
        self.pdf_folder = pdf_folder
        self.txt_folder = txt_folder
    
    def extract_text_from_pdf(self, pdf_path):
        """
        PDFファイルからテキストを抽出
        
        Args:
            pdf_path (str): PDFファイルのパス
            
        Returns:
            str: 抽出されたテキスト
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"エラー: {pdf_path} の読み込みに失敗しました - {e}")
        
        return text
    
    def save_text_to_file(self, text, output_path):
        """
        テキストをファイルに保存
        
        Args:
            text (str): 保存するテキスト
            output_path (str): 出力ファイルのパス
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(text)
        except Exception as e:
            print(f"エラー: {output_path} への書き込みに失敗しました - {e}")
    
    def extract_all(self):
        """
        pdf_folder内のすべてのPDFファイルを処理してテキストファイルを出力
        """
        pdf_files = list(Path(self.pdf_folder).glob('*.pdf'))
        
        if not pdf_files:
            print(f"警告: {self.pdf_folder} にPDFファイルが見つかりません")
            return
        
        for pdf_file in pdf_files:
            print(f"処理中: {pdf_file.name}")
            
            # テキストを抽出
            text = self.extract_text_from_pdf(str(pdf_file))
            
            # 出力ファイル名を作成
            output_filename = pdf_file.stem + '.txt'
            output_path = os.path.join(self.txt_folder, output_filename)
            
            # テキストを保存
            self.save_text_to_file(text, output_path)
            print(f"完了: {output_filename}")
