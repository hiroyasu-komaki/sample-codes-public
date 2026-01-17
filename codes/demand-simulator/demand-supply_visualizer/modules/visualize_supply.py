import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import sys
from pathlib import Path

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Noto Sans CJK JP', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# コマンドライン引数からCSVファイルパスを取得
if len(sys.argv) > 1:
    csv_file_path = sys.argv[1]
else:
    # 引数がない場合は csv/ ディレクトリ内の supply_data.csv を使用
    csv_dir = Path('csv')
    csv_file_path = str(csv_dir / 'supply_data.csv')
    if not Path(csv_file_path).exists():
        print("エラー: supply_data.csv が見つかりません")
        sys.exit(1)

print(f"読み込むCSVファイル: {csv_file_path}")

# CSVファイルを読み込み（BOM対応）
try:
    df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
    print(f"✓ CSVファイルの読み込み成功")
    print(f"検出されたカラム: {df.columns.tolist()}")
    print(f"データ行数: {len(df)}行")
except Exception as e:
    print(f"✗ CSVファイルの読み込みエラー: {e}")
    sys.exit(1)

# カラム名の確認と補正
required_columns = ['稼働開始月', '稼働終了月']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"\n警告: 以下のカラムが見つかりません: {missing_columns}")
    print("実際のカラム名を確認してください:")
    for i, col in enumerate(df.columns):
        print(f"  [{i}] '{col}' (長さ: {len(col)}文字)")
    sys.exit(1)

# 稼働開始月と終了月を日付型に変換
print("\n日付カラムを変換中...")
df['稼働開始月'] = pd.to_datetime(df['稼働開始月'])
df['稼働終了月'] = pd.to_datetime(df['稼働終了月'])
print("✓ 日付変換完了")

# 稼働終了月がNaNの場合は現在から2年後に設定
max_date = pd.Timestamp('2030-12-01')
df['稼働終了月'] = df['稼働終了月'].fillna(max_date)

# ケイパビリティのNaN値を0で埋める
capability_columns = ['ビジネスケイパビリティ', 'デリバリケイパビリティ', 
                     'テクニカルケイパビリティ', 'リーダーシップケイパビリティ']
for col in capability_columns:
    if col in df.columns:
        if df[col].isna().any():
            nan_count = df[col].isna().sum()
            print(f"警告: {col}に{nan_count}件の空白があります。0で補完します。")
            df[col] = df[col].fillna(0)
    else:
        print(f"警告: {col}カラムが見つかりません。0で初期化します。")
        df[col] = 0

# 稼働期間FTEカラムの存在チェック
if '稼働期間FTE' not in df.columns:
    print("警告: '稼働期間FTE'カラムが見つかりません。")
    # 稼働期間月数から自動計算を試みる
    if '稼働期間月数' in df.columns:
        print("  → '稼働期間月数'から稼働期間FTEを計算します（月数/12）")
        df['稼働期間FTE'] = df['稼働期間月数'] / 12
    else:
        print("  → デフォルト値1.0（フルタイム）を使用します。")
        df['稼働期間FTE'] = 1.0
else:
    # 稼働期間FTEのNaN値を1.0で埋める
    if df['稼働期間FTE'].isna().any():
        nan_count = df['稼働期間FTE'].isna().sum()
        print(f"警告: 稼働期間FTEに{nan_count}件の空白があります。1.0（フルタイム）で補完します。")
        df['稼働期間FTE'] = df['稼働期間FTE'].fillna(1.0)

# ★★★ ケイパビリティ合計がゼロの行を検出して除外 ★★★
df['ケイパビリティ合計'] = (
    df['ビジネスケイパビリティ'] + 
    df['デリバリケイパビリティ'] + 
    df['テクニカルケイパビリティ'] + 
    df['リーダーシップケイパビリティ']
)

