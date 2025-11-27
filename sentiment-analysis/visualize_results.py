# visualize_results.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from pathlib import Path

# 日本語フォント設定
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def setup_japanese_font():
    """
    日本語フォントの設定を試みる
    """
    try:
        import matplotlib.font_manager as fm
        japanese_fonts = ['IPAexGothic', 'IPAGothic', 'Noto Sans CJK JP', 'Takao Gothic']
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        for font in japanese_fonts:
            if font in available_fonts:
                plt.rcParams['font.family'] = font
                print(f"日本語フォント設定: {font}")
                return
        
        print("警告: 日本語フォントが見つかりませんでした。デフォルトフォントを使用します。")
    except Exception as e:
        print(f"フォント設定エラー: {e}")

def load_and_merge_results(out_dir="out"):
    """
    outフォルダ内の全CSVファイルを読み込み、統合する
    
    Returns:
    - merged_df: 統合されたデータフレーム
    """
    csv_files = [f for f in os.listdir(out_dir) if f.endswith('.csv')]
    
    if not csv_files:
        raise ValueError(f"エラー: {out_dir} フォルダにCSVファイルが見つかりません")
    
    print(f"\n検出されたファイル: {len(csv_files)}個")
    
    # 各ファイルを読み込んでリストに格納
    all_data = []
    
    for csv_file in sorted(csv_files):
        csv_path = os.path.join(out_dir, csv_file)
        df = pd.read_csv(csv_path)
        
        # モデル名を取得（小文字で比較）
        filename_lower = csv_file.lower()
        if 'transformer1' in filename_lower:
            model_name = 'transformer1'
        elif 'transformer2' in filename_lower:
            model_name = 'transformer2'
        elif 'dictionary' in filename_lower:
            model_name = 'dictionary'
        else:
            print(f"  警告: {csv_file} のモデル名を特定できません。スキップします。")
            continue
        
        # 必要な列のみ抽出
        df_subset = df[['sentence_id', 'sentence', 'score']].copy()
        df_subset['model'] = model_name
        
        all_data.append(df_subset)
        print(f"  読み込み: {csv_file} ({len(df)}件, モデル: {model_name})")
    
    if not all_data:
        raise ValueError(f"エラー: 有効なCSVファイルが見つかりませんでした")
    
    # 全データを統合
    merged_df = pd.concat(all_data, ignore_index=True)
    
    print(f"\n統合完了: 総データ数 {len(merged_df)}件")
    
    return merged_df

