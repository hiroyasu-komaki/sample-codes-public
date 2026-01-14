#!/usr/bin/env python3
"""
IT部門スキルアセスメント可視化ツール

Usage:
    python main.py
"""
import os
import sys
from modules.data_loader import SkillDataLoader
from modules import visualizations


def display_menu():
    """メニューを表示"""
    print("\n" + "="*60)
    print("  IT部門スキルアセスメント可視化ツール")
    print("="*60)
    print("\n以下の可視化を実行できます:\n")
    print("  1. ヒートマップ: ロール×スキルカテゴリー別の平均スキルレベル")
    print("  2. レーダーチャート: 専門性別のスキルプロファイル比較")
    print("  4. 散布図マトリックス: スキルギャップ分析（6つの組み合わせ）")
    print("\n  0. すべての可視化を実行")
    print("  q. 終了")
    print("\n" + "="*60)


def create_visualization(choice, data_loader, output_dir):
    """
    選択された可視化を実行
    
    Args:
        choice: ユーザーの選択
        data_loader: データローダー
        output_dir: 出力ディレクトリ
    """
    visualizations_map = {
        '1': ('ヒートマップ', visualizations.create_heatmap),
        '2': ('レーダーチャート', visualizations.create_radar_chart),
        '4': ('散布図マトリックス', visualizations.create_scatter_matrix)
    }
    
    if choice == '0':
        # すべての可視化を実行
        print("\n全ての可視化を実行します...\n")
        for key in sorted(visualizations_map.keys()):
            name, func = visualizations_map[key]
            print(f"[{key}] {name}を作成中...")
            try:
                func(data_loader, output_dir)
            except Exception as e:
                print(f"  ✗ エラーが発生しました: {e}")
        print("\n✓ すべての可視化が完了しました!")
        
    elif choice in visualizations_map:
        # 選択された可視化のみ実行
        name, func = visualizations_map[choice]
        print(f"\n{name}を作成中...")
        try:
            func(data_loader, output_dir)
            print(f"\n✓ {name}の作成が完了しました!")
        except Exception as e:
            print(f"\n✗ エラーが発生しました: {e}")
            
    else:
        print("\n無効な選択です。")


def main():
    """メイン処理"""
    # ディレクトリの設定
    csv_path = 'csv/consolidated_skill_data.csv'
    output_dir = 'output'
    
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    # データの読み込み
    print("\n" + "="*60)
    print("  データ読み込み中...")
    print("="*60)
    
    try:
        data_loader = SkillDataLoader(csv_path)
        data_loader.load_data()
        data_loader.preprocess_data()
        print("✓ データの読み込みが完了しました。\n")
    except FileNotFoundError as e:
        print(f"\n✗ エラー: {e}")
        print(f"  '{csv_path}' が存在することを確認してください。")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ データ読み込み中にエラーが発生しました: {e}")
        sys.exit(1)
    
    # メインループ
    while True:
        display_menu()
        choice = input("\n選択してください (0, 1, 2, 4, q): ").strip()
        
        if choice.lower() == 'q':
            print("\n終了します。")
            break
        
        create_visualization(choice, data_loader, output_dir)
        
        # 継続確認
        if choice != '0':
            continue_choice = input("\n他の可視化を実行しますか? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("\n終了します。")
                break
        else:
            print(f"\n生成された図は '{output_dir}' フォルダに保存されています。")
            view_choice = input("\n他の可視化を実行しますか? (y/n): ").strip().lower()
            if view_choice != 'y':
                print("\n終了します。")
                break


if __name__ == "__main__":
    main()
