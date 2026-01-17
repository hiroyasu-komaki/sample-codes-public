#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ITスキル人材開発 可視化プログラム
メインエントリポイント
"""

import pandas as pd
import sys
import os

# モジュールのインポート
from module.role_radar_chart import create_role_radar_chart
from module.capability_skill_map import create_capability_skill_map
from module.skill_level_heatmap import create_skill_level_heatmap
from module.expertise_portfolio import create_expertise_portfolio
from module.capability_portfolio import create_capability_portfolio
from module.skill_maturity_matrix import create_skill_maturity_matrix
from module.subcategory_analysis import create_subcategory_analysis

def main():
    """
    メイン処理
    """
    print("=" * 60)
    print("ITスキル人材開発 可視化プログラム")
    print("=" * 60)
    
    # データファイルのパス（複数の候補から自動選択）
    data_file_candidates = [
        './csv/converted_skill_data.csv',
        # '/mnt/user-data/uploads/converted_skill_data.csv',
        # 'converted_skill_data.csv',
    ]
    
    data_file = None
    for candidate in data_file_candidates:
        if os.path.exists(candidate):
            data_file = candidate
            break
    
    if data_file is None:
        print("\nエラー: データファイルが見つかりません。以下のパスを確認してください:")
        for candidate in data_file_candidates:
            print(f"  - {candidate}")
        sys.exit(1)
    
    # 出力ディレクトリ
    output_dir = 'png'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # データの読み込み
        print(f"\nデータを読み込んでいます: {data_file}")
        df = pd.read_csv(data_file)
        print(f"データ読み込み完了: {len(df)} 行")
        
        # データの基本情報を表示
        print(f"\n=== データ概要 ===")
        print(f"ユニークなロール数: {df['ロール'].nunique()}")
        print(f"ロール一覧: {', '.join(df['ロール'].unique())}")
        print(f"ユニークなスキル項目数: {df['スキル項目'].nunique()}")
        print(f"カテゴリー数: {df['カテゴリー'].nunique()}")
        print(f"ケイパビリティ数: {df['capability'].nunique()}")
        
        print("\n" + "=" * 60)
        print("可視化を開始します...")
        print("=" * 60)
        
        # === 優先度:高 ===
        print("\n【優先度:高】")
        
        # 1. ロール別スキルレーダーチャート
        print("\n[1/6] ロール別スキルレーダーチャートを作成中...")
        output_path_1 = os.path.join(output_dir, '1_role_radar_chart.png')
        create_role_radar_chart(df, output_path_1)
        
        # 2. ケイパビリティ別スキルマップ
        print("\n[2/6] ケイパビリティ別スキルマップを作成中...")
        output_path_2 = os.path.join(output_dir, '2_capability_skill_map.png')
        create_capability_skill_map(df, output_path_2)
        
        # 3. スキルレベル分布のヒートマップ
        print("\n[3/6] スキルレベル分布のヒートマップを作成中...")
        output_path_3 = os.path.join(output_dir, '3_skill_level_heatmap.png')
        create_skill_level_heatmap(df, output_path_3)
        
        # === 優先度:中 ===
        print("\n【優先度:中】")
        
        # 4. 専門性別の人材ポートフォリオ
        print("\n[4/7] 専門性別の人材ポートフォリオを作成中...")
        output_path_4 = os.path.join(output_dir, '4_expertise_portfolio.png')
        create_expertise_portfolio(df, output_path_4)
        
        # 4b. ケイパビリティ別の人材ポートフォリオ（新規追加）
        print("\n[4b/7] ケイパビリティ別の人材ポートフォリオを作成中...")
        output_path_4b = os.path.join(output_dir, '4b_capability_portfolio.png')
        create_capability_portfolio(df, output_path_4b)
        
        # 5. スキルレベル×スキル項目のマトリクス分析
        print("\n[5/7] スキルレベル×スキル項目のマトリクス分析を作成中...")
        output_path_5 = os.path.join(output_dir, '5_skill_maturity_matrix.png')
        create_skill_maturity_matrix(df, output_path_5)
        
        # 6. サブカテゴリー別の詳細分析
        print("\n[6/7] サブカテゴリー別の詳細分析を作成中...")
        output_path_6 = os.path.join(output_dir, '6_subcategory_analysis.png')
        create_subcategory_analysis(df, output_path_6)
        
        print("\n" + "=" * 60)
        print("すべての可視化が完了しました!")
        print("=" * 60)
        print(f"\n出力ファイル:")
        print(f"  【優先度:高】")
        print(f"  1. {output_path_1}")
        print(f"  2. {output_path_2}")
        print(f"  3. {output_path_3}")
        print(f"  【優先度:中】")
        print(f"  4. {output_path_4}")
        print(f"  4b. {output_path_4b} (NEW!)")
        print(f"  5. {output_path_5}")
        print(f"  6. {output_path_6}")
        print(f"\n出力ディレクトリ: {os.path.abspath(output_dir)}/")
        
    except FileNotFoundError:
        print(f"\nエラー: データファイルが見つかりません: {data_file}")
        sys.exit(1)
    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