def create_score_plot_with_heatmap(merged_df, output_path):
    """
    Sentence IDごとの3モデルスコアをドットプロットで表示
    左側にSentence IDを平均スコアでヒートマップ表示
    
    Parameters:
    - merged_df: 統合データフレーム
    - output_path: 出力ファイルパス
    """
    # Sentence IDごとにデータを整理（昇順）
    sentence_ids = sorted(merged_df['sentence_id'].unique())
    n_sentences = len(sentence_ids)
    
    # 各Sentence IDの平均スコアを計算
    avg_scores = merged_df.groupby('sentence_id')['score'].mean().to_dict()
    
    # 図のサイズを文章数に応じて調整
    fig_height = max(8, n_sentences * 0.3)
    fig_height = min(fig_height, 50)
    
    # 図の作成
    fig = plt.figure(figsize=(14, fig_height))
    
    # ヒートマップ用の軸（左側）
    ax_heat = plt.axes([0.05, 0.1, 0.08, 0.85])
    
    # メインプロット用の軸（右側）
    ax_main = plt.axes([0.18, 0.1, 0.75, 0.85])
    
    # カラーマップの作成（赤 → 白 → 青）
    colors_heatmap = ['#d73027', '#f46d43', '#fdae61', '#fee090', '#ffffbf',
                      '#e0f3f8', '#abd9e9', '#74add1', '#4575b4']
    cmap = LinearSegmentedColormap.from_list('custom_diverging', colors_heatmap)
    
    # ヒートマップデータの準備
    heatmap_data = np.array([[avg_scores[sid]] for sid in sentence_ids])
    
    # ヒートマップの描画
    im = ax_heat.imshow(heatmap_data, cmap=cmap, aspect='auto', 
                        vmin=-1.0, vmax=1.0)
    
    # ヒートマップの軸設定（上から下へ昇順）
    ax_heat.set_yticks(range(n_sentences))
    ax_heat.set_yticklabels([f'{sid}' for sid in sentence_ids], fontsize=8)
    ax_heat.set_ylabel('Sentence ID', fontsize=12, fontweight='bold')
    ax_heat.set_xticks([0])
    ax_heat.set_xticklabels(['Avg\nScore'], fontsize=9)
    ax_heat.set_title('ID', fontsize=10, fontweight='bold')
    # Y軸の原点を上に設定
    ax_heat.set_ylim(n_sentences - 0.5, -0.5)
    
    # メインプロットの描画
    model_colors = {
        'transformer1': '#1f77b4',  # 青
        'transformer2': '#2ca02c',  # 緑
        'dictionary': '#ff7f0e'      # オレンジ
    }
    
    model_markers = {
        'transformer1': 'o',  # 円
        'transformer2': 's',  # 四角
        'dictionary': '^'     # 三角
    }
    
    model_labels = {
        'transformer1': 'Transformer 1',
        'transformer2': 'Transformer 2',
        'dictionary': 'Dictionary'
    }
    
    # 各Sentence IDについてプロット
    avg_score_positions = []  # 平均スコアの位置を記録
    
    for idx, sid in enumerate(sentence_ids):
        # このSentence IDのデータを取得
        sid_data = merged_df[merged_df['sentence_id'] == sid]
        
        # 各モデルのスコアをプロット
        for _, row in sid_data.iterrows():
            model = row['model']
            score = row['score']
            
            ax_main.scatter(score, idx, 
                          color=model_colors[model],
                          marker=model_markers[model],
                          s=80, alpha=0.7, 
                          edgecolors='black', linewidths=0.5)
        
        # この文章の平均スコアを記録
        avg_score_positions.append((avg_scores[sid], idx))
    
    # 平均スコアの線を描画
    if avg_score_positions:
        avg_x = [pos[0] for pos in avg_score_positions]
        avg_y = [pos[1] for pos in avg_score_positions]
        ax_main.plot(avg_x, avg_y, color='red', linewidth=2, 
                    linestyle='-', alpha=0.8, label='Average Score', zorder=1)
    
    # 中立線（スコア0）を描画
    ax_main.axvline(x=0, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Neutral (0.0)')
    
    # 中立ゾーン（-0.2 ~ 0.2）を塗りつぶし
    ax_main.axvspan(-0.2, 0.2, alpha=0.1, color='gray', label='Neutral Zone')
    
    # 軸の設定
    ax_main.set_xlabel('Sentiment Score', fontsize=13, fontweight='bold')
    ax_main.set_ylabel('Sentence ID', fontsize=13, fontweight='bold')
    ax_main.set_title('Sentiment Score Distribution by Model', 
                     fontsize=15, fontweight='bold', pad=20)
    
    # Y軸の設定（上から下へ昇順）
    ax_main.set_yticks(range(n_sentences))
    ax_main.set_yticklabels([f'{sid}' for sid in sentence_ids], fontsize=8)
    # Y軸の原点を上に設定（上から下へ昇順）
    ax_main.set_ylim(n_sentences - 0.5, -0.5)
    
    # X軸の設定
    ax_main.set_xlim(-1.1, 1.1)
    ax_main.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    
    # グリッドの追加
    ax_main.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    
    # 凡例の作成（モデル + 平均線）
    legend_elements = [
        plt.Line2D([0], [0], color='red', linewidth=2, linestyle='-', 
                   label='Average Score'),
        mpatches.Patch(facecolor=model_colors['transformer1'], 
                      edgecolor='black', label='Transformer 1 (○)'),
        mpatches.Patch(facecolor=model_colors['transformer2'], 
                      edgecolor='black', label='Transformer 2 (□)'),
        mpatches.Patch(facecolor=model_colors['dictionary'], 
                      edgecolor='black', label='Dictionary (△)')
    ]
    
    ax_main.legend(handles=legend_elements, loc='upper right', 
                  fontsize=10, framealpha=0.9)
    
    # カラーバーの追加（下部）
    cbar_ax = plt.axes([0.18, 0.02, 0.75, 0.02])
    cbar = plt.colorbar(im, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Average Sentiment Score (Heatmap)', fontsize=11)
    cbar.ax.tick_params(labelsize=9)
    
    # 統計情報の追加
    stats_text = 'Statistics:\n'
    stats_text += f'Total Sentences: {n_sentences}\n'
    stats_text += f'Score Range: [{merged_df["score"].min():.3f}, {merged_df["score"].max():.3f}]\n'
    stats_text += f'Overall Mean: {merged_df["score"].mean():.3f}\n'
    stats_text += f'Overall Std: {merged_df["score"].std():.3f}'
    
    ax_main.text(0.02, 0.98, stats_text, transform=ax_main.transAxes,
                fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✓ スコアプロットを保存: {output_path}")

def create_score_distribution(merged_df, output_path):
    """
    全体のスコア分布をヒストグラムで表示
    
    Parameters:
    - merged_df: 統合データフレーム
    - output_path: 出力ファイルパス
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # モデルごとにヒストグラムを作成
    models = ['transformer1', 'transformer2', 'dictionary']
    model_labels = {
        'transformer1': 'Transformer 1',
        'transformer2': 'Transformer 2',
        'dictionary': 'Dictionary'
    }
    model_colors = {
        'transformer1': '#1f77b4',
        'transformer2': '#2ca02c',
        'dictionary': '#ff7f0e'
    }
    
    for model in models:
        model_data = merged_df[merged_df['model'] == model]
        scores = model_data['score'].values
        
        ax.hist(scores, bins=40, alpha=0.5, label=model_labels[model],
               color=model_colors[model], edgecolor='black', linewidth=0.5)
    
    # 中立ゾーンの表示
    ax.axvspan(-0.2, 0.2, alpha=0.15, color='gray', label='Neutral Zone (-0.2 to 0.2)')
    ax.axvline(x=0, color='black', linestyle='--', linewidth=2, label='Zero Line')
    
    # 全体の平均値
    overall_mean = merged_df['score'].mean()
    ax.axvline(x=overall_mean, color='red', linestyle='-', linewidth=2, 
              label=f'Overall Mean: {overall_mean:.3f}')
    
    ax.set_xlabel('Sentiment Score', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title('Score Distribution by Model', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # 統計情報
    stats_text = 'Model Statistics:\n'
    for model in models:
        model_data = merged_df[merged_df['model'] == model]['score']
        stats_text += f'\n{model_labels[model]}:\n'
        stats_text += f'  Mean: {model_data.mean():.4f}\n'
        stats_text += f'  Std: {model_data.std():.4f}\n'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           fontsize=8, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ スコア分布を保存: {output_path}")

def visualize_integrated_results(out_dir="out", png_dir="png", merged_dir="merged"):
    """
    統合されたデータを可視化
    """
    # 出力フォルダの作成
    os.makedirs(png_dir, exist_ok=True)
    os.makedirs(merged_dir, exist_ok=True)
    
    print("=" * 70)
    print("感情分析結果の統合可視化")
    print("=" * 70)
    
    try:
        # データの読み込みと統合
        print("\n[Step 1] データの読み込みと統合")
        merged_df = load_and_merge_results(out_dir)
        
        # 統合データをCSVとして保存（mergedフォルダへ）
        merged_csv_path = os.path.join(merged_dir, "merged_results.csv")
        merged_df.to_csv(merged_csv_path, index=False, encoding='utf-8-sig')
        print(f"\n統合データを保存: {merged_csv_path}")
        
        # 可視化1: スコアプロット（ヒートマップ付き）
        print("\n[Step 2] スコアプロット作成中...")
        score_plot_path = os.path.join(png_dir, "integrated_score_plot.png")
        create_score_plot_with_heatmap(merged_df, score_plot_path)
        
        # 可視化2: スコア分布
        print("\n[Step 3] スコア分布作成中...")
        distribution_path = os.path.join(png_dir, "integrated_score_distribution.png")
        create_score_distribution(merged_df, distribution_path)
        
        print("\n" + "=" * 70)
        print("全ての可視化が完了しました！")
        print(f"統合データ: {merged_dir}/")
        print(f"可視化結果: {png_dir}/")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    メイン処理
    """
    # 日本語フォント設定
    setup_japanese_font()
    
    # 統合可視化実行
    visualize_integrated_results(out_dir="out", png_dir="png", merged_dir="merged")

if __name__ == "__main__":
    main()