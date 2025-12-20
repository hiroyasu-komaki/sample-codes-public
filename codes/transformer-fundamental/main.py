#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transformer Attention 可視化プログラム
メインエントリポイント
"""

import sys
import os

# モジュールのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.transformer-pseudo import SimpleTransformer


def main():
    """メイン処理"""
    print("=" * 60)
    print("Transformer Attention 可視化プログラム")
    print("=" * 60)
    print()
    
    # Transformerインスタンスを作成
    transformer = SimpleTransformer()
    
    # 出力ディレクトリ
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 文章理解のプロセス
    print("📖 ステップ1: 文章理解のプロセスを可視化中...")
    text = "私が公園を歩いているとき向こうから犬が歩いてきた。私はその犬を見た。"
    understanding_output = os.path.join(output_dir, "attention_understanding.png")
    attention_matrix = transformer.visualize_understanding(text, understanding_output)
    print()
    
    # 2. 文章生成のプロセス
    print("✍️  ステップ2: 文章生成のプロセスを可視化中...")
    generation_output = os.path.join(output_dir, "attention_generation.png")
    transformer.visualize_generation(generation_output)
    print()
    
    # 3. 詳細な生成ステップ
    print("🔍 ステップ3: 1つの生成ステップを詳細に可視化中...")
    detail_output = os.path.join(output_dir, "attention_generation_detail.png")
    transformer.visualize_detailed_generation_step(detail_output)
    print()
    
    print("=" * 60)
    print("✅ すべての可視化が完了しました！")
    print()
    print("生成されたファイル:")
    print(f"  1. {understanding_output}  - 文章理解のAttentionマップ")
    print(f"  2. {generation_output}     - 文章生成の各ステップ")
    print(f"  3. {detail_output} - 生成ステップの詳細")
    print("=" * 60)


if __name__ == "__main__":
    main()
