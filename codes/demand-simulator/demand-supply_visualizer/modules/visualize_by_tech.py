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

# 技術領域の種類
tech_domains = df['技術領域'].unique()
print(f"技術領域: {tech_domains}")

# 技術領域ごとの色設定
tech_colors = {
    '従来型': '#4A90E2',      # 青
    'AI/ML': '#E94B3C',       # 赤
    'DX/デジタル': '#50C878',  # 緑
    'クラウド': '#F5A623'      # オレンジ
}

# 月次のリソース需要を計算する関数（技術領域別）
def calculate_monthly_demand_by_tech(row):
    start_date = row['活動開始月']
    end_date = row['活動終了月']
    months = row['活動期間月数']
    tech_domain = row['技術領域']
    
    # 各ケイパビリティの月平均需要を計算
    business = row['ビジネスケイパビリティ'] / months if months > 0 else 0
    delivery = row['デリバリケイパビリティ'] / months if months > 0 else 0
    technical = row['テクニカルケイパビリティ'] / months if months > 0 else 0
    leadership = row['リーダーシップケイパビリティ'] / months if months > 0 else 0
    
    # 月のリストを生成
    month_list = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    return month_list, tech_domain, business, delivery, technical, leadership

# 技術領域別の月次データを集計
monthly_data_by_tech = {}

for idx, row in df.iterrows():
    months, tech_domain, business, delivery, technical, leadership = calculate_monthly_demand_by_tech(row)
    
    for month in months:
        if month not in monthly_data_by_tech:
            monthly_data_by_tech[month] = {}
        
        if tech_domain not in monthly_data_by_tech[month]:
            monthly_data_by_tech[month][tech_domain] = {
                'Business': 0,
                'Delivery': 0,
                'Technical': 0,
                'Leadership': 0
            }
        
        monthly_data_by_tech[month][tech_domain]['Business'] += business
        monthly_data_by_tech[month][tech_domain]['Delivery'] += delivery
        monthly_data_by_tech[month][tech_domain]['Technical'] += technical
        monthly_data_by_tech[month][tech_domain]['Leadership'] += leadership

# 各ケイパビリティごとにDataFrameを作成
capabilities = ['Business', 'Delivery', 'Technical', 'Leadership']
dfs_by_capability = {}

for capability in capabilities:
    data_dict = {}
    for month in sorted(monthly_data_by_tech.keys()):
        data_dict[month] = {}
        for tech_domain in tech_domains:
            if tech_domain in monthly_data_by_tech[month]:
                data_dict[month][tech_domain] = monthly_data_by_tech[month][tech_domain][capability]
            else:
                data_dict[month][tech_domain] = 0
    
    dfs_by_capability[capability] = pd.DataFrame.from_dict(data_dict, orient='index').sort_index()
    # 欠損値を0で埋める
    dfs_by_capability[capability] = dfs_by_capability[capability].fillna(0)

# ========== 2段構成のグラフを作成 ==========
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

# ========== グラフ1: 技術領域別積み上げ面グラフ ==========
# 各技術領域のデータを準備（全ケイパビリティの合計）
tech_total_data = {}
for tech in tech_domains:
    tech_total_data[tech] = sum([dfs_by_capability[cap][tech] for cap in capabilities])

# 技術領域別積み上げ面グラフを描画
tech_list = list(tech_domains)
bottom_values = None

for i, tech in enumerate(tech_list):
    if i == 0:
        ax1.fill_between(dfs_by_capability['Business'].index, 
                        0, 
                        tech_total_data[tech],
                        label=tech, 
                        alpha=0.8, 
                        color=tech_colors[tech])
        bottom_values = tech_total_data[tech].values
    else:
        ax1.fill_between(dfs_by_capability['Business'].index, 
                        bottom_values, 
                        bottom_values + tech_total_data[tech].values,
                        label=tech, 
                        alpha=0.8, 
                        color=tech_colors[tech])
        bottom_values = bottom_values + tech_total_data[tech].values

ax1.set_title('Resource Demand by Technology Domain - Stacked Area Chart', 
             fontsize=16, fontweight='bold', pad=20)
ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
ax1.set_ylabel('Resource Demand (Person-Months)', fontsize=12, fontweight='bold')
ax1.legend(loc='upper left', fontsize=11, framealpha=0.9)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# y軸の最大値を設定
total_max = sum([tech_total_data[tech] for tech in tech_domains]).max()
ax1.set_ylim(0, total_max * 1.1)

# ========== グラフ2: 技術領域別折れ線グラフ ==========
# マーカースタイル
markers = ['o', 's', '^', 'd']

for i, tech in enumerate(tech_domains):
    ax2.plot(dfs_by_capability['Business'].index, 
            tech_total_data[tech], 
            label=tech, 
            linewidth=2.5, 
            marker=markers[i], 
            markersize=4, 
            color=tech_colors[tech],
            alpha=0.9)

ax2.set_title('Resource Demand by Technology Domain - Line Chart', 
             fontsize=16, fontweight='bold', pad=20)
ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
ax2.set_ylabel('Resource Demand (Person-Months)', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', fontsize=11, framealpha=0.9)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 各技術領域の最大値を示すアノテーション
for i, tech in enumerate(tech_domains):
    max_val = tech_total_data[tech].max()
    if max_val > 0:
        max_idx = tech_total_data[tech].idxmax()
        ax2.annotate(f'Max: {max_val:.2f}', 
                    xy=(max_idx, max_val), 
                    xytext=(10, 10 + i*15),
                    textcoords='offset points',
                    fontsize=9,
                    color=tech_colors[tech],
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                             edgecolor=tech_colors[tech], alpha=0.8))

plt.tight_layout()

# pngサブフォルダを作成
import os
os.makedirs('png', exist_ok=True)

plt.savefig('png/capability_by_tech_charts.png', dpi=300, bbox_inches='tight')
print("技術領域別グラフを作成しました: png/capability_by_tech_charts.png")

# 統計情報を出力
print("\n=== 技術領域別の統計情報 ===")
for tech in tech_domains:
    max_val = tech_total_data[tech].max()
    if max_val > 0:
        max_date = tech_total_data[tech].idxmax()
        avg_val = tech_total_data[tech].mean()
        print(f"\n【{tech}】")
        print(f"  最大: {max_val:.2f} 人月 ({max_date.strftime('%Y年%m月')})")
        print(f"  平均: {avg_val:.2f} 人月")

print("\n全体リソース需要:")
total_demand = sum([tech_total_data[tech] for tech in tech_domains])
print(f"  最大: {total_demand.max():.2f} 人月 (発生月: {total_demand.idxmax().strftime('%Y年%m月')})")
print(f"  平均: {total_demand.mean():.2f} 人月")
