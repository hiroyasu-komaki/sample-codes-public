import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_skill_level_heatmap(df, output_path):
    """
    スキルレベル分布のヒートマップを作成
    """
    # 日本語フォント設定
    plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Noto Sans CJK JP', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # スキル項目×ロール別のスキルレベルを取得
    pivot_table = df.pivot_table(
        index='ロール',  # 縦軸をロールに変更
        columns='スキル項目',  # 横軸をスキル項目に変更
        values='スキルレベル_数値',
        aggfunc='first'  # 各スキル項目は1つのロールに対して1つの値を持つ
    )
    
    # スキルレベルの平均でソート（列方向）
    avg_values = pivot_table.mean(axis=0)
    sorted_columns = avg_values.sort_values(ascending=False).index
    pivot_table = pivot_table[sorted_columns]
    
    # 図の作成（横長に変更）
    fig, ax = plt.subplots(figsize=(28, 10))
    
    # カスタムカラーマップの作成
    # 1.0(d) = 赤, 2.0(c) = オレンジ, 2.5(z) = 黄色（濃いめ）, 3.0(b) = 黄緑, 5.0(a) = 緑
    colors = ['#d73027', '#fc8d59', '#fee090', '#d9ef8b', '#91cf60', '#1a9850']
    n_bins = 100
    cmap = sns.blend_palette(colors, n_colors=n_bins, as_cmap=True)
    
    # ヒートマップの作成
    sns.heatmap(pivot_table, 
                annot=False,  # 数値は非表示（多すぎるため）
                cmap=cmap, 
                vmin=1.0, 
                vmax=5.0,
                cbar_kws={'label': 'Skill Level (a=5.0, b=3.0, c=2.0, d=1.0, z=2.5)'},
                linewidths=0.5,  # 線を太くする
                linecolor='gray',  # 線の色を濃く
                ax=ax)
    
    ax.set_title('Skill Level Distribution Heatmap\n(Role × Skill Item)', 
                 fontsize=14, weight='bold', pad=20)
    ax.set_xlabel('Skill Item', fontsize=12, weight='bold')
    ax.set_ylabel('Role', fontsize=10, weight='bold')
    
    # ラベルの調整
    plt.xticks(rotation=90, ha='right', fontsize=7)
    plt.yticks(fontsize=10)
    
    plt.tight_layout()
    
    # 保存
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"スキルレベル分布のヒートマップを保存しました: {output_path}")
    
    # 統計情報を出力
    print("\n=== スキルレベル分布統計 ===")
    print(f"総ロール数: {len(pivot_table)}")
    print(f"総スキル項目数: {len(pivot_table.columns)}")
    
    # スキルレベル別のカウント
    all_values = pivot_table.values.flatten()
    all_values = all_values[~np.isnan(all_values)]
    
    level_counts = {
        'Level a (5.0)': np.sum(all_values == 5.0),
        'Level b (3.0)': np.sum(all_values == 3.0),
        'Level c (2.0)': np.sum(all_values == 2.0),
        'Level d (1.0)': np.sum(all_values == 1.0),
        'Level z (2.5)': np.sum(all_values == 2.5),
    }
    
    print("\nスキルレベル別の分布:")
    for level, count in level_counts.items():
        percentage = (count / len(all_values)) * 100
        print(f"  {level}: {count} 件 ({percentage:.1f}%)")
