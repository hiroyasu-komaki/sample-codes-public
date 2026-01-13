#!/usr/bin/env python3
"""
IT人材需要計算プログラム - メインエントリポイント

CSVフォルダ内のプロジェクトポートフォリオを読み込み、
スキル需要を計算してoutフォルダに出力します。

使用方法:
    python main.py

フォルダ構成:
    CSV/            入力CSVファイルを格納
    intermediate/   中間ファイル（分類結果）
    out/            出力CSVファイル（スキル需要追加）
    config.yaml     設定ファイル
    modules/        プログラムモジュール

ステップ説明:
    ステップ1: プロジェクト分類処理
        - CSVフォルダのファイルを読み込み
        - プロジェクト規模・種別・技術領域を判定
        - 結果をintermediateフォルダに保存
        - 用途: 分類精度の確認、YAML設定の微調整
    
    ステップ2: スキル需要計算
        - intermediateフォルダの分類済みファイルを読み込み
        - ケイパビリティ別の需要を計算
        - 結果をoutフォルダに保存
        - 用途: 人手による分類結果の修正後の再計算
"""

from pathlib import Path
import sys
from modules.demand_calculator import DemandCalculator
from modules.data_validator import DataValidator


def select_step():
    """実行するステップを選択"""
    print("\n実行するステップを選択してください:")
    print("  1: ステップ1のみ（分類処理）")
    print("  2: ステップ2のみ（需要計算）")
    print("  Enter: 両方実行（デフォルト）")
    
    while True:
        choice = input("\n選択 [Enter]: ").strip()
        
        if choice == '':
            return 'all'
        elif choice == '1':
            return '1'
        elif choice == '2':
            return '2'
        else:
            print("エラー: 1、2、またはEnterキーを入力してください。")
            continue


