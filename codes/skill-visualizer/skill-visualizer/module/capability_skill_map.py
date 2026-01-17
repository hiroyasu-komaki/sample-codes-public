import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_capability_skill_map(df, output_path):
    """
    ケイパビリティ別スキルマップを作成（ヒートマップ形式）
    """
    # 日本語フォント設定
    plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Noto Sans CJK JP', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # ケイパビリティ×ロール別の平均スキルレベルを計算
    capability_avg = df.groupby(['capability', 'ロール'])['スキルレベル_数値'].mean().reset_index()
    
    # ピボットテーブルの作成
    pivot_table = capability_avg.pivot(index='capability', columns='ロール', values='スキルレベル_数値')
    
    # ケイパビリティ名を英語に変換
    capability_map = {
        'リーダーシップケイパビリティ': 'Leadership',
        'ビジネスケイパビリティ': 'Business',
        'テクニカルケイパビリティ': 'Technical',
        'デリバリケイパビリティ': 'Delivery'
    }
    pivot_table.index = [capability_map.get(idx, idx) for idx in pivot_table.index]
    
    # 図の作成
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # ヒートマップの作成
    sns.heatmap(pivot_table, 
                annot=True, 
                fmt='.2f', 
                cmap='RdYlGn', 
                center=2.5,
                vmin=1.0, 
                vmax=5.0,
                cbar_kws={'label': 'Average Skill Level'},
                linewidths=0.5,
                linecolor='white',
                ax=ax)
    
    ax.set_title('Skill Map by Capability\n(Average Skill Level by Capability × Role)', 
                 fontsize=14, weight='bold', pad=20)
    ax.set_xlabel('Role', fontsize=12, weight='bold')
    ax.set_ylabel('Capability', fontsize=12, weight='bold')
    
    # ラベルの回転調整
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    
    # 保存
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"ケイパビリティ別スキルマップを保存しました: {output_path}")
    
    # 統計情報も出力
    print("\n=== ケイパビリティ別統計 ===")
    for capability in pivot_table.index:
        avg = pivot_table.loc[capability].mean()
        print(f"{capability}: 平均スキルレベル = {avg:.2f}")
