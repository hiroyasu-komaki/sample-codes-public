"""
SimpleTransformer: Transformerの動作を擬似的に可視化するクラス
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import matplotlib.font_manager as fm
import platform
# japanize_matplotlibはPython 3.12ではdistutilsの削除により動作しないため削除


class SimpleTransformer:
    """簡易的なTransformerシミュレーター"""
    
    def __init__(self):
        # macOS用の日本語フォントの設定
        if platform.system() == 'Darwin':  # macOS
            # macOSで利用可能な日本語フォントを設定
            japanese_fonts = ['Hiragino Sans', 'Hiragino Kaku Gothic ProN', 
                            'Hiragino Kaku Gothic Pro', 'Yu Gothic', 'AppleGothic']
            
            # 利用可能なフォント名のリストを取得
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            
            # 日本語フォントを検索
            font_found = False
            for font in japanese_fonts:
                if font in available_fonts:
                    rcParams['font.family'] = font
                    font_found = True
                    break
            
            if not font_found:
                # Hiraginoの部分一致でも探す
                for font_name in available_fonts:
                    if 'Hiragino' in font_name or 'Yu Gothic' in font_name:
                        rcParams['font.family'] = font_name
                        font_found = True
                        break
            
            if not font_found:
                # フォントが見つからない場合はデフォルトのsans-serifを使用
                rcParams['font.family'] = 'sans-serif'
        else:
            rcParams['font.family'] = 'sans-serif'
        
        # 簡易的な単語辞書（実際はもっと大きい）
        self.vocab = {
            '私': 0, 'が': 1, '公園': 2, 'を': 3, '歩いて': 4, 'いる': 5, 'と': 6,
            '向こう': 7, 'から': 8, '犬': 9, '歩いてきた': 10, '。': 11,
            'は': 12, 'その': 13, '見た': 14, '[END]': 15
        }
        self.id_to_word = {v: k for k, v in self.vocab.items()}
        
    def tokenize(self, text):
        """テキストをトークン化（簡易版）"""
        # 実際はもっと複雑なトークナイザーを使用
        words = ['私', 'が', '公園', 'を', '歩いて', 'いる', 'と', '向こう', 
                 'から', '犬', 'が', '歩いてきた', '。', 
                 '私', 'は', 'その', '犬', 'を', '見た', '。']
        return words
    
    def compute_attention_scores(self, query_word, all_words, query_idx):
        """Attentionスコアを計算（擬似的）"""
        scores = np.zeros(len(all_words))
        
        # ルールベースで擬似的なスコアを計算
        for i, word in enumerate(all_words):
            # 未来の単語は見えない（Causal Masking）
            if i > query_idx:
                scores[i] = 0
                continue
            
            # 擬似的な関連性スコア
            if query_word == 'その' and word == '犬' and i < query_idx:
                scores[i] = 0.8  # 「その」は前の「犬」を参照
            elif query_word == '犬' and word in ['を', 'が']:
                scores[i] = 0.6  # 格助詞との関連
            elif query_word == 'を' and word == '見た':
                scores[i] = 0.9  # 目的語と動詞
            elif query_word == '見た' and word in ['犬', 'を']:
                scores[i] = 0.7  # 動詞と目的語
            elif query_word == word:
                scores[i] = 0.5  # 自分自身
            elif abs(i - query_idx) == 1:
                scores[i] = 0.4  # 隣接単語
            elif abs(i - query_idx) <= 3:
                scores[i] = 0.2  # 近い単語
            else:
                scores[i] = 0.1  # 遠い単語
        
        # 正規化（Softmax的な処理）
        scores = scores / (np.sum(scores) + 1e-10)
        return scores
    
    def visualize_understanding(self, text, output_path='attention_understanding.png'):
        """文章理解のプロセスを可視化"""
        words = self.tokenize(text)
        n_words = len(words)
        
        # Attentionマップの作成
        attention_matrix = np.zeros((n_words, n_words))
        
        for i, query_word in enumerate(words):
            scores = self.compute_attention_scores(query_word, words, i)
            attention_matrix[i, :] = scores
        
        # 可視化
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # 左側：Attentionマップ
        im = ax1.imshow(attention_matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=0.3)
        ax1.set_xticks(range(n_words))
        ax1.set_yticks(range(n_words))
        ax1.set_xticklabels(words, rotation=45, ha='right')
        ax1.set_yticklabels(words)
        ax1.set_xlabel('参照される単語（Key）', fontsize=12)
        ax1.set_ylabel('注目している単語（Query）', fontsize=12)
        ax1.set_title('Attention マップ（文章理解）\n各行が各単語からの視点', fontsize=14, fontweight='bold')
        
        # カラーバー
        cbar = plt.colorbar(im, ax=ax1)
        cbar.set_label('Attention スコア', fontsize=11)
        
        # グリッド
        ax1.set_xticks(np.arange(n_words) - 0.5, minor=True)
        ax1.set_yticks(np.arange(n_words) - 0.5, minor=True)
        ax1.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
        
        # 右側：特定の単語のAttentionを強調表示
        target_idx = 15  # 「その」のインデックス
        target_word = words[target_idx]
        target_scores = attention_matrix[target_idx, :]
        
        colors = plt.cm.YlOrRd(target_scores / 0.3)
        bars = ax2.barh(range(n_words), target_scores, color=colors)
        ax2.set_yticks(range(n_words))
        ax2.set_yticklabels(words)
        ax2.set_xlabel('Attention スコア', fontsize=12)
        ax2.set_title(f'「{target_word}」が注目している単語', fontsize=14, fontweight='bold')
        ax2.invert_yaxis()
        ax2.grid(axis='x', alpha=0.3)
        
        # 最も高いスコアの単語を強調
        max_idx = np.argmax(target_scores[:target_idx])  # 自分より前の単語のみ
        ax2.get_yticklabels()[max_idx].set_color('red')
        ax2.get_yticklabels()[max_idx].set_fontweight('bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 文章理解の可視化を保存しました: {output_path}")
        return attention_matrix
    
    def visualize_generation(self, output_path='attention_generation.png'):
        """文章生成のプロセスを可視化"""
        # 入力文
        input_text = "犬について教えて"
        input_words = ['犬', 'について', '教えて']
        
        # 生成プロセス（擬似的）
        generated_words = ['犬', 'は', '哺乳類', 'で', 'す']
        
        # 各生成ステップでのAttentionを計算
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for step in range(5):
            ax = axes[step]
            
            # 現在のコンテキスト（入力 + これまでの生成）
            context = input_words + generated_words[:step]
            current_word = generated_words[step] if step < len(generated_words) else ''
            
            # Attentionスコアを擬似的に計算
            n_context = len(context)
            scores = np.zeros(n_context)
            
            # ルールベースでスコアを設定
            if step == 0:  # 「犬」を生成
                scores[0] = 0.7  # 入力の「犬」
                scores[1] = 0.2  # 「について」
                scores[2] = 0.6  # 「教えて」
            elif step == 1:  # 「は」を生成
                scores[0] = 0.3
                scores[3] = 0.8  # 生成した「犬」
                scores[2] = 0.4
            elif step == 2:  # 「哺乳類」を生成
                scores[0] = 0.6  # 入力の「犬」
                scores[3] = 0.7  # 生成した「犬」
                scores[4] = 0.5  # 「は」
                scores[2] = 0.5  # 「教えて」
            elif step == 3:  # 「で」を生成
                scores[5] = 0.8  # 「哺乳類」
                scores[4] = 0.4  # 「は」
            elif step == 4:  # 「す」を生成
                scores[6] = 0.9  # 「で」
                scores[5] = 0.5  # 「哺乳類」
            
            scores = scores / (np.sum(scores) + 1e-10)
            
            # 可視化
            colors = ['lightblue'] * len(input_words) + ['lightcoral'] * step
            bars = ax.barh(range(n_context), scores, color=colors)
            
            # ラベル
            labels = input_words + [f"[生成]{w}" for w in generated_words[:step]]
            ax.set_yticks(range(n_context))
            ax.set_yticklabels(labels, fontsize=10)
            ax.set_xlabel('Attention スコア', fontsize=10)
            ax.set_title(f'ステップ {step+1}: 「{current_word}」を生成', 
                        fontsize=12, fontweight='bold', color='darkgreen')
            ax.invert_yaxis()
            ax.grid(axis='x', alpha=0.3)
            ax.set_xlim(0, 0.5)
            
            # 凡例
            if step == 0:
                blue_patch = mpatches.Patch(color='lightblue', label='入力文')
                red_patch = mpatches.Patch(color='lightcoral', label='生成済み')
                ax.legend(handles=[blue_patch, red_patch], loc='lower right')
        
        # 最後のサブプロットは使わない
        axes[5].axis('off')
        axes[5].text(0.5, 0.5, '生成完了！\n\n出力: 「犬は哺乳類です」', 
                    ha='center', va='center', fontsize=16, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 文章生成の可視化を保存しました: {output_path}")
    
    def visualize_detailed_generation_step(self, output_path='attention_generation_detail.png'):
        """1つの生成ステップを詳細に可視化"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # ステップ3: 「哺乳類」を生成する詳細プロセス
        input_words = ['犬', 'について', '教えて']
        generated_words = ['犬', 'は']
        context = input_words + generated_words
        
        # 1. Query, Key, Value の概念図
        ax1 = axes[0, 0]
        ax1.axis('off')
        ax1.set_xlim(0, 10)
        ax1.set_ylim(0, 10)
        
        # Query
        rect_q = mpatches.FancyBboxPatch((1, 7), 2, 1.5, boxstyle="round,pad=0.1", 
                                         edgecolor='orange', facecolor='lightyellow', linewidth=3)
        ax1.add_patch(rect_q)
        ax1.text(2, 7.75, 'Query\n「次は？」', ha='center', va='center', fontsize=11, fontweight='bold')
        
        # Keys
        for i, word in enumerate(context):
            y_pos = 5.5 - i * 0.8
            color = 'lightblue' if i < 3 else 'lightcoral'
            rect = mpatches.FancyBboxPatch((4, y_pos-0.3), 1.5, 0.6, boxstyle="round,pad=0.05",
                                          edgecolor='blue', facecolor=color, linewidth=2)
            ax1.add_patch(rect)
            ax1.text(4.75, y_pos, f'Key: {word}', ha='center', va='center', fontsize=9)
        
        # Attention計算
        ax1.annotate('', xy=(4, 4), xytext=(3, 7.5),
                    arrowprops=dict(arrowstyle='->', lw=2, color='red'))
        ax1.text(3.5, 5.5, 'Attention\n計算', ha='center', fontsize=10, 
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        # Values
        for i, word in enumerate(context):
            y_pos = 5.5 - i * 0.8
            rect = mpatches.FancyBboxPatch((7, y_pos-0.3), 1.8, 0.6, boxstyle="round,pad=0.05",
                                          edgecolor='green', facecolor='lightgreen', linewidth=2)
            ax1.add_patch(rect)
            ax1.text(7.9, y_pos, f'Value: {word}', ha='center', va='center', fontsize=9)
        
        # 出力
        rect_out = mpatches.FancyBboxPatch((4, 0.5), 2.5, 1, boxstyle="round,pad=0.1",
                                          edgecolor='darkgreen', facecolor='lightgreen', linewidth=3)
        ax1.add_patch(rect_out)
        ax1.text(5.25, 1, '出力: 哺乳類', ha='center', va='center', fontsize=12, fontweight='bold')
        
        ax1.set_title('Query-Key-Value の仕組み', fontsize=14, fontweight='bold')
        
        # 2. Attentionスコア
        ax2 = axes[0, 1]
        scores = np.array([0.6, 0.2, 0.5, 0.7, 0.5])
        scores = scores / scores.sum()
        colors = ['lightblue', 'lightblue', 'lightblue', 'lightcoral', 'lightcoral']
        
        bars = ax2.barh(range(len(context)), scores, color=colors, edgecolor='black', linewidth=1.5)
        ax2.set_yticks(range(len(context)))
        ax2.set_yticklabels(context, fontsize=11)
        ax2.set_xlabel('正規化後のスコア', fontsize=11)
        ax2.set_title('Attention スコアの分布', fontsize=13, fontweight='bold')
        ax2.invert_yaxis()
        ax2.grid(axis='x', alpha=0.3)
        
        # スコアを表示
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax2.text(score + 0.01, i, f'{score:.2f}', va='center', fontsize=10, fontweight='bold')
        
        # 3. 重み付け平均の計算
        ax3 = axes[1, 0]
        ax3.axis('off')
        ax3.set_xlim(0, 10)
        ax3.set_ylim(0, 10)
        
        ax3.text(5, 9, '重み付け平均の計算', ha='center', fontsize=14, fontweight='bold')
        
        y_start = 7.5
        for i, (word, score) in enumerate(zip(context, scores)):
            y = y_start - i * 1.2
            color = 'lightblue' if i < 3 else 'lightcoral'
            
            # Value box
            rect = mpatches.FancyBboxPatch((1, y-0.3), 2, 0.6, boxstyle="round,pad=0.05",
                                          facecolor=color, edgecolor='black', linewidth=1.5)
            ax3.add_patch(rect)
            ax3.text(2, y, word, ha='center', va='center', fontsize=10, fontweight='bold')
            
            # 掛け算記号
            ax3.text(3.5, y, '×', ha='center', va='center', fontsize=14, fontweight='bold')
            
            # スコア
            rect2 = mpatches.FancyBboxPatch((4, y-0.3), 1.5, 0.6, boxstyle="round,pad=0.05",
                                           facecolor='yellow', edgecolor='black', linewidth=1.5)
            ax3.add_patch(rect2)
            ax3.text(4.75, y, f'{score:.2f}', ha='center', va='center', fontsize=10, fontweight='bold')
            
            # 等号
            if i < len(context) - 1:
                ax3.text(6.2, y, '+', ha='center', va='center', fontsize=14, fontweight='bold')
        
        # 結果
        ax3.text(5, 1.5, '↓', ha='center', va='center', fontsize=20, fontweight='bold')
        result_box = mpatches.FancyBboxPatch((3, 0.3), 4, 0.8, boxstyle="round,pad=0.1",
                                            facecolor='lightgreen', edgecolor='darkgreen', linewidth=3)
        ax3.add_patch(result_box)
        ax3.text(5, 0.7, '文脈ベクトル → 「哺乳類」', ha='center', va='center', 
                fontsize=11, fontweight='bold')
        
        # 4. 次の単語の予測
        ax4 = axes[1, 1]
        
        # 候補単語とそのスコア
        candidates = ['哺乳類', '動物', 'ペット', '生き物', 'かわいい']
        candidate_scores = [0.85, 0.07, 0.04, 0.03, 0.01]
        
        bars = ax4.bar(candidates, candidate_scores, color='skyblue', edgecolor='black', linewidth=1.5)
        bars[0].set_color('lightgreen')
        bars[0].set_edgecolor('darkgreen')
        bars[0].set_linewidth(3)
        
        ax4.set_ylabel('予測スコア（確率）', fontsize=11)
        ax4.set_title('次の単語の候補と確率', fontsize=13, fontweight='bold')
        ax4.set_ylim(0, 1)
        ax4.grid(axis='y', alpha=0.3)
        
        # 最高スコアを強調
        for i, (bar, score) in enumerate(zip(bars, candidate_scores)):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{score:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax4.text(0, 0.95, '← 選択！', fontsize=12, fontweight='bold', color='darkgreen')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 生成ステップの詳細可視化を保存しました: {output_path}")