def main():
    """メイン関数"""
    
    print("=" * 80)
    print("IT人材需要計算プログラム v2.0")
    print("=" * 80)
    
    # ステップの選択（インタラクティブプロンプト）
    step = select_step()
    
    # 実行ステップの表示
    print("\n" + "=" * 80)
    if step == '1':
        print("実行モード: ステップ1のみ（分類処理）")
    elif step == '2':
        print("実行モード: ステップ2のみ（需要計算）")
    else:
        print("実行モード: 全ステップ実行（分類→需要計算）")
    print("=" * 80)
    
    # フォルダの設定
    csv_folder = Path('CSV')
    intermediate_folder = Path('intermediate')
    out_folder = Path('out')
    
    # ステップに応じたフォルダ存在確認
    if step in ['1', 'all']:
        # ステップ1を実行する場合はCSVフォルダが必要
        if not csv_folder.exists():
            print(f"\nエラー: '{csv_folder}' フォルダが見つかりません。")
            print(f"'{csv_folder}' フォルダを作成し、CSVファイルを配置してください。")
            sys.exit(1)
    
    if step == '2':
        # ステップ2のみの場合はintermediateフォルダが必要
        if not intermediate_folder.exists():
            print(f"\nエラー: '{intermediate_folder}' フォルダが見つかりません。")
            print(f"ステップ2を実行するには、先にステップ1を実行してください。")
            sys.exit(1)
    
    # 出力フォルダの作成
    intermediate_folder.mkdir(exist_ok=True)
    out_folder.mkdir(exist_ok=True)
    print(f"\n中間ファイルフォルダ: {intermediate_folder}")
    print(f"最終出力フォルダ: {out_folder}")
    
    # 計算オブジェクトの作成
    calculator = DemandCalculator()
    validator = DataValidator()
    
    # ========================================================================
    # 設定ファイルのバリデーション（全ステップの前に実行）
    # ========================================================================
    print("\n" + "=" * 80)
    print("設定ファイルの検証")
    print("=" * 80)
    
    config_valid = validator.validate_config_file()
    if not config_valid:
        print("\n" + "=" * 80)
        print("❌ 設定ファイルのバリデーションに失敗しました")
        print("=" * 80)
        print("\nconfig/calc_assumptions.yaml のエラーを修正してから再実行してください。")
        print("処理を中断します。")
        sys.exit(1)
    
    # ========================================================================
    # データバリデーション（全ステップの前に実行）
    # ========================================================================
    if step in ['1', 'all']:
        print("\n" + "=" * 80)
        print("データバリデーション: 入力データの品質チェック")
        print("=" * 80)
        
        # CSVファイルの検索
        csv_files = list(csv_folder.glob('*.csv'))
        
        if not csv_files:
            print(f"\nエラー: '{csv_folder}' フォルダにCSVファイルが見つかりません。")
            sys.exit(1)
        
        print(f"\n検証対象CSVファイル: {len(csv_files)}件")
        for csv_file in csv_files:
            print(f"  - {csv_file.name}")
        
        # 全てのCSVファイルをバリデーション
        all_valid = True
        for csv_file in csv_files:
            is_valid, _ = validator.validate_csv_file(csv_file)
            if not is_valid:
                all_valid = False
        
        # バリデーション失敗時は処理を中断
        if not all_valid:
            print("\n" + "=" * 80)
            print("❌ データバリデーションに失敗しました")
            print("=" * 80)
            print("\nエラーを修正してから再実行してください。")
            print("処理を中断します。")
            sys.exit(1)
        
        print("\n" + "=" * 80)
        print("✅ データバリデーション完了: すべてのファイルが検証を通過しました")
        print("=" * 80)
        
        # ユーザーに確認を求める（警告がある場合）
        if any(len(validator.warnings) > 0 for csv_file in csv_files 
               for validator in [DataValidator()] if validator.validate_csv_file(csv_file)[0]):
            print("\n⚠️  警告が検出されました。このまま処理を続行しますか？")
            print("  Enter: 続行")
            print("  Ctrl+C: 中断")
            try:
                input("\n続行するにはEnterキーを押してください...")
            except KeyboardInterrupt:
                print("\n\n処理を中断しました。")
                sys.exit(0)
    
    # ========================================================================
    # ステップ1: 分類処理（中間ファイル生成）
    # ========================================================================
    if step in ['1', 'all']:
        print("\n" + "=" * 80)
        print("ステップ1: プロジェクト分類処理を開始します")
        print("=" * 80)
        
        # CSVファイルの検索（バリデーション済み）
        csv_files = list(csv_folder.glob('*.csv'))
        
        print(f"\n処理対象CSVファイル: {len(csv_files)}件")
        for csv_file in csv_files:
            print(f"  - {csv_file.name}")
        
        for csv_file in csv_files:
            intermediate_file = intermediate_folder / f"classified_{csv_file.name}"
            calculator.process_csv_file_classify(csv_file, intermediate_file)
        
        print("\n" + "=" * 80)
        print("ステップ1: 分類処理が完了しました")
        print("=" * 80)
        
        # 中間ファイルの一覧
        print(f"\n生成された中間ファイル:")
        for intermediate_file in intermediate_folder.glob('classified_*.csv'):
            print(f"  - {intermediate_file.name}")
        
        if step == '1':
            # ステップ1のみの場合はここで終了
            print("\n" + "=" * 80)
            print("処理が完了しました（ステップ1のみ実行）")
            print("=" * 80)
            print(f"\n中間ファイルを確認してください: {intermediate_folder.absolute()}")
            print("\n次のステップ:")
            print("  1. intermediateフォルダ内のCSVファイルで分類結果を確認")
            print("  2. 必要に応じてcalc_assumptions.yamlを微調整")
            print("  3. 再度ステップ1を実行するか、ステップ2で需要計算を実行")
            return
    
    # ========================================================================
    # ステップ2: スキル需要計算（中間ファイルから最終結果を生成）
    # ========================================================================
    if step in ['2', 'all']:
        print("\n" + "=" * 80)
        print("ステップ2: スキル需要計算を開始します")
        print("=" * 80)
        
        intermediate_files = list(intermediate_folder.glob('classified_*.csv'))
        
        if not intermediate_files:
            print(f"\nエラー: '{intermediate_folder}' フォルダに分類済みCSVファイルが見つかりません。")
            print(f"先にステップ1を実行してください。")
            sys.exit(1)
        
        print(f"\n処理する中間ファイル: {len(intermediate_files)}件")
        for intermediate_file in intermediate_files:
            print(f"  - {intermediate_file.name}")
        
        for intermediate_file in intermediate_files:
            # 元のファイル名を復元
            original_name = intermediate_file.name.replace('classified_', '')
            output_file = out_folder / original_name
            calculator.process_csv_file_demand(intermediate_file, output_file)
        
        print("\n" + "=" * 80)
        print("ステップ2: スキル需要計算が完了しました")
        print("=" * 80)
        
        # 出力されたファイルの一覧
        print(f"\n最終出力ファイル:")
        for output_file in out_folder.glob('*.csv'):
            print(f"  - {output_file.name}")
    
    # ========================================================================
    # 完了メッセージ
    # ========================================================================
    print("\n" + "=" * 80)
    if step == 'all':
        print("すべての処理が完了しました")
    elif step == '2':
        print("処理が完了しました（ステップ2のみ実行）")
    print("=" * 80)
    
    if step in ['2', 'all']:
        print(f"\n最終結果: {out_folder.absolute()}")
    if step == 'all':
        print(f"中間ファイル: {intermediate_folder.absolute()}")



if __name__ == '__main__':
    main()
