from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import warnings
from collections import Counter
import os

# 警告を抑制
warnings.filterwarnings('ignore', category=UserWarning, module='tqdm')

class WordCloudGenerator:
    """
    WordCloud生成クラス
    """
    
    def __init__(self):
        self.japanese_stopwords = {
            'の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 'いる',
            'する', 'です', 'ます', 'だ', 'である', 'から', 'まで', 'より', 'も', 'や', 'か',
            'これ', 'それ', 'あれ', 'この', 'その', 'あの', 'ここ', 'そこ', 'あそこ',
            'こう', 'そう', 'ああ', 'どう', 'なる', 'なっ', 'なり', 'なら',
            'ない', 'なく', 'なかっ', 'ました', 'ません', 'でしょ', 'でき', 'よう',
            'ため', 'こと', 'もの', 'とき', 'ところ', 'はず', 'わけ', 'そのため', 'なし'
        }
    
    def get_japanese_font_path(self):
        """
        日本語フォントのパスを自動検出
        """
        font_paths = [
            # macOS
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/Library/Fonts/Arial Unicode MS.ttf",
            # Windows
            "C:/Windows/Fonts/msgothic.ttc",
            "C:/Windows/Fonts/msmincho.ttc",
            "C:/Windows/Fonts/NotoSansCJK-Regular.ttc",
            # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf"
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                print(f"使用フォント: {font_path}")
                return font_path
        print("警告: 日本語フォントが見つかりません。英語フォントを使用します。")
        return None

    def is_valid_word(self, word, stopwords):
        """
        単語が有効かどうかを判定する厳密なフィルタ
        """
        # 長さチェック
        if len(word) < 2:
            return False

        # ストップワードチェック
        if word in stopwords:
            return False

        # 記号パターンの除外
        symbol_patterns = [
            r'^[|\-#\+:─├──]+$',          # 罫線、記号類
            r'^[0-9]+[:：]$',             # 数字+コロン (1:, 2:など)
            r'^[\-]{2,}$',                # 連続ハイフン (---, ----など)
            r'^[#]{2,}$',                 # 連続シャープ (##, ###など)
            r'^[`]{1,}$',                 # バッククォート (`, ```, など)
            r'^[\+\-\*=]{2,}$',           # 演算子の連続
            r'^[()（）\[\]【】「」『』]+$',  # 括弧類のみ
            r'^[.,。、!?！？]+$',         # 句読点のみ
            r'^[0-9\s\W]*$',              # 数字・空白・記号のみ
            r'^[A-Z]{1,3}$',              # 短い英字大文字 (C, APO, BAIなど)
        ]
        for pattern in symbol_patterns:
            if re.match(pattern, word):
                return False

        # ひらがなのみを除外
        if re.match(r'^[ぁ-ん]+$', word):
            return False

        # 有効な単語の条件
        has_japanese = re.search(r'[ひらがなカタカナ漢字]', word)
        has_meaningful_english = re.match(r'^[a-zA-Z]{4,}$', word)  # 4文字以上の英単語

        return has_japanese or has_meaningful_english

    def preprocess_japanese_text(self, text):
        """
        日本語テキストの前処理（MeCab使用）
        """
        # タイムスタンプを除去
        clean_text = re.sub(r'\[\d+\.\d+s -> \d+\.\d+s\]', '', text)

        try:
            import MeCab

            # MeCabで分かち書き
            tagger = MeCab.Tagger('-Owakati')
            wakati_text = tagger.parse(clean_text)

            # 単語をフィルタリング
            words = wakati_text.split()
            filtered_words = [
                word.strip() for word in words
                if self.is_valid_word(word.strip(), self.japanese_stopwords)
            ]

            print(f"MeCab処理完了: {len(filtered_words)}個の単語を抽出")
            return ' '.join(filtered_words)

        except ImportError:
            print("MeCabがインストールされていません。基本的な前処理を実行します。")
            return self.apply_basic_filtering(clean_text, self.japanese_stopwords)
        except Exception as e:
            print(f"MeCab処理エラー: {e}")
            return self.apply_basic_filtering(clean_text, self.japanese_stopwords)

    def preprocess_english_text(self, text):
        """
        英語テキストの前処理（NLTK使用）
        """
        # タイムスタンプを除去
        clean_text = re.sub(r'\[\d+\.\d+s -> \d+\.\d+s\]', '', text)

        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize

            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)

            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(clean_text.lower())

            filtered_text = [
                word for word in word_tokens
                if word.isalpha() and len(word) > 2 and word not in stop_words
            ]

            print(f"NLTK処理完了: {len(filtered_text)}個の単語を抽出")
            return ' '.join(filtered_text)

        except Exception as e:
            print(f"NLTK処理エラー: {e}")
            # 基本的なフィルタリング
            words = clean_text.split()
            filtered_words = [
                word for word in words
                if len(word) > 2 and word.isalpha()
            ]
            return ' '.join(filtered_words)

    def apply_basic_filtering(self, text, stopwords):
        """
        MeCab未使用時の基本フィルタリング
        """
        words = text.split()
        filtered_words = [
            word.strip() for word in words
            if self.is_valid_word(word.strip(), stopwords)
        ]

        print(f"基本フィルタリング完了: {len(filtered_words)}個の単語を抽出")
        return ' '.join(filtered_words)

    def detect_language_and_preprocess(self, text):
        """
        言語を自動検出して適切な前処理を適用
        """
        # 日本語文字が含まれているかチェック
        if re.search(r'[ひらがなカタカナ漢字]', text):
            print("日本語テキストを検出しました")
            return self.preprocess_japanese_text(text), "japanese"
        else:
            print("英語テキストとして処理します")
            return self.preprocess_english_text(text), "english"

    def create_wordcloud_with_params(self, clean_text, language, **params):
        """
        パラメータを指定してWordCloudを生成
        """
        wordcloud_params = {
            'width': 800,
            'height': 400,
            'background_color': 'white',
            'max_words': 100,
            'colormap': 'viridis'
        }

        # パラメータを更新
        wordcloud_params.update(params)

        # 日本語の場合はフォントを設定
        if language == "japanese":
            font_path = self.get_japanese_font_path()
            if font_path:
                wordcloud_params['font_path'] = font_path

        return WordCloud(**wordcloud_params).generate(clean_text)

    def create_wordcloud_from_file(self, input_filepath, output_filepath, title="WordCloud", **params):
        """
        ファイルからWordCloudを作成してPNG形式で保存
        """
        try:
            with open(input_filepath, "r", encoding="utf-8") as file:
                text = file.read()

            clean_text, language = self.detect_language_and_preprocess(text)

            if not clean_text.strip():
                print("有効な単語が見つかりませんでした")
                return False

            wordcloud = self.create_wordcloud_with_params(clean_text, language, **params)

            # WordCloudを生成・保存
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(title, fontsize=16, pad=20)
            
            # 出力ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
            
            plt.savefig(output_filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()  # メモリ節約のため図を閉じる
            
            print(f"WordCloudを保存しました: {output_filepath}")
            return True
            
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return False

    def batch_process_directory(self, input_dir, output_dir, **params):
        """
        ディレクトリ内の全ファイルを一括処理
        """
        if not os.path.exists(input_dir):
            print(f"入力ディレクトリが存在しません: {input_dir}")
            return
        
        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 対応するファイル拡張子
        supported_extensions = ['.txt', '.csv', '.md']
        
        processed_count = 0
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            
            # ファイルかどうか、対応拡張子かどうかをチェック
            if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in supported_extensions):
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_dir, f"{base_name}_wordcloud.png")
                
                print(f"\n処理中: {filename}")
                if self.create_wordcloud_from_file(file_path, output_path, title=f"{base_name} WordCloud", **params):
                    processed_count += 1
        
        print(f"\n✅ 一括処理完了! {processed_count}個のファイルを処理しました。")
