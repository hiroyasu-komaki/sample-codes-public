import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_subcategory_analysis(df, output_path):
    """
    サブカテゴリー別の詳細分析を作成
    """
    # 日本語フォント設定
    plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Noto Sans CJK JP', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # サブカテゴリー別の平均スキルレベルを計算
    subcat_avg = df.groupby(['カテゴリー', 'サブカテゴリー', 'ロール'])['スキルレベル_数値'].mean().reset_index()
    
    # ユニークなサブカテゴリーを取得
    subcategories = df['サブカテゴリー'].unique()
    n_subcat = len(subcategories)
    
    # 図の作成（動的に行数を決定）
    n_cols = 2
    n_rows = (n_subcat + 1) // 2
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 6*n_rows))
    axes = axes.flatten() if n_subcat > 1 else [axes]
    
    # カテゴリーごとに色を定義
    category_colors = {
        'ビジネス変革': '#e74c3c',
        'デザイン': '#3498db',
        'データ活用': '#2ecc71',
        'テクノロジー': '#f39c12',
        'セキュリティ': '#9b59b6',
        'パーソナルスキル': '#95a5a6'
    }
    
    # 各サブカテゴリーごとにグラフを作成
    for idx, subcat in enumerate(sorted(subcategories)):
        if idx >= len(axes):
            break
            
        ax = axes[idx]
        
        # このサブカテゴリーのデータを取得
        subcat_data = subcat_avg[subcat_avg['サブカテゴリー'] == subcat]
        
        if len(subcat_data) == 0:
            ax.set_visible(False)
            continue
        
        # カテゴリーを取得（色決定用）
        category = subcat_data['カテゴリー'].iloc[0]
        color = category_colors.get(category, '#34495e')
        
        # ロール別の平均を計算してソート
        role_avg = subcat_data.groupby('ロール')['スキルレベル_数値'].mean().sort_values(ascending=True)
        
        # 横棒グラフ
        bars = ax.barh(role_avg.index, role_avg.values, color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
        
        # 基準線（2.5）を追加
        ax.axvline(x=2.5, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        
        # タイトルとラベル
        ax.set_title(f'{subcat}\n({category})', fontsize=11, weight='bold', pad=10)
        ax.set_xlabel('Average Skill Level', fontsize=9)
        ax.set_ylabel('Role', fontsize=9)
        ax.set_xlim(0, 5.5)
        ax.grid(axis='x', alpha=0.3)
        
        # 値をラベル表示
        for i, (role, val) in enumerate(role_avg.items()):
            ax.text(val + 0.1, i, f'{val:.2f}', va='center', fontsize=8)
    
    # 使用していない軸を非表示
    for idx in range(len(subcategories), len(axes)):
        axes[idx].set_visible(False)
    
    # 全体タイトル
    fig.suptitle('Detailed Analysis by Sub-Category\n(Average Skill Level by Role for Each Sub-Category)', 
                 fontsize=16, weight='bold', y=0.995)
    
    plt.tight_layout()
    
    # 保存
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"サブカテゴリー別の詳細分析を保存しました: {output_path}")
    
    # 統計情報を出力
    print("\n=== サブカテゴリー別統計 ===")
    subcat_overall = df.groupby(['カテゴリー', 'サブカテゴリー'])['スキルレベル_数値'].agg(['mean', 'std', 'count']).round(2)
    subcat_overall = subcat_overall.sort_values('mean', ascending=False)
    print(subcat_overall.to_string())
    
    print("\n=== サブカテゴリー別トップ5 ===")
    print(subcat_overall.head(5).to_string())
    
    print("\n=== サブカテゴリー別ボトム5 ===")
    print(subcat_overall.tail(5).to_string())
