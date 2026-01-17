import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_expertise_portfolio(df, output_path):
    """
    専門性別の人材ポートフォリオを作成
    """
    # 日本語フォント設定
    plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Noto Sans CJK JP', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 専門性別の集計
    expertise_stats = df.groupby('専門性').agg({
        'ロール': 'count',  # ロール数（データ件数）
        'スキルレベル_数値': ['mean', 'std']
    }).round(2)
    
    expertise_stats.columns = ['データ件数', '平均スキルレベル', '標準偏差']
    expertise_stats = expertise_stats.sort_values('平均スキルレベル', ascending=False)
    
    # 専門性別のロール数を計算
    role_count = df.groupby('専門性')['ロール'].nunique().to_dict()
    expertise_stats['ロール数'] = expertise_stats.index.map(role_count)
    
    # 図の作成（2x2のサブプロット）
    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # 1. 専門性別の平均スキルレベル（棒グラフ）
    ax1 = fig.add_subplot(gs[0, 0])
    colors = ['#2ecc71' if x > 2.5 else '#e74c3c' if x < 2.0 else '#f39c12' 
              for x in expertise_stats['平均スキルレベル']]
    bars = ax1.barh(expertise_stats.index, expertise_stats['平均スキルレベル'], color=colors, alpha=0.7)
    ax1.axvline(x=2.5, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Target: 2.5')
    ax1.set_xlabel('Average Skill Level', fontsize=12, weight='bold')
    ax1.set_ylabel('Expertise', fontsize=12, weight='bold')
    ax1.set_title('Average Skill Level by Expertise', fontsize=14, weight='bold', pad=15)
    ax1.grid(axis='x', alpha=0.3)
    ax1.legend()
    
    # 値をラベル表示
    for i, (idx, row) in enumerate(expertise_stats.iterrows()):
        ax1.text(row['平均スキルレベル'] + 0.05, i, f"{row['平均スキルレベル']:.2f}", 
                va='center', fontsize=10)
    
    # 2. 専門性別のスキル分散（箱ひげ図）
    ax2 = fig.add_subplot(gs[0, 1])
    expertise_order = expertise_stats.index.tolist()
    
    # 箱ひげ図用のデータ準備
    box_data = [df[df['専門性'] == exp]['スキルレベル_数値'].values for exp in expertise_order]
    
    bp = ax2.boxplot(box_data, labels=expertise_order, vert=False, patch_artist=True,
                     boxprops=dict(facecolor='lightblue', alpha=0.7),
                     medianprops=dict(color='red', linewidth=2),
                     whiskerprops=dict(linewidth=1.5),
                     capprops=dict(linewidth=1.5))
    
    ax2.set_xlabel('Skill Level', fontsize=12, weight='bold')
    ax2.set_ylabel('Expertise', fontsize=12, weight='bold')
    ax2.set_title('Skill Level Distribution by Expertise (Box Plot)', fontsize=14, weight='bold', pad=15)
    ax2.grid(axis='x', alpha=0.3)
    ax2.set_xlim(0, 5.5)
    
    # 3. 専門性別のロール数とデータ件数（積み上げ棒グラフ）
    ax3 = fig.add_subplot(gs[1, 0])
    x = np.arange(len(expertise_stats))
    width = 0.35
    
    bars1 = ax3.bar(x - width/2, expertise_stats['ロール数'], width, 
                    label='Number of Roles', color='#3498db', alpha=0.8)
    bars2 = ax3.bar(x + width/2, expertise_stats['データ件数'] / 42, width,
                    label='Data Points (÷42)', color='#e74c3c', alpha=0.8)
    
    ax3.set_xlabel('Expertise', fontsize=12, weight='bold')
    ax3.set_ylabel('Count', fontsize=12, weight='bold')
    ax3.set_title('Number of Roles and Data Points by Expertise', fontsize=14, weight='bold', pad=15)
    ax3.set_xticks(x)
    ax3.set_xticklabels(expertise_stats.index, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    
    # 値をラベル表示
    for bar in bars1:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    # 4. スキルレベル分布のヒートマップ（専門性×スキルレベル）
    ax4 = fig.add_subplot(gs[1, 1])
    
    # スキルレベル別の件数を集計
    level_dist = df.groupby(['専門性', 'スキルレベル']).size().unstack(fill_value=0)
    level_order = ['d', 'c', 'z', 'b', 'a']
    level_dist = level_dist.reindex(columns=level_order, fill_value=0)
    level_dist = level_dist.loc[expertise_order]
    
    # パーセンテージに変換
    level_dist_pct = level_dist.div(level_dist.sum(axis=1), axis=0) * 100
    
    sns.heatmap(level_dist_pct, annot=True, fmt='.1f', cmap='RdYlGn', 
                cbar_kws={'label': 'Percentage (%)'},
                linewidths=0.5, linecolor='white', ax=ax4)
    
    ax4.set_xlabel('Skill Level', fontsize=12, weight='bold')
    ax4.set_ylabel('Expertise', fontsize=12, weight='bold')
    ax4.set_title('Skill Level Distribution by Expertise (%)', fontsize=14, weight='bold', pad=15)
    ax4.set_xticklabels(['d(1.0)', 'c(2.0)', 'z(2.5)', 'b(3.0)', 'a(5.0)'], rotation=0)
    
    # 全体タイトル
    fig.suptitle('Human Resource Portfolio by Expertise\n(Expertise-based Analysis)', 
                 fontsize=16, weight='bold', y=0.98)
    
    # 保存
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"専門性別の人材ポートフォリオを保存しました: {output_path}")
    
    # 統計情報を出力
    print("\n=== 専門性別統計 ===")
    print(expertise_stats.to_string())
