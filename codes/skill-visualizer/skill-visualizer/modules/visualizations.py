"""
スキルアセスメント可視化モジュール
必要な可視化機能のみを統合
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
plt.rcParams['axes.unicode_minus'] = False


def create_heatmap(data_loader, output_dir='output'):
    """
    可視化1: ロール×スキルカテゴリー別の平均スキルレベルをヒートマップで可視化
    
    Args:
        data_loader: SkillDataLoaderインスタンス
        output_dir: 出力ディレクトリ
    """
    # データ取得
    pivot_data = data_loader.get_category_avg_by_role()
    
    # 図の作成
    plt.figure(figsize=(12, 10))
    
    # ヒートマップの作成
    sns.heatmap(
        pivot_data,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        cbar_kws={'label': 'スキルレベル'},
        vmin=1,
        vmax=5,
        linewidths=0.5
    )
    
    plt.title('ロール×スキルカテゴリー別 平均スキルレベル', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('スキルカテゴリー', fontsize=12, fontweight='bold')
    plt.ylabel('ロール', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # 保存
    output_path = os.path.join(output_dir, '01_heatmap_role_category.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ ヒートマップを保存しました: {output_path}")
    plt.close()
    
    return output_path


def create_radar_chart(data_loader, output_dir='output'):
    """
    可視化2: 専門性別のスキルプロファイルをレーダーチャートで可視化
    
    Args:
        data_loader: SkillDataLoaderインスタンス
        output_dir: 出力ディレクトリ
    """
    # データ取得
    specialty_data = data_loader.get_category_avg_by_specialty()
    
    # カテゴリーと専門性のリスト
    categories = specialty_data.columns.tolist()
    specialties = specialty_data.index.tolist()
    
    # レーダーチャートのセットアップ
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # 円を閉じる
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # 色の設定
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
    
    # 各専門性のデータをプロット
    for idx, specialty in enumerate(specialties):
        values = specialty_data.loc[specialty].tolist()
        values += values[:1]  # 円を閉じる
        
        ax.plot(angles, values, 'o-', linewidth=2, label=specialty, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])
    
    # 軸の設定
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # タイトルと凡例
    plt.title('専門性別スキルプロファイル比較', fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    
    plt.tight_layout()
    
    # 保存
    output_path = os.path.join(output_dir, '02_radar_chart_specialty.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ レーダーチャートを保存しました: {output_path}")
    plt.close()
    
    return output_path


def create_scatter_matrix(data_loader, output_dir='output'):
    """
    可視化4: 2軸スキルレベルの散布図でロールをプロット（6つの組み合わせを1画像に）
    
    Args:
        data_loader: SkillDataLoaderインスタンス
        output_dir: 出力ディレクトリ
    """
    # 4つのカテゴリーから2つを選ぶ組み合わせ（6通り）
    import itertools
    categories = ['ビジネス変革', 'テクノロジー', 'デザイン', 'データ活用']
    combinations = list(itertools.combinations(categories, 2))
    
    # 専門性ごとに色分け
    specialty_colors = {
        'ビジネスアーキテクト': '#E74C3C',
        'データサイエンティスト': '#3498DB',
        'ソフトウェアエンジニア': '#2ECC71',
        'デザイナー': '#F39C12'
    }
    
    # 2行3列のサブプロットを作成
    fig, axes = plt.subplots(2, 3, figsize=(20, 14))
    axes = axes.flatten()
    
    # 各組み合わせについて散布図を作成
    for idx, (cat_x, cat_y) in enumerate(combinations):
        ax = axes[idx]
        
        # データ取得
        scatter_data = data_loader.get_two_axis_data(cat_x, cat_y)
        
        # 専門性ごとにプロット
        for specialty in scatter_data['専門性'].unique():
            data_subset = scatter_data[scatter_data['専門性'] == specialty]
            ax.scatter(
                data_subset[cat_x],
                data_subset[cat_y],
                c=specialty_colors[specialty],
                s=100,
                alpha=0.6,
                edgecolors='black',
                linewidth=1,
                label=specialty if idx == 0 else ''  # 凡例は最初のグラフのみ
            )
            
            # ロール名をラベルとして追加（フォントサイズ小さめ）
            for _, row in data_subset.iterrows():
                ax.annotate(
                    row['ロール'],
                    (row[cat_x], row[cat_y]),
                    fontsize=6,
                    ha='center',
                    va='bottom',
                    xytext=(0, 3),
                    textcoords='offset points'
                )
        
        # 対角線を追加（バランス型人材の目安）
        ax.plot([1, 5], [1, 5], 'k--', alpha=0.3, linewidth=0.8)
        
        # グリッドと象限の追加
        ax.axhline(y=3, color='gray', linestyle=':', alpha=0.5, linewidth=0.8)
        ax.axvline(x=3, color='gray', linestyle=':', alpha=0.5, linewidth=0.8)
        
        # 象限のラベル（フォントサイズ小さめ）
        ax.text(4.5, 4.5, '理想型', ha='center', va='center', 
                fontsize=8, color='green', fontweight='bold', alpha=0.5)
        ax.text(1.5, 4.5, f'{cat_y}\n特化', ha='center', va='center', 
                fontsize=7, color='gray', alpha=0.5)
        ax.text(4.5, 1.5, f'{cat_x}\n特化', ha='center', va='center', 
                fontsize=7, color='gray', alpha=0.5)
        ax.text(1.5, 1.5, '育成必要', ha='center', va='center', 
                fontsize=8, color='red', fontweight='bold', alpha=0.5)
        
        # 軸の設定
        ax.set_xlabel(f'{cat_x}', fontsize=10, fontweight='bold')
        ax.set_ylabel(f'{cat_y}', fontsize=10, fontweight='bold')
        ax.set_title(f'{cat_x} vs {cat_y}', fontsize=11, fontweight='bold', pad=10)
        
        ax.set_xlim(0.5, 5.5)
        ax.set_ylim(0.5, 5.5)
        ax.grid(True, alpha=0.3)
        
        # 凡例は最初のグラフのみ表示
        if idx == 0:
            ax.legend(loc='upper left', fontsize=8, framealpha=0.9)
    
    # 全体のタイトル
    fig.suptitle('スキルギャップマトリックス：4カテゴリーの組み合わせ分析', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    
    # 保存
    output_path = os.path.join(output_dir, '04_scatter_skill_gap_matrix.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ スキルギャップマトリックス（6つの組み合わせ）を保存しました: {output_path}")
    plt.close()
    
    return output_path
