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
if len(sys.argv) > 2:
    demand_csv_path = sys.argv[1]
    supply_csv_path = sys.argv[2]
else:
    # 引数がない場合は csv/ ディレクトリ内のファイルを使用
    csv_dir = Path('csv')
    demand_csv_path = str(csv_dir / 'demand_data.csv')
    supply_csv_path = str(csv_dir / 'supply_data.csv')

print(f"需要データ: {demand_csv_path}")
print(f"供給データ: {supply_csv_path}")

# ========== 需要データの読み込みと集計 ==========
demand_df = pd.read_csv(demand_csv_path)
demand_df['活動開始月'] = pd.to_datetime(demand_df['活動開始月'])
demand_df['活動終了月'] = pd.to_datetime(demand_df['活動終了月'])

def calculate_monthly_demand(row):
    """月次需要を計算"""
    start_date = row['活動開始月']
    end_date = row['活動終了月']
    months = row['活動期間月数']
    
    business = row['ビジネスケイパビリティ'] / months if months > 0 else 0
    delivery = row['デリバリケイパビリティ'] / months if months > 0 else 0
    technical = row['テクニカルケイパビリティ'] / months if months > 0 else 0
    leadership = row['リーダーシップケイパビリティ'] / months if months > 0 else 0
    
    month_list = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    return month_list, business, delivery, technical, leadership

# 需要の月次データを集計
monthly_demand = {}

for idx, row in demand_df.iterrows():
    months, business, delivery, technical, leadership = calculate_monthly_demand(row)
    
    for month in months:
        if month not in monthly_demand:
            monthly_demand[month] = {
                'Business': 0,
                'Delivery': 0,
                'Technical': 0,
                'Leadership': 0
            }
        
        monthly_demand[month]['Business'] += business
        monthly_demand[month]['Delivery'] += delivery
        monthly_demand[month]['Technical'] += technical
        monthly_demand[month]['Leadership'] += leadership

# ========== 供給データの読み込みと集計（FTE正規化版） ==========
supply_df = pd.read_csv(supply_csv_path)
supply_df['稼働開始月'] = pd.to_datetime(supply_df['稼働開始月'])
supply_df['稼働終了月'] = pd.to_datetime(supply_df['稼働終了月'])

# 稼働終了月がNaNの場合は現在から2年後に設定
max_date = pd.Timestamp('2030-12-01')
supply_df['稼働終了月'] = supply_df['稼働終了月'].fillna(max_date)

# ★★★ FTE正規化: 各社員のケイパビリティ合計を1.0にする ★★★
print("\n" + "="*60)
print("FTE正規化処理")
print("="*60)

supply_df['ケイパビリティ合計'] = (
    supply_df['ビジネスケイパビリティ'] + 
    supply_df['デリバリケイパビリティ'] + 
    supply_df['テクニカルケイパビリティ'] + 
    supply_df['リーダーシップケイパビリティ']
)

print(f"正規化前のケイパビリティ合計: 最小={supply_df['ケイパビリティ合計'].min():.2f}, "
      f"最大={supply_df['ケイパビリティ合計'].max():.2f}, "
      f"平均={supply_df['ケイパビリティ合計'].mean():.2f}")

# 正規化（各社員のケイパビリティを合計で割る）
supply_df['Business_normalized'] = supply_df['ビジネスケイパビリティ'] / supply_df['ケイパビリティ合計']
supply_df['Delivery_normalized'] = supply_df['デリバリケイパビリティ'] / supply_df['ケイパビリティ合計']
supply_df['Technical_normalized'] = supply_df['テクニカルケイパビリティ'] / supply_df['ケイパビリティ合計']
supply_df['Leadership_normalized'] = supply_df['リーダーシップケイパビリティ'] / supply_df['ケイパビリティ合計']

# 正規化後の合計を確認
supply_df['正規化後合計'] = (
    supply_df['Business_normalized'] + 
    supply_df['Delivery_normalized'] + 
    supply_df['Technical_normalized'] + 
    supply_df['Leadership_normalized']
)

