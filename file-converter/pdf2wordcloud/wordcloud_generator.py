"""
テキストファイルからWordcloudを生成するモジュール
"""
import os
from pathlib import Path
import csv
from wordcloud import WordCloud
import matplotlib.pyplot as plt


class WordCloudGenerator:
    def __init__(self, txt_folder, png_folder, stopwords_file):
        """
        WordCloudGeneratorの初期化
        
        Args:
            txt_folder (str): テキストファイルが格納されているフォルダ
            png_folder (str): PNG画像を出力するフォルダ
            stopwords_file (str): ストップワードのCSVファイルパス
        """
        self.txt_folder = txt_folder
        self.png_folder = png_folder
        self.stopwords = self.load_stopwords(stopwords_file)
    
    def load_stopwords(self, stopwords_file):
        """
        CSVファイルからストップワードを読み込み
        
        Args:
            stopwords_file (str): ストップワードのCSVファイルパス
            
        Returns:
            set: ストップワードのセット
        """
        stopwords = set()
        
        if not os.path.exists(stopwords_file):
            print(f"警告: {stopwords_file} が見つかりません。ストップワードなしで処理します。")
            return stopwords
        
        try:
            with open(stopwords_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    for word in row:
                        if word.strip():
                            stopwords.add(word.strip())
        except Exception as e:
            print(f"エラー: {stopwords_file} の読み込みに失敗しました - {e}")
        
        return stopwords
    
    def read_text_file(self, txt_path):
        """
        テキストファイルを読み込み
        
        Args:
            txt_path (str): テキストファイルのパス
            
        Returns:
            str: テキスト内容
        """
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"エラー: {txt_path} の読み込みに失敗しました - {e}")
            return ""
    
    def get_japanese_font_path(self):
        """
        日本語フォントのパスを取得
        
        Returns:
            str: フォントパス（見つからない場合はNone）
        """
        import platform
        import os
        
        system = platform.system()
        
        # OSごとの日本語フォントパスのリスト
        font_paths = []
        
        if system == 'Darwin':  # macOS
            font_paths = [
                '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
                '/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc',
                '/Library/Fonts/Arial Unicode.ttf'
            ]
        elif system == 'Windows':
            font_paths = [
                'C:\\Windows\\Fonts\\msgothic.ttc',
                'C:\\Windows\\Fonts\\meiryo.ttc',
                'C:\\Windows\\Fonts\\YuGothM.ttc'
            ]
        elif system == 'Linux':
            font_paths = [
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf',
                '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
            ]
        
        # 存在するフォントを探す
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        
        print("警告: 日本語フォントが見つかりません。デフォルトフォントを使用します。")
        return None
    
    def generate_wordcloud(self, text, output_path):
        """
        テキストからWordcloudを生成して保存
        
        Args:
            text (str): 入力テキスト
            output_path (str): 出力画像のパス
        """
        if not text.strip():
            print(f"警告: テキストが空です。Wordcloudを生成できません。")
            return
        
        try:
            # 日本語フォントを取得
            font_path = self.get_japanese_font_path()
            
            # Wordcloudを生成
            wordcloud = WordCloud(
                width=800,
                height=600,
                background_color='white',
                stopwords=self.stopwords,
                font_path=font_path,
                collocations=False
            ).generate(text)
            
            # 画像を保存
            plt.figure(figsize=(10, 7.5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"エラー: Wordcloudの生成に失敗しました - {e}")
    
    def generate_all(self):
        """
        txt_folder内のすべてのテキストファイルを処理してWordcloudを出力
        """
        txt_files = list(Path(self.txt_folder).glob('*.txt'))
        
        if not txt_files:
            print(f"警告: {self.txt_folder} にテキストファイルが見つかりません")
            return
        
        for txt_file in txt_files:
            print(f"処理中: {txt_file.name}")
            
            # テキストを読み込み
            text = self.read_text_file(str(txt_file))
            
            # 出力ファイル名を作成
            output_filename = txt_file.stem + '.png'
            output_path = os.path.join(self.png_folder, output_filename)
            
            # Wordcloudを生成
            self.generate_wordcloud(text, output_path)
            print(f"完了: {output_filename}")
