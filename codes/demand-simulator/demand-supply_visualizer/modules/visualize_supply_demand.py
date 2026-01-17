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
try:
    demand_df = pd.read_csv(demand_csv_path, encoding='utf-8-sig')
    print(f"✓ 需要データの読み込み成功")
    print(f"データ行数: {len(demand_df)}行")
except Exception as e:
    print(f"✗ 需要データの読み込みエラー: {e}")
    sys.exit(1)

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
try:
    supply_df = pd.read_csv(supply_csv_path, encoding='utf-8-sig')
    print(f"✓ 供給データの読み込み成功")
    print(f"供給データのカラム: {supply_df.columns.tolist()}")
    print(f"データ行数: {len(supply_df)}行")
except Exception as e:
    print(f"✗ 供給データの読み込みエラー: {e}")
    sys.exit(1)

# カラム名の確認
required_columns = ['稼働開始月', '稼働終了月']
missing_columns = [col for col in required_columns if col not in supply_df.columns]
if missing_columns:
    print(f"\n警告: 以下のカラムが見つかりません: {missing_columns}")
    print("実際のカラム名:")
    for i, col in enumerate(supply_df.columns):
        print(f"  [{i}] '{col}'")
    sys.exit(1)

supply_df['稼働開始月'] = pd.to_datetime(supply_df['稼働開始月'])
supply_df['稼働終了月'] = pd.to_datetime(supply_df['稼働終了月'])

# 稼働終了月がNaNの場合は現在から2年後に設定
max_date = pd.Timestamp('2030-12-01')
supply_df['稼働終了月'] = supply_df['稼働終了月'].fillna(max_date)

# ★★★ ケイパビリティのNaN値を0で埋める ★★★
capability_columns = ['ビジネスケイパビリティ', 'デリバリケイパビリティ', 
                     'テクニカルケイパビリティ', 'リーダーシップケイパビリティ']
for col in capability_columns:
    if supply_df[col].isna().any():
        nan_count = supply_df[col].isna().sum()
        print(f"警告: {col}に{nan_count}件の空白があります。0で補完します。")
        supply_df[col] = supply_df[col].fillna(0)

# 稼働期間FTEカラムの存在チェック
if '稼働期間FTE' not in supply_df.columns:
    print("警告: '稼働期間FTE'カラムが見つかりません。")
    # 稼働期間月数から自動計算を試みる
    if '稼働期間月数' in supply_df.columns:
        print("  → '稼働期間月数'から稼働期間FTEを計算します（月数/12）")
        supply_df['稼働期間FTE'] = supply_df['稼働期間月数'] / 12
    else:
        print("  → デフォルト値1.0（フルタイム）を使用します。")
        supply_df['稼働期間FTE'] = 1.0
else:
    # 稼働期間FTEのNaN値を1.0で埋める
    if supply_df['稼働期間FTE'].isna().any():
        nan_count = supply_df['稼働期間FTE'].isna().sum()
        print(f"警告: 稼働期間FTEに{nan_count}件の空白があります。1.0（フルタイム）で補完します。")
        supply_df['稼働期間FTE'] = supply_df['稼働期間FTE'].fillna(1.0)

# ★★★ 2ステップ正規化: ケイパビリティを正規化してからFTEを乗算 ★★★
print("\n" + "="*60)
print("2ステップ正規化処理（正規化 → FTE乗算）")
print("="*60)

# ステップ1: ケイパビリティ合計で正規化（スキル比率を算出）
supply_df['ケイパビリティ合計'] = (
    supply_df['ビジネスケイパビリティ'] + 
    supply_df['デリバリケイパビリティ'] + 
    supply_df['テクニカルケイパビリティ'] + 
    supply_df['リーダーシップケイパビリティ']
)

print(f"ステップ1: ケイパビリティ合計の範囲")
print(f"  最小={supply_df['ケイパビリティ合計'].min():.2f}, "
      f"最大={supply_df['ケイパビリティ合計'].max():.2f}, "
      f"平均={supply_df['ケイパビリティ合計'].mean():.2f}")

# ★★★ ケイパビリティ合計がゼロの行を検出して除外 ★★★
zero_capability_mask = supply_df['ケイパビリティ合計'] == 0
if zero_capability_mask.any():
    zero_count = zero_capability_mask.sum()
    print(f"\n警告: {zero_count}件の社員がすべてのケイパビリティが0です。")
    print("これらの社員は供給計算から除外されます。")
    if '社員ID' in supply_df.columns:
        print(f"対象社員ID: {supply_df[zero_capability_mask]['社員ID'].tolist()}")
    supply_df = supply_df[~zero_capability_mask].copy()
    print(f"残り社員数: {len(supply_df)}人\n")

# 正規化（各ケイパビリティを合計で割る → 合計=1.0）
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
print(f"  正規化後の合計: 最小={supply_df['正規化後合計'].min():.2f}, "
      f"最大={supply_df['正規化後合計'].max():.2f} (全員1.0になるはず)")

