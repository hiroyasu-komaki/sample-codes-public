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

# CSVファイルを読み込み
df = pd.read_csv(csv_file_path)

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

# ========== グラフ1: 4つのケイパビリティを技術領域別に積み上げ面グラフで表示 ==========
fig1, axes1 = plt.subplots(2, 2, figsize=(18, 14))
fig1.suptitle('Resource Demand by Capability and Technology Domain - Stacked Area Charts', 
              fontsize=18, fontweight='bold', y=0.995)

for idx, capability in enumerate(capabilities):
    ax = axes1[idx // 2, idx % 2]
    df_cap = dfs_by_capability[capability]
    
    # 積み上げ面グラフを描画
    ax.stackplot(df_cap.index, 
                 *[df_cap[tech].values for tech in tech_domains],
                 labels=tech_domains,
                 colors=[tech_colors[tech] for tech in tech_domains],
                 alpha=0.8)
    
    ax.set_title(f'{capability} Capability', fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax.set_ylabel('Resource Demand (Person-Months)', fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 最大値を取得して表示
    total_max = df_cap.sum(axis=1).max()
    total_max_date = df_cap.sum(axis=1).idxmax()
    ax.text(0.02, 0.98, f'Peak: {total_max:.2f} ({total_max_date.strftime("%Y-%m")})',
            transform=ax.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()

# pngサブフォルダを作成
import os
os.makedirs('png', exist_ok=True)

plt.savefig('png/capability_by_tech_stacked.png', dpi=300, bbox_inches='tight')
print("積み上げ面グラフを作成しました: png/capability_by_tech_stacked.png")

# ========== グラフ2: 4つのケイパビリティを技術領域別に折れ線グラフで表示 ==========
fig2, axes2 = plt.subplots(2, 2, figsize=(18, 14))
fig2.suptitle('Resource Demand by Capability and Technology Domain - Line Charts', 
              fontsize=18, fontweight='bold', y=0.995)

# マーカースタイル
markers = ['o', 's', '^', 'd']

for idx, capability in enumerate(capabilities):
    ax = axes2[idx // 2, idx % 2]
    df_cap = dfs_by_capability[capability]
    
    # 各技術領域の折れ線グラフを描画
    for i, tech in enumerate(tech_domains):
        ax.plot(df_cap.index, df_cap[tech], 
               label=tech, 
               linewidth=2.5, 
               marker=markers[i], 
               markersize=4, 
               color=tech_colors[tech],
               alpha=0.9)
    
    ax.set_title(f'{capability} Capability', fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax.set_ylabel('Resource Demand (Person-Months)', fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 各技術領域の最大値を表示
    for i, tech in enumerate(tech_domains):
        max_val = df_cap[tech].max()
        if max_val > 0:
            max_idx = df_cap[tech].idxmax()
            # アノテーションの位置を調整
            ax.annotate(f'{max_val:.2f}', 
                       xy=(max_idx, max_val), 
                       xytext=(8, 8 + i*12),
                       textcoords='offset points',
                       fontsize=8,
                       color=tech_colors[tech],
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                edgecolor=tech_colors[tech], alpha=0.8))

plt.tight_layout()
plt.savefig('png/capability_by_tech_lines.png', dpi=300, bbox_inches='tight')
print("折れ線グラフを作成しました: png/capability_by_tech_lines.png")

# 統計情報を出力
print("\n=== 技術領域別の統計情報 ===")
for capability in capabilities:
    print(f"\n【{capability} Capability】")
    df_cap = dfs_by_capability[capability]
    for tech in tech_domains:
        max_val = df_cap[tech].max()
        if max_val > 0:
            max_date = df_cap[tech].idxmax()
            avg_val = df_cap[tech].mean()
            print(f"  {tech}:")
            print(f"    最大: {max_val:.2f} 人月 ({max_date.strftime('%Y年%m月')})")
            print(f"    平均: {avg_val:.2f} 人月")