zero_capability_mask = df['ケイパビリティ合計'] == 0
if zero_capability_mask.any():
    zero_count = zero_capability_mask.sum()
    print(f"\n警告: {zero_count}件の社員がすべてのケイパビリティが0です。")
    print("これらの社員は供給計算から除外されます。")
    if '社員ID' in df.columns:
        print(f"対象社員ID: {df[zero_capability_mask]['社員ID'].tolist()}")
    df = df[~zero_capability_mask].copy()
    print(f"残り社員数: {len(df)}人\n")

# ★★★ 2ステップ正規化: ケイパビリティを正規化してからFTEを乗算 ★★★
print("\n" + "="*60)
print("2ステップ正規化処理（正規化 → FTE乗算）")
print("="*60)

# 正規化（各ケイパビリティを合計で割る → 合計=1.0）
df['Business_normalized'] = df['ビジネスケイパビリティ'] / df['ケイパビリティ合計']
df['Delivery_normalized'] = df['デリバリケイパビリティ'] / df['ケイパビリティ合計']
df['Technical_normalized'] = df['テクニカルケイパビリティ'] / df['ケイパビリティ合計']
df['Leadership_normalized'] = df['リーダーシップケイパビリティ'] / df['ケイパビリティ合計']

# 実効供給能力 = 正規化後ケイパビリティ × 稼働期間FTE
df['Business_effective'] = df['Business_normalized'] * df['稼働期間FTE']
df['Delivery_effective'] = df['Delivery_normalized'] * df['稼働期間FTE']
df['Technical_effective'] = df['Technical_normalized'] * df['稼働期間FTE']
df['Leadership_effective'] = df['Leadership_normalized'] * df['稼働期間FTE']

print(f"稼働期間FTEの範囲: 最小={df['稼働期間FTE'].min():.2f}, "
      f"最大={df['稼働期間FTE'].max():.2f}, "
      f"平均={df['稼働期間FTE'].mean():.2f}")
print("="*60 + "\n")

# 月次のリソース供給を計算する関数（FTE考慮版）
def calculate_monthly_supply(row):
    start_date = row['稼働開始月']
    end_date = row['稼働終了月']
    
    # FTEを考慮した実効供給能力を使用
    business = row['Business_effective']
    delivery = row['Delivery_effective']
    technical = row['Technical_effective']
    leadership = row['Leadership_effective']
    
    # 月のリストを生成
    month_list = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    return month_list, business, delivery, technical, leadership

# 全体の月次データを集計
monthly_data = {}

for idx, row in df.iterrows():
    months, business, delivery, technical, leadership = calculate_monthly_supply(row)
    
    for month in months:
        if month not in monthly_data:
            monthly_data[month] = {
                'Business': 0,
                'Delivery': 0,
                'Technical': 0,
                'Leadership': 0
            }
        
        monthly_data[month]['Business'] += business
        monthly_data[month]['Delivery'] += delivery
        monthly_data[month]['Technical'] += technical
        monthly_data[month]['Leadership'] += leadership

# DataFrameに変換
monthly_df = pd.DataFrame.from_dict(monthly_data, orient='index').sort_index()

# 図のサイズを設定
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

# ========== 1. 積み上げ面グラフ ==========
colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']

ax1.fill_between(monthly_df.index, 0, monthly_df['Business'], 
                 label='Business Capability', alpha=0.8, color=colors[0])
ax1.fill_between(monthly_df.index, monthly_df['Business'], 
                 monthly_df['Business'] + monthly_df['Delivery'],
                 label='Delivery Capability', alpha=0.8, color=colors[1])
ax1.fill_between(monthly_df.index, 
                 monthly_df['Business'] + monthly_df['Delivery'],
                 monthly_df['Business'] + monthly_df['Delivery'] + monthly_df['Technical'],
                 label='Technical Capability', alpha=0.8, color=colors[2])
