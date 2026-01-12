#!/usr/bin/env python3
"""
プロジェクトポートフォリオ分析 - メインエントリポイント

出力:
    png/ ディレクトリに以下のグラフが生成されます:
    - capability_demand_charts.png (ケイパビリティ全体の推移)
    - capability_by_tech_stacked.png (技術領域別・積み上げ)
    - capability_by_tech_lines.png (技術領域別・折れ線)
    - supply_demand_balance.png (需給バランス)
"""

import os
import sys
import subprocess
from pathlib import Path

def find_csv_files():
    """csv/ディレクトリ内のCSVファイルを検出"""
    csv_dir = Path('csv')
    
    if not csv_dir.exists():
        print("エラー: csv/ ディレクトリが見つかりません。")
        print("csv/ ディレクトリを作成し、CSVファイルを配置してください。")
        return None, None
    
    # demand_data.csv と supply_data.csv を検索
    demand_file = csv_dir / 'demand_data.csv'
    supply_file = csv_dir / 'supply_data.csv'
    
    if not demand_file.exists():
        print("エラー: demand_data.csv が見つかりません。")
        print("csv/ ディレクトリに demand_data.csv を配置してください。")
        return None, None
    
    if not supply_file.exists():
        print("警告: supply_data.csv が見つかりません。")
        print("需給バランス分析はスキップされます。")
        print(f"使用するCSVファイル: {demand_file}")
        return demand_file, None
    
    print(f"需要データ: {demand_file}")
    print(f"供給データ: {supply_file}")
    return demand_file, supply_file

def create_output_directory():
    """出力ディレクトリを作成"""
    output_dir = Path('png')
    output_dir.mkdir(exist_ok=True)
    print(f"出力ディレクトリ: {output_dir.absolute()}")
    return output_dir

def run_visualization(script_name, demand_file, supply_file=None):
    """可視化スクリプトを実行"""
    print(f"\n{'='*60}")
    print(f"実行中: {script_name}")
    print(f"{'='*60}")
    
    try:
        # 需給バランス分析の場合は2つのファイルを引数に渡す
        if script_name == 'visualize_supply_demand.py' and supply_file:
            cmd_args = [sys.executable, script_name, str(demand_file), str(supply_file)]
        else:
            cmd_args = [sys.executable, script_name, str(demand_file)]
        
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            check=True
        )
        
        # 標準出力を表示
        if result.stdout:
            print(result.stdout)
        
        # 警告メッセージは無視（フォント関連の警告が出る場合がある）
        if result.stderr and "UserWarning" not in result.stderr:
            print("警告:", result.stderr)
        
        print(f"✓ {script_name} の実行が完了しました")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ エラー: {script_name} の実行に失敗しました")
        print(f"エラーメッセージ: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"✗ エラー: {script_name} が見つかりません")
        return False

def main():
    """メイン処理"""
    print("="*60)
    print("プロジェクトポートフォリオ分析 - ケイパビリティ可視化")
    print("="*60)
    
    # CSVファイルの検出
    demand_file, supply_file = find_csv_files()
    if demand_file is None:
        sys.exit(1)
    
    # 出力ディレクトリの作成
    output_dir = create_output_directory()
    
    # スクリプトのリスト
    scripts = [
        'visualize_capability.py',
        'visualize_by_tech.py'
    ]
    
    # 供給データがある場合は需給バランス分析も実行
    if supply_file:
        scripts.append('visualize_supply_demand.py')
    
    # 各スクリプトを実行
    success_count = 0
    for script in scripts:
        if run_visualization(script, demand_file, supply_file):
            success_count += 1
    
    # 結果サマリー
    print("\n" + "="*60)
    print("実行結果サマリー")
    print("="*60)
    print(f"成功: {success_count}/{len(scripts)} スクリプト")
    
    if success_count == len(scripts):
        print("\n✓ すべてのグラフ生成が完了しました！")
        print(f"\n出力ファイル:")
        
        # 生成されたファイルをリスト表示
        png_files = sorted(output_dir.glob('*.png'))
        for png_file in png_files:
            file_size = png_file.stat().st_size / 1024  # KB単位
            print(f"  - {png_file.name} ({file_size:.1f} KB)")
        
        print(f"\n場所: {output_dir.absolute()}")
    else:
        print("\n✗ 一部のスクリプト実行に失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main()
