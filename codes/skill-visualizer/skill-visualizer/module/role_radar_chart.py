import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
import os

def create_role_radar_chart(df, output_path):
    """
    ロール別スキルレーダーチャートを作成
    """
    # 日本語フォント設定
    plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Noto Sans CJK JP', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # カテゴリー別の平均スキルレベルを計算
    category_avg = df.groupby(['ロール', 'カテゴリー'])['スキルレベル_数値'].mean().reset_index()
    
    # ユニークなロールとカテゴリーを取得
    roles = category_avg['ロール'].unique()
    categories = ['ビジネス変革', 'デザイン', 'データ活用', 'テクノロジー', 'セキュリティ', 'パーソナルスキル']
    
    # カテゴリーが存在することを確認
    available_categories = [cat for cat in categories if cat in category_avg['カテゴリー'].unique()]
    
    # 角度の計算
    angles = np.linspace(0, 2 * np.pi, len(available_categories), endpoint=False).tolist()
    angles += angles[:1]  # 閉じた形にする
    
    # 図の作成（3行4列で11ロール + 1空白）
    fig, axes = plt.subplots(3, 4, figsize=(24, 18), subplot_kw=dict(projection='polar'))
    axes = axes.flatten()
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2', '#F06292', '#AED581', '#FFD54F']
    
    for idx, role in enumerate(roles):
        if idx >= len(axes):
            break
            
        ax = axes[idx]
        
        # このロールのデータを取得
        role_data = category_avg[category_avg['ロール'] == role]
        
        # 各カテゴリーの値を取得（存在しない場合は0）
        values = []
        for cat in available_categories:
            cat_data = role_data[role_data['カテゴリー'] == cat]
            if len(cat_data) > 0:
                values.append(cat_data['スキルレベル_数値'].values[0])
            else:
                values.append(0)
        
        values += values[:1]  # 閉じた形にする
        
        # プロット
        ax.plot(angles, values, 'o-', linewidth=2, color=colors[idx % len(colors)], label=role)
        ax.fill(angles, values, alpha=0.25, color=colors[idx % len(colors)])
        
        # カテゴリー名を設定（英語に変換して表示）
        category_labels = []
        for cat in available_categories:
            if cat == 'ビジネス変革':
                category_labels.append('Business\nTransformation')
            elif cat == 'デザイン':
                category_labels.append('Design')
            elif cat == 'データ活用':
                category_labels.append('Data\nUtilization')
            elif cat == 'テクノロジー':
                category_labels.append('Technology')
            elif cat == 'セキュリティ':
                category_labels.append('Security')
            elif cat == 'パーソナルスキル':
                category_labels.append('Personal\nSkills')
            else:
                category_labels.append(cat)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(category_labels, size=9)
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1', '2', '3', '4', '5'], size=8)
        ax.grid(True)
        
        # タイトル設定（ロール名を英語化）
        role_en = role.replace('/', '_')
        ax.set_title(f'{role}', size=12, weight='bold', pad=20)
    
    # 使用していない軸を非表示
    for idx in range(len(roles), len(axes)):
        axes[idx].set_visible(False)
    
    plt.suptitle('Skill Radar Chart by Role\n(Average Skill Level by Category)', 
                 fontsize=16, weight='bold', y=0.98)
    plt.tight_layout()
    
    # 保存
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"ロール別スキルレーダーチャートを保存しました: {output_path}")