print(f"正規化後のケイパビリティ合計: 最小={supply_df['正規化後合計'].min():.2f}, "
      f"最大={supply_df['正規化後合計'].max():.2f}, "
      f"平均={supply_df['正規化後合計'].mean():.2f}")
print("="*60 + "\n")

def calculate_monthly_supply(row):
    """月次供給を計算（FTE正規化版）"""
    start_date = row['稼働開始月']
    end_date = row['稼働終了月']
    
    # 正規化されたケイパビリティを使用（合計=1.0 FTE）
    business = row['Business_normalized']
    delivery = row['Delivery_normalized']
    technical = row['Technical_normalized']
    leadership = row['Leadership_normalized']
    
    month_list = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    return month_list, business, delivery, technical, leadership

# 供給の月次データを集計
monthly_supply = {}

for idx, row in supply_df.iterrows():
    months, business, delivery, technical, leadership = calculate_monthly_supply(row)
    
    for month in months:
        if month not in monthly_supply:
            monthly_supply[month] = {
                'Business': 0,
                'Delivery': 0,
                'Technical': 0,
                'Leadership': 0
            }
        
        monthly_supply[month]['Business'] += business
        monthly_supply[month]['Delivery'] += delivery
        monthly_supply[month]['Technical'] += technical
        monthly_supply[month]['Leadership'] += leadership

# ========== データフレーム化 ==========
demand_df_monthly = pd.DataFrame.from_dict(monthly_demand, orient='index').sort_index()
supply_df_monthly = pd.DataFrame.from_dict(monthly_supply, orient='index').sort_index()

# ★★★ 需要データの期間に基づいて表示範囲を制限 ★★★
demand_start = demand_df_monthly.index.min()
demand_end = demand_df_monthly.index.max()

print(f"表示期間: {demand_start.strftime('%Y年%m月')} 〜 {demand_end.strftime('%Y年%m月')}")

# 需要データの期間内の月のみを使用
all_months = pd.date_range(start=demand_start, end=demand_end, freq='MS')
capabilities = ['Business', 'Delivery', 'Technical', 'Leadership']

# データフレームを再作成
demand_complete = pd.DataFrame(index=all_months, columns=capabilities).fillna(0)
supply_complete = pd.DataFrame(index=all_months, columns=capabilities).fillna(0)

for month in all_months:
    if month in demand_df_monthly.index:
        demand_complete.loc[month] = demand_df_monthly.loc[month]
    if month in supply_df_monthly.index:
        supply_complete.loc[month] = supply_df_monthly.loc[month]

# 需給バランス（供給 - 需要）を計算
balance = supply_complete - demand_complete

# ========== グラフ作成 ==========
fig, axes = plt.subplots(2, 2, figsize=(18, 14))
fig.suptitle('Supply-Demand Balance by Capability (FTE-Normalized)', fontsize=18, fontweight='bold', y=0.995)

colors_demand = '#E94B3C'  # 赤（需要）
colors_supply = '#4A90E2'  # 青（供給）
colors_balance = '#50C878'  # 緑（バランス）

