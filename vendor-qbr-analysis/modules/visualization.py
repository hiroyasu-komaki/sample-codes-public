"""
可視化モジュール
vendor-qbr-analysis.md 第6章対応（必須4グラフ）
matplotlibのみ使用
日本語フォント対応版
"""

import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from typing import Dict, Optional

# 日本語フォント設定
def setup_japanese_font():
    """日本語フォントを設定（macOS/Linux両対応）"""
    # 利用可能な日本語フォントを探す
    japanese_font_candidates = [
        # macOS標準フォント（最優先）
        'Hiragino Sans',
        'Hiragino Kaku Gothic ProN',
        'Hiragino Maru Gothic ProN',
        'Yu Gothic',
        # Linux用フォント
        'Noto Sans CJK JP',
        'Noto Sans JP', 
        'IPAexGothic',
        'IPAGothic',
        'TakaoPGothic',
        'VL PGothic',
        # フォールバック
        'DejaVu Sans'
    ]
    
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    for font in japanese_font_candidates:
        if font in available_fonts:
            plt.rcParams['font.family'] = font
            print(f"Using font: {font}")
            break
    else:
        # フォールバック
        plt.rcParams['font.sans-serif'] = japanese_font_candidates
    
    # マイナス記号の文字化け対策
    plt.rcParams['axes.unicode_minus'] = False

# 初期化時にフォント設定を実行
setup_japanese_font()


def plot_radar_chart(data: pd.DataFrame, config: Dict, filename: str = "radar_chart.png") -> None:
    """
    レーダーチャート（4大分類比較）
    - 軸: performance, technical, business, improvement
    - 4ベンダーを同時プロット
    """
    categories = list(config["categories"].keys())
    N = len(categories)

    # 角度設定
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure(figsize=(6, 6))
    ax = plt.subplot(111, polar=True)

    for vendor in config["vendors"]:
        vendor_id = vendor["id"]
        color = vendor["color"]

        values = data[data["vendor_id"] == vendor_id]["mean_score"].tolist()
        values += values[:1]

        ax.plot(angles, values, linewidth=2, linestyle='solid', label=vendor["name"], color=color)
        ax.fill(angles, values, alpha=0.1, color=color)

    plt.xticks(angles[:-1], categories, fontsize=11)
    plt.yticks(fontsize=9)
    plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)

    output_path = os.path.join(config["output"]["figures_dir"], filename)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()
    print(f"✓ Radar chart saved: {output_path}")


def plot_category_radar_chart(data: pd.DataFrame, category: str, config: Dict, filename: str = None) -> None:
    """
    カテゴリ別詳細レーダーチャート
    - 指定されたカテゴリ内の全項目を軸として表示
    - 4ベンダーを同時プロット
    
    Args:
        data: bias_adjusted_scores データフレーム
        category: カテゴリ名 ('performance', 'technical', 'business', 'improvement')
        config: 設定ディクショナリ
        filename: 出力ファイル名（Noneの場合は自動生成）
    """
    if filename is None:
        filename = f"radar_chart_{category}.png"
    
    # カテゴリ内の項目リストを取得
    items = config["categories"][category]["items"]
    category_name_ja = config["categories"][category]["name_ja"]
    N = len(items)

    # 角度設定
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    # 項目名を短縮表示用に変換（プレフィックス除去）
    item_labels = [item.replace(f"{category}_", "") for item in items]

    fig = plt.figure(figsize=(5, 5))
    ax = plt.subplot(111, polar=True)

    for vendor in config["vendors"]:
        vendor_id = vendor["id"]
        color = vendor["color"]

        # ベンダーごとの各項目の平均スコアを取得
        vendor_data = data[data["vendor_id"] == vendor_id]
        values = [vendor_data[item].mean() for item in items]
        values += values[:1]

        ax.plot(angles, values, linewidth=1.5, linestyle='solid', label=vendor["name"], color=color)
        ax.fill(angles, values, alpha=0.1, color=color)

    # 軸ラベル設定（フォントサイズを小さく）
    plt.xticks(angles[:-1], item_labels, fontsize=7)
    plt.yticks(fontsize=7)
    
    # タイトル追加
    plt.title(category_name_ja, fontsize=10, pad=20, fontweight='bold')
    
    # 凡例は表示しない（総合評価のみに表示）
    ax.grid(True)

    output_path = os.path.join(config["output"]["figures_dir"], filename)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"✓ Category radar chart saved: {output_path}")