# ステップ2: 正規化後の値に稼働期間FTEを乗算（実効供給能力）
print(f"\nステップ2: 稼働期間FTEの範囲")
print(f"  最小={supply_df['稼働期間FTE'].min():.2f}, "
      f"最大={supply_df['稼働期間FTE'].max():.2f}, "
      f"平均={supply_df['稼働期間FTE'].mean():.2f}")

# 実効供給能力 = 正規化後ケイパビリティ × 稼働期間FTE
# （例：Business_normalized=0.625, FTE=0.5 → Business_effective=0.3125）
supply_df['Business_effective'] = supply_df['Business_normalized'] * supply_df['稼働期間FTE']
supply_df['Delivery_effective'] = supply_df['Delivery_normalized'] * supply_df['稼働期間FTE']
supply_df['Technical_effective'] = supply_df['Technical_normalized'] * supply_df['稼働期間FTE']
supply_df['Leadership_effective'] = supply_df['Leadership_normalized'] * supply_df['稼働期間FTE']

# 実効供給能力の合計を確認（= 稼働期間FTE）
supply_df['実効供給合計'] = (
    supply_df['Business_effective'] + 
    supply_df['Delivery_effective'] + 
    supply_df['Technical_effective'] + 
    supply_df['Leadership_effective']
)

print(f"  実効供給合計: 最小={supply_df['実効供給合計'].min():.2f}, "
      f"最大={supply_df['実効供給合計'].max():.2f}, "
      f"平均={supply_df['実効供給合計'].mean():.2f}")
print(f"  (実効供給合計 = 各社員の稼働期間FTE)")
print("="*60 + "\n")

def calculate_monthly_supply(row):
    """月次供給を計算（FTE考慮版）"""
    start_date = row['稼働開始月']
    end_date = row['稼働終了月']
    
    # FTEを考慮した実効供給能力を使用
    business = row['Business_effective']
    delivery = row['Delivery_effective']
    technical = row['Technical_effective']
    leadership = row['Leadership_effective']
    
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
fig.suptitle('Supply-Demand Balance by Capability (FTE-Adjusted)', fontsize=18, fontweight='bold', y=0.995)

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
           label='Supply (FTE-Adjusted)', linewidth=2.5, marker='s', markersize=4, 
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
print("需給バランスグラフ（4分割）を作成しました: png/supply_demand_balance.png")

# ========== 全体合計グラフを2段構成で作成 ==========
fig2, (ax_total1, ax_total2) = plt.subplots(2, 1, figsize=(16, 12))
fig2.suptitle('Total Supply-Demand Balance (All Capabilities Combined, FTE-Adjusted)', 
             fontsize=18, fontweight='bold', y=0.995)

# 全ケイパビリティの合計を計算
total_demand = demand_complete.sum(axis=1)
total_supply = supply_complete.sum(axis=1)
total_balance = balance.sum(axis=1)

# ========== 上段：合計の需給バランス ==========
# 需要、供給、バランスのプロット
ax_total1.plot(total_demand.index, total_demand, 
       label='Total Demand', linewidth=3, marker='o', markersize=5, 
       color=colors_demand, alpha=0.8)
ax_total1.plot(total_supply.index, total_supply, 
       label='Total Supply (FTE-Adjusted)', linewidth=3, marker='s', markersize=5, 
       color=colors_supply, alpha=0.8)

# バランスを面グラフで表示（供給不足は赤、供給過剰は青）
positive_balance_total = total_balance.clip(lower=0)
negative_balance_total = total_balance.clip(upper=0)

ax_total1.fill_between(total_balance.index, 0, positive_balance_total, 
                color=colors_supply, alpha=0.2, label='Supply Surplus')
ax_total1.fill_between(total_balance.index, 0, negative_balance_total, 
                color=colors_demand, alpha=0.2, label='Supply Shortage')

# ゼロライン
ax_total1.axhline(y=0, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)

ax_total1.set_title('Total Balance Overview', fontsize=16, fontweight='bold', pad=20)
ax_total1.set_xlabel('Month', fontsize=12, fontweight='bold')
ax_total1.set_ylabel('Total Resource (Person-Months)', fontsize=12, fontweight='bold')
ax_total1.legend(loc='upper left', fontsize=11, framealpha=0.9)
ax_total1.grid(True, alpha=0.3, linestyle='--')
ax_total1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax_total1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax_total1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 統計情報を表示
max_shortage_total = negative_balance_total.min()
max_surplus_total = positive_balance_total.max()

if max_shortage_total < 0:
    max_shortage_date_total = negative_balance_total.idxmin()
    shortage_text_total = f'Max Shortage: {abs(max_shortage_total):.2f} ({max_shortage_date_total.strftime("%Y-%m")})'
else:
    shortage_text_total = 'Max Shortage: None'

if max_surplus_total > 0:
    max_surplus_date_total = positive_balance_total.idxmax()
    surplus_text_total = f'Max Surplus: {max_surplus_total:.2f} ({max_surplus_date_total.strftime("%Y-%m")})'
else:
    surplus_text_total = 'Max Surplus: None'

# 平均値も追加
avg_demand_total = total_demand.mean()
avg_supply_total = total_supply.mean()
avg_balance_total = total_balance.mean()