for idx, capability in enumerate(capabilities):
    ax = axes[idx // 2, idx % 2]
    
    # 需要、供給、バランスのプロット
    ax.plot(demand_complete.index, demand_complete[capability], 
           label='Demand', linewidth=2.5, marker='o', markersize=4, 
           color=colors_demand, alpha=0.8)
    ax.plot(supply_complete.index, supply_complete[capability], 
           label='Supply (FTE-Normalized)', linewidth=2.5, marker='s', markersize=4, 
           color=colors_supply, alpha=0.8)
    
    # バランスを面グラフで表示（供給不足は赤、供給過剰は青）
    positive_balance = balance[capability].clip(lower=0)
    negative_balance = balance[capability].clip(upper=0)
    
    ax.fill_between(balance.index, 0, positive_balance, 
                    color=colors_supply, alpha=0.2, label='Supply Surplus')
    ax.fill_between(balance.index, 0, negative_balance, 
                    color=colors_demand, alpha=0.2, label='Supply Shortage')
    
    # ゼロライン
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    ax.set_title(f'{capability} Capability', fontsize=14, fontweight='bold', pad=10)
    ax.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax.set_ylabel('Resource (Person-Months)', fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 統計情報を表示
    max_shortage = negative_balance.min()
    max_surplus = positive_balance.max()
    
    if max_shortage < 0:
        max_shortage_date = negative_balance.idxmin()
        shortage_text = f'Max Shortage: {abs(max_shortage):.2f} ({max_shortage_date.strftime("%Y-%m")})'
    else:
        shortage_text = 'Max Shortage: None'
    
    if max_surplus > 0:
        max_surplus_date = positive_balance.idxmax()
        surplus_text = f'Max Surplus: {max_surplus:.2f} ({max_surplus_date.strftime("%Y-%m")})'
    else:
        surplus_text = 'Max Surplus: None'
    
    # テキストボックスに統計情報を表示
    textstr = f'{shortage_text}\n{surplus_text}'
    ax.text(0.02, 0.98, textstr,
            transform=ax.transAxes, fontsize=8, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

plt.tight_layout()

# pngサブフォルダを作成
import os
os.makedirs('png', exist_ok=True)

plt.savefig('png/supply_demand_balance.png', dpi=300, bbox_inches='tight')
print("需給バランスグラフを作成しました: png/supply_demand_balance.png")

# ========== 統計情報の出力 ==========
print("\n=== 需給バランス統計情報（FTE正規化版） ===")
for capability in capabilities:
    print(f"\n【{capability} Capability】")
    
    avg_demand = demand_complete[capability].mean()
    avg_supply = supply_complete[capability].mean()
    avg_balance = balance[capability].mean()
    
    max_shortage = balance[capability].min()
    max_surplus = balance[capability].max()
    
    shortage_months = (balance[capability] < 0).sum()
    surplus_months = (balance[capability] > 0).sum()
    balanced_months = (balance[capability] == 0).sum()
    
    print(f"  平均需要: {avg_demand:.2f} 人月")
    print(f"  平均供給: {avg_supply:.2f} 人月 (FTE正規化済み)")
    print(f"  平均バランス: {avg_balance:.2f} 人月")
    print(f"  最大不足: {max_shortage:.2f} 人月" + 
          (f" ({balance[capability].idxmin().strftime('%Y年%m月')})" if max_shortage < 0 else ""))
    print(f"  最大余剰: {max_surplus:.2f} 人月" + 
          (f" ({balance[capability].idxmax().strftime('%Y年%m月')})" if max_surplus > 0 else ""))
    print(f"  不足月数: {shortage_months} ヶ月")
    print(f"  余剰月数: {surplus_months} ヶ月")
    print(f"  均衡月数: {balanced_months} ヶ月")

print("\n=== 全体サマリー ===")
total_avg_demand = demand_complete.sum(axis=1).mean()
total_avg_supply = supply_complete.sum(axis=1).mean()
total_avg_balance = balance.sum(axis=1).mean()

print(f"全ケイパビリティ合計:")
print(f"  平均総需要: {total_avg_demand:.2f} 人月")
print(f"  平均総供給: {total_avg_supply:.2f} 人月 (FTE正規化済み)")
print(f"  平均総バランス: {total_avg_balance:.2f} 人月")

# 供給側の実際の人数（FTE）を表示
print(f"\n=== 供給側の人数（FTE換算） ===")
target_month = pd.Timestamp('2025-06-01')
active_at_target = supply_df[
    (supply_df['稼働開始月'] <= target_month) & 
    (supply_df['稼働終了月'] >= target_month)
]
print(f"2025年6月の稼働社員数: {len(active_at_target)}人 (各1.0 FTE)")
print(f"  総供給能力: {len(active_at_target):.2f} FTE")