def plot_heatmap(data: pd.DataFrame, config: Dict, filename: str = "heatmap.png") -> None:
    """
    ヒートマップ（詳細項目 × ベンダー）
    """
    pivot_table = data.pivot(index="item", columns="vendor_id", values="score")

    fig, ax = plt.subplots(figsize=(10, 6))
    cax = ax.imshow(pivot_table, cmap="RdYlGn", aspect="auto")

    ax.set_xticks(np.arange(len(pivot_table.columns)))
    ax.set_yticks(np.arange(len(pivot_table.index)))
    ax.set_xticklabels(pivot_table.columns)
    ax.set_yticklabels(pivot_table.index)

    plt.colorbar(cax)
    plt.tight_layout()

    output_path = os.path.join(config["output"]["figures_dir"], filename)
    plt.savefig(output_path, dpi=120)
    plt.close()
    print(f"✓ Heatmap saved: {output_path}")


def plot_positioning_map(
    data: pd.DataFrame, 
    config: Dict, 
    filename: str = "positioning_map.png",
    x_label: Optional[str] = None,
    y_label: Optional[str] = None
) -> None:
    """
    ポジショニングマップ
    X: 指定された評価軸（デフォルト: Performance）
    Y: 指定された評価軸（デフォルト: Improvement Proposals）
    バブルサイズ: respondent count
    
    Args:
        data: positioning data (vendor_id, x, y, respondent_count)
        config: 設定ディクショナリ
        filename: 出力ファイル名
        x_label: X軸のラベル（Noneの場合は"Performance"を使用）
        y_label: Y軸のラベル（Noneの場合は"Improvement Proposals"を使用）
    """
    # デフォルトラベル
    if x_label is None:
        x_label = "Performance"
    if y_label is None:
        y_label = "Improvement Proposals"
    
    fig, ax = plt.subplots(figsize=(8, 7))

    # データの範囲を取得
    x_min, x_max = data["x"].min(), data["x"].max()
    y_min, y_max = data["y"].min(), data["y"].max()
    
    # マージンを計算（データ範囲の10%）
    x_margin = (x_max - x_min) * 0.15
    y_margin = (y_max - y_min) * 0.15
    
    # バブルサイズの最大値を取得してテキスト配置に使用
    max_bubble_size = data["respondent_count"].max() * 10
    y_text_offset = (y_max - y_min) * 0.02

    for vendor in config["vendors"]:
        vendor_id = vendor["id"]
        vendor_data = data[data["vendor_id"] == vendor_id]

        ax.scatter(
            vendor_data["x"],
            vendor_data["y"],
            s=vendor_data["respondent_count"] * 10,
            label=vendor["name"],
            color=vendor["color"],
            alpha=0.7,
            edgecolors='white',
            linewidth=2
        )

        # ベンダー名のテキスト配置（バブルの上部）
        ax.text(
            vendor_data["x"].values[0],
            vendor_data["y"].values[0] + y_text_offset,
            vendor["name"],
            fontsize=11,
            ha="center",
            va="bottom",
            fontweight='bold'
        )

    # 平均値の線
    ax.axvline(data["x"].mean(), linestyle="--", color="gray", alpha=0.5, linewidth=1)
    ax.axhline(data["y"].mean(), linestyle="--", color="gray", alpha=0.5, linewidth=1)

    # 軸ラベル（日本語対応）
    ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
    ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
    
    # 軸範囲を設定（マージン付き）
    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    
    # グリッド
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 背景色
    ax.set_facecolor('#f8f9fa')

    plt.tight_layout()
    output_path = os.path.join(config["output"]["figures_dir"], filename)
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"✓ Positioning map saved: {output_path}")


def plot_boxplot_with_significance(data: pd.DataFrame, sig_df: pd.DataFrame, item_cols, config: Dict,
                                   filename: str = "boxplot_significance.png") -> None:
    """
    箱ひげ図 + 有意差マーク
    Z-score(1–5変換)列 *_z5 を評価軸として利用
    """
    score_cols = [c for c in data.columns if c.endswith("_z5")]

    fig, ax = plt.subplots(figsize=(8, 6))

    groups = [
        data[data["vendor_id"] == v["id"]][score_cols].mean(axis=1)
        for v in config["vendors"]
    ]
    labels = [v["name"] for v in config["vendors"]]

    ax.boxplot(groups, labels=labels)
    ax.set_ylabel("Z-score (1–5 normalized)")
    ax.set_title("Vendor Score Distribution")

    # 有意差マーク
    for _, row in sig_df.iterrows():
        if row["reject"]:
            x1 = labels.index(row["group1"]) + 1
            x2 = labels.index(row["group2"]) + 1
            y = max([g.max() for g in groups]) + 0.1
            ax.plot([x1, x1, x2, x2], [y, y + 0.05, y + 0.05, y], lw=1.2, color="black")
            ax.text((x1 + x2) * 0.5, y + 0.07, "*", ha="center", fontsize=16)

    output_path = os.path.join(config["output"]["figures_dir"], filename)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()
    print(f"✓ Boxplot with significance saved: {output_path}")