ax1.fill_between(monthly_df.index, 
                 monthly_df['Business'] + monthly_df['Delivery'] + monthly_df['Technical'],
                 monthly_df['Business'] + monthly_df['Delivery'] + monthly_df['Technical'] + monthly_df['Leadership'],
                 label='Leadership Capability', alpha=0.8, color=colors[3])

ax1.set_title('Resource Supply by Capability - Stacked Area Chart (FTE-Adjusted)', 
             fontsize=16, fontweight='bold', pad=20)
ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
ax1.set_ylabel('Resource Supply (Person-Months)', fontsize=12, fontweight='bold')
ax1.legend(loc='upper left', fontsize=11, framealpha=0.9)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# y軸の最大値を設定（全体の合計の最大値）
total_max = (monthly_df['Business'] + monthly_df['Delivery'] + 
             monthly_df['Technical'] + monthly_df['Leadership']).max()
ax1.set_ylim(0, total_max * 1.1)

# ========== 2. 折れ線グラフ ==========
ax2.plot(monthly_df.index, monthly_df['Business'], 
         label='Business Capability', linewidth=2.5, marker='o', markersize=4, color=colors[0])
ax2.plot(monthly_df.index, monthly_df['Delivery'], 
         label='Delivery Capability', linewidth=2.5, marker='s', markersize=4, color=colors[1])
ax2.plot(monthly_df.index, monthly_df['Technical'], 
         label='Technical Capability', linewidth=2.5, marker='^', markersize=4, color=colors[2])
ax2.plot(monthly_df.index, monthly_df['Leadership'], 
         label='Leadership Capability', linewidth=2.5, marker='d', markersize=4, color=colors[3])

ax2.set_title('Resource Supply by Capability - Line Chart (FTE-Adjusted)', 
             fontsize=16, fontweight='bold', pad=20)
ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
ax2.set_ylabel('Resource Supply (Person-Months)', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', fontsize=11, framealpha=0.9)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 各ケイパビリティの最大値を示すためのアノテーション
max_values = monthly_df.max()
for i, (capability, color) in enumerate(zip(['Business', 'Delivery', 'Technical', 'Leadership'], colors)):
    max_val = max_values[capability]
    max_idx = monthly_df[capability].idxmax()
    ax2.annotate(f'Max: {max_val:.2f}', 
                xy=(max_idx, max_val), 
                xytext=(10, 10 + i*15),
                textcoords='offset points',
                fontsize=9,
                color=color,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color, alpha=0.8))

plt.tight_layout()

# pngサブフォルダを作成
import os
os.makedirs('png', exist_ok=True)

plt.savefig('png/capability_supply_charts.png', dpi=300, bbox_inches='tight')
print("供給グラフを作成しました: png/capability_supply_charts.png")

# 統計情報を出力
print("\n=== 各ケイパビリティの統計情報（供給・FTE考慮版） ===")
print("\n最大値:")
for capability in ['Business', 'Delivery', 'Technical', 'Leadership']:
    max_val = monthly_df[capability].max()
    max_date = monthly_df[capability].idxmax()
    print(f"  {capability}: {max_val:.2f} 人月 (発生月: {max_date.strftime('%Y年%m月')})")

print("\n平均値:")
for capability in ['Business', 'Delivery', 'Technical', 'Leadership']:
    avg_val = monthly_df[capability].mean()
    print(f"  {capability}: {avg_val:.2f} 人月")

print("\n全体リソース供給:")
monthly_df['Total'] = monthly_df.sum(axis=1)
print(f"  最大: {monthly_df['Total'].max():.2f} 人月 (発生月: {monthly_df['Total'].idxmax().strftime('%Y年%m月')})")
print(f"  平均: {monthly_df['Total'].mean():.2f} 人月")

# 供給側の実際の人数（FTE）を表示
print(f"\n=== 供給側の人数（FTE考慮） ===")
print(f"総社員数: {len(df)}人")
print(f"総FTE: {df['稼働期間FTE'].sum():.2f}")
print(f"平均FTE: {df['稼働期間FTE'].mean():.2f}")
