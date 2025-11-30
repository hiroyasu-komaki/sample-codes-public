#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordCloud生成メインスクリプト

使用方法:
    python main.py

機能:
    - inフォルダ内のテキストファイル（.txt, .csv, .md）を自動検出
    - 日本語/英語を自動判定して適切な前処理を実行
    - WordCloudを生成してoutフォルダにPNG形式で保存
    - 複数ファイルの一括処理に対応
"""

import os
import sys
from wordcloud_generator import WordCloudGenerator

def setup_directories():
    """
    必要なディレクトリを作成
    """
    directories = ['in', 'out']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"ディレクトリを作成しました: {directory}/")

def check_input_files(input_dir):
    """
    入力ファイルの存在をチェック
    """
    if not os.path.exists(input_dir):
        print(f"❌ 入力ディレクトリが存在しません: {input_dir}")
        return False
    
    supported_extensions = ['.txt', '.csv', '.md']
    input_files = [
        f for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f)) and
           any(f.lower().endswith(ext) for ext in supported_extensions)
    ]
    
    if not input_files:
        print(f"❌ 対応するファイル（.txt, .csv, .md）が見つかりません: {input_dir}")
        print("対応ファイルをinフォルダに配置してください。")
        return False
    
    print(f"✅ {len(input_files)}個の入力ファイルを検出しました:")
    for file in input_files:
        print(f"   - {file}")
    
    return True

def main():
    """
    メイン実行関数
    """
    print("🎨 WordCloud生成ツール")
    print("=" * 50)
    
    # 設定
    input_dir = "in"
    output_dir = "out"
    
    # ディレクトリのセットアップ
    setup_directories()
    
    # 入力ファイルの確認
    if not check_input_files(input_dir):
        return
    
    # WordCloudGeneratorのインスタンス作成
    generator = WordCloudGenerator()
    
    print("\n📊 WordCloud生成開始...")
    
    # WordCloudのパラメータ設定（必要に応じてカスタマイズ可能）
    wordcloud_params = {
        'width': 1200,
        'height': 600,
        'background_color': 'white',
        'max_words': 150,
        'colormap': 'viridis',
        'relative_scaling': 0.5,
        'min_font_size': 10
    }
    
    # 一括処理実行
    generator.batch_process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        **wordcloud_params
    )
    
    print("\n" + "=" * 50)
    print("🎉 すべての処理が完了しました！")
    print(f"生成されたWordCloudは {output_dir}/ フォルダをご確認ください。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  処理が中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)