# テキストボックスに統計情報を表示
textstr_total = (f'{shortage_text_total}\n{surplus_text_total}\n\n'
                f'Avg Demand: {avg_demand_total:.2f}\n'
                f'Avg Supply: {avg_supply_total:.2f}\n'
                f'Avg Balance: {avg_balance_total:.2f}')
ax_total1.text(0.02, 0.98, textstr_total,
        transform=ax_total1.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# ========== 下段：需要と供給の累計比較（時系列の積み上げ） ==========
# 需要と供給の累計を計算
total_demand_cumulative = total_demand.cumsum()
total_supply_cumulative = total_supply.cumsum()
total_balance_cumulative = total_balance.cumsum()

# 累計の需要と供給をプロット
ax_total2.plot(total_demand_cumulative.index, total_demand_cumulative, 
              label='Cumulative Demand', linewidth=3, linestyle='-', 
              color=colors_demand, alpha=0.8, marker='o', markersize=5)
ax_total2.plot(total_supply_cumulative.index, total_supply_cumulative, 
              label='Cumulative Supply (FTE-Adjusted)', linewidth=3, linestyle='-', 
              color=colors_supply, alpha=0.8, marker='s', markersize=5)

# 累計バランスを面グラフで表示
positive_balance_cumulative = total_balance_cumulative.clip(lower=0)
negative_balance_cumulative = total_balance_cumulative.clip(upper=0)

ax_total2.fill_between(total_balance_cumulative.index, 0, positive_balance_cumulative, 
                      color=colors_supply, alpha=0.2, label='Cumulative Surplus')
ax_total2.fill_between(total_balance_cumulative.index, 0, negative_balance_cumulative, 
                      color=colors_demand, alpha=0.2, label='Cumulative Shortage')

# ゼロライン
ax_total2.axhline(y=0, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)

ax_total2.set_title('Cumulative Balance (Time Series)', 
                   fontsize=16, fontweight='bold', pad=20)
ax_total2.set_xlabel('Month', fontsize=12, fontweight='bold')
ax_total2.set_ylabel('Cumulative Resource (Person-Months)', fontsize=12, fontweight='bold')
ax_total2.legend(loc='upper left', fontsize=11, framealpha=0.9)
ax_total2.grid(True, alpha=0.3, linestyle='--')
ax_total2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax_total2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax_total2.xaxis.get_majorticklabels(), rotation=45, ha='right')

# 累計の統計情報を表示
final_demand_cumulative = total_demand_cumulative.iloc[-1]
final_supply_cumulative = total_supply_cumulative.iloc[-1]
final_balance_cumulative = total_balance_cumulative.iloc[-1]

max_balance_cumulative = total_balance_cumulative.max()
min_balance_cumulative = total_balance_cumulative.min()

if max_balance_cumulative > 0:
    max_balance_date = total_balance_cumulative.idxmax()
    max_text = f'Max Cumulative Surplus: {max_balance_cumulative:.2f} ({max_balance_date.strftime("%Y-%m")})'
else:
    max_text = 'Max Cumulative Surplus: None'

if min_balance_cumulative < 0:
    min_balance_date = total_balance_cumulative.idxmin()
    min_text = f'Max Cumulative Shortage: {abs(min_balance_cumulative):.2f} ({min_balance_date.strftime("%Y-%m")})'
else:
    min_text = 'Max Cumulative Shortage: None'

# テキストボックスに累計統計情報を表示
textstr_cumulative = (f'Final Cumulative Values:\n'
                     f'  Demand: {final_demand_cumulative:.2f}\n'
                     f'  Supply: {final_supply_cumulative:.2f}\n'
                     f'  Balance: {final_balance_cumulative:+.2f}\n\n'
                     f'{max_text}\n{min_text}')
ax_total2.text(0.02, 0.98, textstr_cumulative,
              transform=ax_total2.transAxes, fontsize=10, verticalalignment='top',
              bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
plt.savefig('png/supply_demand_balance_total.png', dpi=300, bbox_inches='tight')
print("需給バランスグラフ（合計・2段構成）を作成しました: png/supply_demand_balance_total.png")

# ========== 統計情報の出力 ==========
print("\n=== 需給バランス統計情報（FTE考慮版） ===")
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
    print(f"  平均供給: {avg_supply:.2f} 人月 (FTE考慮済み)")
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
print(f"  平均総供給: {total_avg_supply:.2f} 人月 (FTE考慮済み)")
print(f"  平均総バランス: {total_avg_balance:.2f} 人月")

# 供給側の実際の人数（FTE）を表示
print(f"\n=== 供給側の人数（FTE考慮） ===")
target_month = pd.Timestamp('2025-06-01')
active_at_target = supply_df[
    (supply_df['稼働開始月'] <= target_month) & 
    (supply_df['稼働終了月'] >= target_month)
]
total_fte = active_at_target['稼働期間FTE'].sum()
print(f"2025年6月の稼働社員数: {len(active_at_target)}人")
print(f"  総FTE: {total_fte:.2f}")
print(f"  平均FTE: {total_fte/len(active_at_target):.2f}" if len(active_at_target) > 0 else "")