def plot_boxplot_comparison(data_raw: pd.DataFrame, data_adjusted: pd.DataFrame, 
                           sig_df: pd.DataFrame, item_cols, config: Dict,
                           filename: str = "boxplot_comparison.png") -> None:
    """
    補正前後の箱ひげ図比較（横に2つ並べて表示）
    
    Args:
        data_raw: 補正前データ（生スコア）
        data_adjusted: 補正後データ（Z-score 1-5正規化済み）
        sig_df: 統計検定結果
        item_cols: 評価項目列リスト
        config: 設定ディクショナリ
        filename: 出力ファイル名
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    labels = [v["name"] for v in config["vendors"]]
    
    # ========================================
    # 左側: 補正前（生スコア）
    # ========================================
    groups_raw = [
        data_raw[data_raw["vendor_id"] == v["id"]][item_cols].mean(axis=1)
        for v in config["vendors"]
    ]
    
    bp1 = ax1.boxplot(groups_raw, labels=labels, patch_artist=True)
    
    # ベンダーカラーを適用
    for patch, vendor in zip(bp1['boxes'], config["vendors"]):
        patch.set_facecolor(vendor["color"])
        patch.set_alpha(0.6)
    
    ax1.set_ylabel("スコア（1-5点）", fontsize=12, fontweight='bold')
    ax1.set_title("補正前（生スコア）", fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_ylim(0.5, 5.5)
    
    # ========================================
    # 右側: 補正後（Z-score 1-5正規化）
    # ========================================
    score_cols_z5 = [c for c in data_adjusted.columns if c.endswith("_z5")]
    
    groups_adjusted = [
        data_adjusted[data_adjusted["vendor_id"] == v["id"]][score_cols_z5].mean(axis=1)
        for v in config["vendors"]
    ]
    
    bp2 = ax2.boxplot(groups_adjusted, labels=labels, patch_artist=True)
    
    # ベンダーカラーを適用
    for patch, vendor in zip(bp2['boxes'], config["vendors"]):
        patch.set_facecolor(vendor["color"])
        patch.set_alpha(0.6)
    
    ax2.set_ylabel("Z-score（1-5正規化）", fontsize=12, fontweight='bold')
    ax2.set_title("補正後（バイアス補正済み）", fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_ylim(0.5, 5.5)
    
    # 有意差マーク（補正後のみ）
    for _, row in sig_df.iterrows():
        if row["reject"]:
            try:
                x1 = labels.index(row["group1"]) + 1
                x2 = labels.index(row["group2"]) + 1
                y = max([g.max() for g in groups_adjusted]) + 0.15
                ax2.plot([x1, x1, x2, x2], [y, y + 0.05, y + 0.05, y], 
                        lw=1.5, color="black")
                ax2.text((x1 + x2) * 0.5, y + 0.1, "*", 
                        ha="center", fontsize=18, fontweight='bold')
            except (ValueError, KeyError):
                continue
    
    plt.tight_layout()
    output_path = os.path.join(config["output"]["figures_dir"], filename)
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"✓ Boxplot comparison saved: {output_path}")


def plot_zscore_distribution(data_adjusted: pd.DataFrame, item_cols, config: Dict,
                             filename: str = "zscore_distribution.png") -> None:
    """
    Z-score標準化値の分布図（ヒストグラム + カーネル密度推定）
    
    標準化されたままの値（平均0、標準偏差1）の分布を表示
    これにより、各ベンダーの評価が標準的な分布からどれだけ偏っているかが分かる
    
    Args:
        data_adjusted: 補正後データ（Z-score列を含む）
        item_cols: 評価項目列リスト
        config: 設定ディクショナリ
        filename: 出力ファイル名
    """
    from scipy import stats
    
    # Z-score列（_z5ではなく、標準化されたままの列）を取得
    # まず、_z5列から元のZ-score値を逆算するか、
    # あるいは元のZ-score列を保持している場合はそれを使用
    
    # ここでは_z5列から標準化値を推定
    # （実装によっては、元のZ-score列を別途保存しておく方が良い）
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for idx, vendor in enumerate(config["vendors"]):
        ax = axes[idx]
        vendor_id = vendor["id"]
        vendor_name = vendor["name"]
        color = vendor["color"]
        
        # ベンダーのZ-score値を取得（_z5列から逆算）
        # _z5は1-5に正規化されているので、標準正規分布に戻す
        score_cols_z5 = [c for c in data_adjusted.columns if c.endswith("_z5")]
        vendor_data = data_adjusted[data_adjusted["vendor_id"] == vendor_id][score_cols_z5]
        
        # 全データを1次元配列に変換
        all_scores = vendor_data.values.flatten()
        
        # NaN、Infを除去
        all_scores = all_scores[np.isfinite(all_scores)]
        
        # データが不足している場合はスキップ
        if len(all_scores) < 10:
            ax.text(0.5, 0.5, f"{vendor_name}\nデータ不足", 
                   ha='center', va='center', fontsize=14,
                   transform=ax.transAxes)
            ax.set_title(f"{vendor_name}", fontsize=12, fontweight='bold')
            continue
        
        # Z-score値に変換（簡易的な逆変換）
        # _z5は平均3、標準偏差1程度に正規化されていると仮定
        z_scores = (all_scores - 3.0) / 0.8  # おおよその逆変換
        
        # 外れ値を除去（-5σ ～ +5σ の範囲のみ）
        z_scores = z_scores[(z_scores >= -5) & (z_scores <= 5)]
        
        # データが不足している場合はスキップ
        if len(z_scores) < 10:
            ax.text(0.5, 0.5, f"{vendor_name}\nデータ不足", 
                   ha='center', va='center', fontsize=14,
                   transform=ax.transAxes)
            ax.set_title(f"{vendor_name}", fontsize=12, fontweight='bold')
            continue
        
        # ヒストグラム
        try:
            n, bins, patches = ax.hist(z_scores, bins=30, density=True, 
                                       alpha=0.6, color=color, edgecolor='black')
        except Exception as e:
            print(f"Warning: ヒストグラム生成エラー ({vendor_name}): {e}")
            ax.text(0.5, 0.5, f"{vendor_name}\nヒストグラム生成エラー", 
                   ha='center', va='center', fontsize=12,
                   transform=ax.transAxes)
            ax.set_title(f"{vendor_name}", fontsize=12, fontweight='bold')
            continue
        
        # カーネル密度推定
        try:
            # 分散が0に近い場合はKDEをスキップ
            if z_scores.std() < 0.01:
                print(f"Warning: {vendor_name} の標準偏差が小さすぎるためKDEをスキップ")
            else:
                kde = stats.gaussian_kde(z_scores)
                x_range = np.linspace(z_scores.min(), z_scores.max(), 200)
                ax.plot(x_range, kde(x_range), color=color, linewidth=2, label='KDE')
        except Exception as e:
            print(f"Warning: KDE計算エラー ({vendor_name}): {e}")
            # KDEが失敗してもヒストグラムは表示されるので続行
        
        # 標準正規分布の理論曲線
        try:
            x_range_norm = np.linspace(-3, 3, 200)
            ax.plot(x_range_norm, stats.norm.pdf(x_range_norm, 0, 1), 
                   'k--', linewidth=1.5, alpha=0.7, label='標準正規分布')
        except Exception as e:
            print(f"Warning: 正規分布曲線描画エラー ({vendor_name}): {e}")
        
        # 平均値の線
        try:
            mean_val = z_scores.mean()
            ax.axvline(mean_val, color='red', linestyle='-', linewidth=2, 
                      alpha=0.8, label=f'平均: {mean_val:.2f}')
        except Exception as e:
            print(f"Warning: 平均値線描画エラー ({vendor_name}): {e}")
            mean_val = 0
        
        # 装飾
        ax.set_title(f"{vendor_name}", fontsize=12, fontweight='bold')
        ax.set_xlabel("Z-score（標準化値）", fontsize=10)
        ax.set_ylabel("密度", fontsize=10)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(-3, 3)
        
        # 統計情報を表示
        try:
            skewness_val = stats.skew(z_scores)
            std_val = z_scores.std()
            stats_text = f"平均: {mean_val:.2f}\n標準偏差: {std_val:.2f}\n歪度: {skewness_val:.2f}"
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   fontsize=8, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        except Exception as e:
            print(f"Warning: 統計情報表示エラー ({vendor_name}): {e}")
    
    plt.suptitle("ベンダー別 Z-score分布（標準化値）", fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    output_path = os.path.join(config["output"]["figures_dir"], filename)
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"✓ Z-score distribution plot saved: {output_path}")


def plot_rank_flow_chart(data: pd.DataFrame, config: Dict, 
                         filename: str = "rank_flow_chart.png") -> None:
    """
    Rank Flow Chart（セグメント別ベンダーランキングの推移）
    
    - 折れ線: ベンダー単位
    - 横軸: axis（セグメントカテゴリを保持順で並べる）
    - 縦軸: rank（invert_yaxis）
    
    Args:
        data: 統合されたセグメントランキングデータ
              (category, axis, vendor_id, rank, avg_score列を含む)
        config: 設定ディクショナリ
        filename: 出力ファイル名
    """
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # データをコピーして処理
    df = data.copy()
    
    # 横軸用のラベルを作成（category + axis）
    df["x_label"] = df["category"] + "\n" + df["axis"].astype(str)
    
    # 横軸の順序を保持するため、x座標を数値化
    unique_labels = df["x_label"].unique()
    x_mapping = {label: i for i, label in enumerate(unique_labels)}
    df["x_pos"] = df["x_label"].map(x_mapping)
    
    # カテゴリごとの境界を計算（背景色用）
    category_boundaries = []
    current_category = None
    for i, label in enumerate(unique_labels):
        category = df[df["x_label"] == label]["category"].iloc[0]
        if category != current_category:
            if current_category is not None:
                category_boundaries.append(i)
            current_category = category
    category_boundaries.append(len(unique_labels))
    
    # カテゴリごとに背景色を交互に設定
    start = 0
    colors_bg = ['#f0f0f0', '#ffffff']
    for idx, end in enumerate(category_boundaries):
        ax.axvspan(start - 0.5, end - 0.5, 
                  facecolor=colors_bg[idx % 2], 
                  alpha=0.3, 
                  zorder=0)
        start = end
    
    # ベンダーごとに折れ線を描画
    for vendor in config["vendors"]:
        vendor_id = vendor["id"]
        vendor_name = vendor["name"]
        color = vendor["color"]
        
        # ベンダーのデータを取得
        vendor_data = df[df["vendor_id"] == vendor_id].sort_values("x_pos")
        
        if len(vendor_data) == 0:
            continue
        
        # 折れ線をプロット
        ax.plot(
            vendor_data["x_pos"],
            vendor_data["rank"],
            marker='o',
            markersize=8,
            linewidth=2.5,
            label=vendor_name,
            color=color,
            alpha=0.85,
            zorder=2
        )
        
        # ランク数値をプロット上に表示
        for _, row in vendor_data.iterrows():
            ax.text(
                row["x_pos"],
                row["rank"],
                str(int(row["rank"])),
                fontsize=9,
                ha="center",
                va="bottom",
                fontweight='bold',
                color=color,
                bbox=dict(
                    boxstyle='round,pad=0.3',
                    facecolor='white',
                    edgecolor=color,
                    alpha=0.8
                ),
                zorder=3
            )
    
    # Y軸を反転（1位が上）
    ax.invert_yaxis()
    
    # Y軸の設定
    max_rank = df["rank"].max()
    ax.set_yticks(range(1, int(max_rank) + 1))
    ax.set_ylabel("ランク（順位）", fontsize=14, fontweight='bold')
    
    # X軸の設定
    ax.set_xticks(range(len(unique_labels)))
    ax.set_xticklabels(unique_labels, fontsize=9, rotation=0, ha='center')
    ax.set_xlabel("セグメント分類", fontsize=14, fontweight='bold')
    
    # カテゴリ境界に縦線を追加
    for boundary in category_boundaries[:-1]:
        ax.axvline(boundary - 0.5, color='gray', linestyle='--', 
                  linewidth=1.5, alpha=0.5, zorder=1)
    
    # グリッド
    ax.grid(True, alpha=0.3, linestyle=':', axis='y', zorder=0)
    
    # タイトル
    ax.set_title("セグメント別ベンダーランキング推移（Rank Flow Chart）", 
                fontsize=16, fontweight='bold', pad=20)
    
    # 凡例
    ax.legend(
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        fontsize=11,
        frameon=True,
        shadow=True
    )
    
    # レイアウト調整
    plt.tight_layout()
    
    # 保存
    output_path = os.path.join(config["output"]["figures_dir"], filename)
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"✓ Rank Flow Chart saved: {output_path}")