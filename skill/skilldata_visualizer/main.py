#!/usr/bin/env python3
"""
スキルデータ可視化プログラム - メインエントリポイント

個人プロファイル分析と集団分析の2つの機能を提供
"""

import sys
import argparse
from pathlib import Path

from data_loader import DataLoader
from individual_analyzer import IndividualAnalyzer
from group_analyzer import GroupAnalyzer
from standard_analyzer import StandardAnalyzer
from utils import setup_japanese_font


def parse_arguments():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description='スキルデータを分析・可視化します（個人プロファイル・集団分析）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
実行例:
  python main.py group                         # 集団分析
  python main.py standard                      # スキル標準レーダーチャート作成
  python main.py individual --person sample_001_engineer_focused  # 特定個人のみ
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['individual', 'group', 'standard'],
        help='分析モード: individual（個人レーダーチャート）、group（集団分析）、standard（スキル標準）'
    )
    
    parser.add_argument(
        '--person',
        help='個人分析時の対象者名（必須）'
    )
    
    return parser.parse_args()


def validate_file(filepath):
    """ファイルの存在確認"""
    file_path = Path(filepath)
    if not file_path.exists():
        print(f"エラー: ファイル '{filepath}' が見つかりません")
        print(f"現在のディレクトリ: {Path.cwd()}")
        return False
    
    if not filepath.endswith('.csv'):
        print(f"エラー: '{filepath}' はCSVファイルではありません")
        return False
    
    return True


def main():
    """メイン実行関数"""
    try:
        # 引数解析
        args = parse_arguments()
        
        # individualモードでは--personが必須
        if args.mode == 'individual' and not args.person:
            print("エラー: individualモードでは --person オプションが必須です")
            sys.exit(1)
        
        # 日本語フォント設定
        setup_japanese_font()
        
        # 分析実行
        if args.mode == 'individual':
            # 固定ファイルパス
            data_file = 'input/consolidated_skill_data.csv'
            
            # ファイル検証
            if not validate_file(data_file):
                sys.exit(1)
            
            # データ読み込み
            loader = DataLoader(data_file)
            df = loader.load_data()
            
            if df is None:
                print("エラー: データの読み込みに失敗しました")
                sys.exit(1)
            
            print("\n個人レーダーチャート分析を開始...")
            analyzer = IndividualAnalyzer(df)
            analyzer.create_radar_chart(args.person)
        
        elif args.mode == 'standard':
            print("スキル標準レーダーチャート分析を開始...")
            analyzer = StandardAnalyzer()
            analyzer.create_skill_standard_radar()
            
        elif args.mode == 'group':
            # 固定ファイルパス
            data_file = 'input/consolidated_skill_data.csv'
            
            # ファイル検証
            if not validate_file(data_file):
                sys.exit(1)
            
            # データ読み込み
            loader = DataLoader(data_file)
            df = loader.load_data()
            
            if df is None:
                print("エラー: データの読み込みに失敗しました")
                sys.exit(1)
            
            print("集団分析を開始...")
            analyzer = GroupAnalyzer(df)
            analyzer.create_skill_sufficiency_analysis()

        print("\n分析完了！")
    
    except KeyboardInterrupt:
        print("\n\nユーザーによって中断されました")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()