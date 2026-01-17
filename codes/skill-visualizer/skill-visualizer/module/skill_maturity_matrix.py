import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_skill_maturity_matrix(df, output_path):
    """
    スキルレベル×スキル項目のマトリクス分析を作成
    組織の成熟度を測定
    """
    # 日本語フォント設定
    plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Noto Sans CJK JP', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 図の作成（2x2のサブプロット）
    fig = plt.figure(figsize=(22, 16))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # 1. スキルレベル別の項目数（全体）
    ax1 = fig.add_subplot(gs[0, 0])
    
    level_counts = df.groupby('スキルレベル').size()
    level_order = ['a', 'b', 'z', 'c', 'd']
    level_counts = level_counts.reindex(level_order)
    level_labels = [f'{l}\n({df[df["スキルレベル"]==l]["スキルレベル_数値"].iloc[0]})' 
                   for l in level_order]
    
    colors_map = {'a': '#1a9850', 'b': '#91cf60', 'z': '#fee090', 'c': '#fc8d59', 'd': '#d73027'}
    colors = [colors_map[l] for l in level_order]
    
    bars = ax1.bar(level_labels, level_counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Skill Level', fontsize=12, weight='bold')
    ax1.set_ylabel('Number of Items', fontsize=12, weight='bold')
    ax1.set_title('Distribution of Skill Items by Level\n(Overall Organization)', 
                  fontsize=14, weight='bold', pad=15)
    ax1.grid(axis='y', alpha=0.3)
    
    # パーセンテージと件数を表示
    total = level_counts.sum()
    for bar, count in zip(bars, level_counts):
        height = bar.get_height()
        pct = (count / total) * 100
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(count)}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=11, weight='bold')
    
    # 2. カテゴリー別のスキルレベル分布（積み上げ棒グラフ）
    ax2 = fig.add_subplot(gs[0, 1])
    
    category_level = df.groupby(['カテゴリー', 'スキルレベル']).size().unstack(fill_value=0)
    category_level = category_level.reindex(columns=level_order, fill_value=0)
    
    # パーセンテージに変換
    category_level_pct = category_level.div(category_level.sum(axis=1), axis=0) * 100
    
    category_level_pct.plot(kind='barh', stacked=True, ax=ax2, 
                            color=[colors_map[l] for l in level_order],
                            alpha=0.8, edgecolor='black', linewidth=0.5)
    
    ax2.set_xlabel('Percentage (%)', fontsize=12, weight='bold')
    ax2.set_ylabel('Category', fontsize=12, weight='bold')
    ax2.set_title('Skill Level Distribution by Category\n(Stacked Percentage)', 
                  fontsize=14, weight='bold', pad=15)
    ax2.legend(title='Skill Level', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(axis='x', alpha=0.3)
    ax2.set_xlim(0, 100)
    
    # 3. スキルレベル×カテゴリーのヒートマップ（件数）
    ax3 = fig.add_subplot(gs[1, 0])
    
    sns.heatmap(category_level, annot=True, fmt='d', cmap='YlOrRd', 
                cbar_kws={'label': 'Number of Items'},
                linewidths=0.5, linecolor='white', ax=ax3)
    
    ax3.set_xlabel('Skill Level', fontsize=12, weight='bold')
    ax3.set_ylabel('Category', fontsize=12, weight='bold')
    ax3.set_title('Skill Maturity Matrix\n(Category × Skill Level)', 
                  fontsize=14, weight='bold', pad=15)
    ax3.set_xticklabels(['a(5.0)', 'b(3.0)', 'z(2.5)', 'c(2.0)', 'd(1.0)'], rotation=0)
    
    # 4. 高レベルスキル(a/b)と低レベルスキル(c/d)の比率
    ax4 = fig.add_subplot(gs[1, 1])
    
    # カテゴリー別に高レベル・低レベルを集計
    high_level = category_level[['a', 'b']].sum(axis=1)
    mid_level = category_level[['z']]
    low_level = category_level[['c', 'd']].sum(axis=1)
    
    ratio_df = pd.DataFrame({
        'High (a/b)': high_level,
        'Mid (z)': mid_level.values.flatten(),
        'Low (c/d)': low_level
    })
    
    ratio_df_pct = ratio_df.div(ratio_df.sum(axis=1), axis=0) * 100
    
    x = np.arange(len(ratio_df))
    width = 0.6
    
    p1 = ax4.barh(x, ratio_df_pct['High (a/b)'], width, label='High (a/b)', 
                  color='#1a9850', alpha=0.8)
    p2 = ax4.barh(x, ratio_df_pct['Mid (z)'], width, left=ratio_df_pct['High (a/b)'],
                  label='Mid (z)', color='#fee090', alpha=0.8)
    p3 = ax4.barh(x, ratio_df_pct['Low (c/d)'], width, 
                  left=ratio_df_pct['High (a/b)'] + ratio_df_pct['Mid (z)'],
                  label='Low (c/d)', color='#d73027', alpha=0.8)
    
    ax4.set_yticks(x)
    ax4.set_yticklabels(ratio_df.index)
    ax4.set_xlabel('Percentage (%)', fontsize=12, weight='bold')
    ax4.set_ylabel('Category', fontsize=12, weight='bold')
    ax4.set_title('Skill Maturity Ratio by Category\n(High vs Mid vs Low)', 
                  fontsize=14, weight='bold', pad=15)
    ax4.legend(loc='lower right')
    ax4.set_xlim(0, 100)
    ax4.grid(axis='x', alpha=0.3)
    
    # 全体タイトル
    fig.suptitle('Skill Maturity Matrix Analysis\n(Organizational Skill Level Assessment)', 
                 fontsize=16, weight='bold', y=0.98)
    
    # 保存
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"スキルレベル×スキル項目のマトリクス分析を保存しました: {output_path}")
    
    # 統計情報を出力
    print("\n=== スキルレベル別統計 ===")
    print(f"高レベル(a/b): {level_counts[['a', 'b']].sum()}件 ({level_counts[['a', 'b']].sum()/total*100:.1f}%)")
    print(f"中レベル(z): {level_counts['z']}件 ({level_counts['z']/total*100:.1f}%)")
    print(f"低レベル(c/d): {level_counts[['c', 'd']].sum()}件 ({level_counts[['c', 'd']].sum()/total*100:.1f}%)")
    
    print("\n=== カテゴリー別成熟度 ===")
    for cat in ratio_df.index:
        high_pct = ratio_df_pct.loc[cat, 'High (a/b)']
        low_pct = ratio_df_pct.loc[cat, 'Low (c/d)']
        maturity = 'High' if high_pct > 50 else 'Low' if low_pct > 50 else 'Medium'
        print(f"{cat}: 高レベル{high_pct:.1f}% / 低レベル{low_pct:.1f}% → 成熟度: {maturity}")
