import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_capability_portfolio(df, output_path):
    """
    ケイパビリティ別の人材ポートフォリオを作成
    """
    # 日本語フォント設定
    plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Noto Sans CJK JP', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # ケイパビリティ別の集計
    capability_stats = df.groupby('capability').agg({
        'ロール': 'count',  # データ件数
        'スキルレベル_数値': ['mean', 'std', 'min', 'max']
    }).round(2)
    
    capability_stats.columns = ['データ件数', '平均スキルレベル', '標準偏差', '最小値', '最大値']
    capability_stats = capability_stats.sort_values('平均スキルレベル', ascending=False)
    
    # ケイパビリティ別のロール数を計算
    role_count = df.groupby('capability')['ロール'].nunique().to_dict()
    capability_stats['ロール数'] = capability_stats.index.map(role_count)
    
    # 図の作成（2x2のサブプロット）
    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # 1. ケイパビリティ別の平均スキルレベル（棒グラフ）
    ax1 = fig.add_subplot(gs[0, 0])
    
    # ケイパビリティ名を英語化
    capability_names = {
        'ビジネスケイパビリティ': 'Business',
        'デリバリケイパビリティ': 'Delivery',
        'リーダーシップケイパビリティ': 'Leadership',
        'テクニカルケイパビリティ': 'Technical'
    }
    
    capability_stats_display = capability_stats.copy()
    capability_stats_display.index = [capability_names.get(idx, idx) for idx in capability_stats_display.index]
    
    colors = ['#2ecc71' if x > 2.5 else '#e74c3c' if x < 2.0 else '#f39c12' 
              for x in capability_stats_display['平均スキルレベル']]
    bars = ax1.barh(capability_stats_display.index, capability_stats_display['平均スキルレベル'], 
                    color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax1.axvline(x=2.5, color='gray', linestyle='--', linewidth=2, alpha=0.7, label='Target: 2.5')
    ax1.axvline(x=3.0, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Goal: 3.0')
    ax1.set_xlabel('Average Skill Level', fontsize=13, weight='bold')
    ax1.set_ylabel('Capability', fontsize=13, weight='bold')
    ax1.set_title('Average Skill Level by Capability\n(Organizational Capability Assessment)', 
                  fontsize=15, weight='bold', pad=15)
    ax1.grid(axis='x', alpha=0.3)
    ax1.legend(fontsize=11)
    ax1.set_xlim(0, 5.5)
    
    # 値をラベル表示
    for i, (idx, row) in enumerate(capability_stats_display.iterrows()):
        ax1.text(row['平均スキルレベル'] + 0.1, i, f"{row['平均スキルレベル']:.2f}", 
                va='center', fontsize=12, weight='bold')
    
    # 2. ケイパビリティ別のスキル分散（箱ひげ図）
    ax2 = fig.add_subplot(gs[0, 1])
    capability_order = capability_stats.index.tolist()
    
    # 箱ひげ図用のデータ準備
    box_data = [df[df['capability'] == cap]['スキルレベル_数値'].values for cap in capability_order]
    box_labels = [capability_names.get(cap, cap) for cap in capability_order]
    
    bp = ax2.boxplot(box_data, labels=box_labels, vert=False, patch_artist=True,
                     boxprops=dict(facecolor='lightblue', alpha=0.7, linewidth=1.5),
                     medianprops=dict(color='red', linewidth=3),
                     whiskerprops=dict(linewidth=2),
                     capprops=dict(linewidth=2),
                     flierprops=dict(marker='o', markerfacecolor='red', markersize=6, alpha=0.5))
    
    ax2.axvline(x=2.5, color='gray', linestyle='--', linewidth=2, alpha=0.7)
    ax2.set_xlabel('Skill Level', fontsize=13, weight='bold')
    ax2.set_ylabel('Capability', fontsize=13, weight='bold')
    ax2.set_title('Skill Level Distribution by Capability\n(Box Plot with Outliers)', 
                  fontsize=15, weight='bold', pad=15)
    ax2.grid(axis='x', alpha=0.3)
    ax2.set_xlim(0, 5.5)
    
    # 統計値を表示
    for i, cap in enumerate(capability_order):
        cap_data = df[df['capability'] == cap]['スキルレベル_数値']
        q1 = cap_data.quantile(0.25)
        q3 = cap_data.quantile(0.75)
        median = cap_data.median()
        ax2.text(5.3, i, f'Med:{median:.1f}\nIQR:{q3-q1:.1f}', 
                va='center', fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 3. ケイパビリティ別のロール数とスキル項目数
    ax3 = fig.add_subplot(gs[1, 0])
    
    # スキル項目数を計算
    skill_count = df.groupby('capability')['スキル項目'].nunique().to_dict()
    capability_stats_display['スキル項目数'] = [skill_count.get(orig_cap, 0) 
                                                for orig_cap in capability_stats.index]
    
    x = np.arange(len(capability_stats_display))
    width = 0.25
    
    bars1 = ax3.bar(x - width, capability_stats_display['ロール数'], width, 
                    label='Number of Roles', color='#3498db', alpha=0.8, edgecolor='black', linewidth=1)
    bars2 = ax3.bar(x, capability_stats_display['スキル項目数'], width,
                    label='Number of Skill Items', color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1)
    bars3 = ax3.bar(x + width, capability_stats_display['データ件数'] / 42, width,
                    label='Data Points (÷42)', color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1)
    
    ax3.set_xlabel('Capability', fontsize=13, weight='bold')
    ax3.set_ylabel('Count', fontsize=13, weight='bold')
    ax3.set_title('Capability Composition\n(Roles, Skills, and Data Points)', 
                  fontsize=15, weight='bold', pad=15)
    ax3.set_xticks(x)
    ax3.set_xticklabels(capability_stats_display.index, rotation=0, ha='center', fontsize=11)
    ax3.legend(fontsize=10, loc='upper left')
    ax3.grid(axis='y', alpha=0.3)
    
    # 値をラベル表示
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9, weight='bold')
    
    # 4. スキルレベル分布のヒートマップ（ケイパビリティ×スキルレベル）
    ax4 = fig.add_subplot(gs[1, 1])
    
    # スキルレベル別の件数を集計
    level_dist = df.groupby(['capability', 'スキルレベル']).size().unstack(fill_value=0)
    level_order = ['d', 'c', 'z', 'b', 'a']
    level_dist = level_dist.reindex(columns=level_order, fill_value=0)
    level_dist = level_dist.loc[capability_order]
    
    # パーセンテージに変換
    level_dist_pct = level_dist.div(level_dist.sum(axis=1), axis=0) * 100
    
    # 表示用にインデックスを英語化
    level_dist_pct_display = level_dist_pct.copy()
    level_dist_pct_display.index = [capability_names.get(idx, idx) for idx in level_dist_pct_display.index]
    
    # カスタムカラーマップ（緑=良い、赤=悪い）
    sns.heatmap(level_dist_pct_display, annot=True, fmt='.1f', cmap='RdYlGn', 
                cbar_kws={'label': 'Percentage (%)'},
                linewidths=1, linecolor='white', ax=ax4,
                vmin=0, vmax=50)
    
    ax4.set_xlabel('Skill Level', fontsize=13, weight='bold')
    ax4.set_ylabel('Capability', fontsize=13, weight='bold')
    ax4.set_title('Skill Level Distribution by Capability (%)\n(Maturity Assessment)', 
                  fontsize=15, weight='bold', pad=15)
    ax4.set_xticklabels(['d(1.0)', 'c(2.0)', 'z(2.5)', 'b(3.0)', 'a(5.0)'], rotation=0, fontsize=11)
    ax4.set_yticklabels(ax4.get_yticklabels(), rotation=0, fontsize=11)
    
    # 全体タイトル
    fig.suptitle('Human Resource Portfolio by Capability\n(Strategic Capability Assessment)', 
                 fontsize=18, weight='bold', y=0.98)
    
    # 保存
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"ケイパビリティ別の人材ポートフォリオを保存しました: {output_path}")
    
    # 統計情報を出力
    print("\n=== ケイパビリティ別統計 ===")
    print(capability_stats.to_string())
    
    print("\n=== 成熟度評価（高レベルスキル比率） ===")
    for cap in capability_order:
        cap_name = capability_names.get(cap, cap)
        high_pct = level_dist_pct.loc[cap, ['a', 'b']].sum()
        mid_pct = level_dist_pct.loc[cap, 'z']
        low_pct = level_dist_pct.loc[cap, ['c', 'd']].sum()
        
        maturity = '高' if high_pct > 50 else '低' if low_pct > 50 else '中'
        print(f'{cap_name}:')
        print(f'  高レベル(a/b): {high_pct:.1f}%, 中レベル(z): {mid_pct:.1f}%, 低レベル(c/d): {low_pct:.1f}%')
        print(f'  成熟度: {maturity}')
