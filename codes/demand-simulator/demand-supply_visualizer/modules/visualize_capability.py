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
    # 引数がない場合は csv/ ディレクトリ内の最初の.csvファイルを使用
    csv_dir = Path('csv')
    csv_files = list(csv_dir.glob('*.csv'))
    if not csv_files:
        print("エラー: CSVファイルが見つかりません")
        sys.exit(1)
    csv_file_path = str(csv_files[0])

print(f"読み込むCSVファイル: {csv_file_path}")

# CSVファイルを読み込み（BOM対応）
df = pd.read_csv(csv_file_path, encoding='utf-8-sig')

# 活動開始月と終了月を日付型に変換
df['活動開始月'] = pd.to_datetime(df['活動開始月'])
df['活動終了月'] = pd.to_datetime(df['活動終了月'])

# 月次のリソース需要を計算する関数
def calculate_monthly_demand(row):
    start_date = row['活動開始月']
    end_date = row['活動終了月']
    months = row['活動期間月数']
    
    # 各ケイパビリティの月平均需要を計算
    business = row['ビジネスケイパビリティ'] / months if months > 0 else 0
    delivery = row['デリバリケイパビリティ'] / months if months > 0 else 0
    technical = row['テクニカルケイパビリティ'] / months if months > 0 else 0
    leadership = row['リーダーシップケイパビリティ'] / months if months > 0 else 0
    
    # 月のリストを生成
    month_list = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    return month_list, business, delivery, technical, leadership

# 全体の月次データを集計
monthly_data = {}

for idx, row in df.iterrows():
    months, business, delivery, technical, leadership = calculate_monthly_demand(row)
    
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

ax1.set_title('Resource Demand by Capability - Stacked Area Chart', fontsize=16, fontweight='bold', pad=20)
ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
ax1.set_ylabel('Resource Demand (Person-Months)', fontsize=12, fontweight='bold')
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

ax2.set_title('Resource Demand by Capability - Line Chart', fontsize=16, fontweight='bold', pad=20)
ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
ax2.set_ylabel('Resource Demand (Person-Months)', fontsize=12, fontweight='bold')
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

plt.savefig('png/capability_demand_charts.png', dpi=300, bbox_inches='tight')
print("グラフを作成しました: png/capability_demand_charts.png")

# 統計情報を出力
print("\n=== 各ケイパビリティの統計情報 ===")
print("\n最大値:")
for capability in ['Business', 'Delivery', 'Technical', 'Leadership']:
    max_val = monthly_df[capability].max()
    max_date = monthly_df[capability].idxmax()
    print(f"  {capability}: {max_val:.2f} 人月 (発生月: {max_date.strftime('%Y年%m月')})")

print("\n平均値:")
for capability in ['Business', 'Delivery', 'Technical', 'Leadership']:
    avg_val = monthly_df[capability].mean()
    print(f"  {capability}: {avg_val:.2f} 人月")

print("\n全体リソース需要:")
monthly_df['Total'] = monthly_df.sum(axis=1)
print(f"  最大: {monthly_df['Total'].max():.2f} 人月 (発生月: {monthly_df['Total'].idxmax().strftime('%Y年%m月')})")
print(f"  平均: {monthly_df['Total'].mean():.2f} 人月")
