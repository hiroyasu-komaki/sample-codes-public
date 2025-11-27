"""
PDFレポート生成モジュール - Step8
reportlab.platypusベース
全てのポジショニングマップ組み合わせに対応
"""

import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics


def generate_report(final_scores_df,
                    category_scores_df,
                    significance_df,
                    config,
                    output_dir,
                    radar_path,
                    heatmap_path,
                    boxplot_path,
                    positioning_map_paths,
                    rank_flow_chart_path=None):
    """
    PDFレポート生成メイン関数
    
    Args:
        final_scores_df: 最終スコアデータフレーム
        category_scores_df: カテゴリ別スコアデータフレーム
        significance_df: 統計検定結果データフレーム
        config: 設定ディクショナリ
        output_dir: 出力ディレクトリ
        radar_path: 総合レーダーチャートのパス
        heatmap_path: ヒートマップのパス
        boxplot_path: 箱ひげ図のパス
        positioning_map_paths: dict - 全てのポジショニングマップのパス
                               例: {'performance_technical_raw': 'path/to/file.png', ...}
        rank_flow_chart_path: Rank Flow Chartのパス（オプション）
    """

    pdf_path = os.path.join(output_dir, "Vendor_QBR_Report.pdf")

    # PDF設定
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=landscape(A4),
        title="Vendor QBR Report",
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    # フォント登録 (日本語)
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

    styles = getSampleStyleSheet()

    # 既存スタイル Title を日本語対応に変更
    styles["Title"].fontName = "HeiseiMin-W3"
    styles["Title"].fontSize = 22
    styles["Title"].leading = 26

    # 日本語ヘッダースタイル追加
    styles.add(ParagraphStyle(name="Header", fontName="HeiseiMin-W3", fontSize=16, leading=20, spaceAfter=10))

    # 日本語サブヘッダースタイル追加
    styles.add(ParagraphStyle(name="SubHeader", fontName="HeiseiMin-W3", fontSize=13, leading=16, spaceAfter=8))

    # 日本語本文スタイル追加
    styles.add(ParagraphStyle(name="NormalJP", fontName="HeiseiMin-W3", fontSize=11, leading=14))
    
    # コンパクトな日本語本文スタイル追加（ポジショニングマップ用）
    styles.add(ParagraphStyle(name="CompactJP", fontName="HeiseiMin-W3", fontSize=9, leading=11, spaceAfter=2))

    story = []

    # ===============================================================
    # 表紙
    # ===============================================================
    story.append(Paragraph("ベンダーQBR評価レポート", styles["Title"]))
    story.append(Spacer(1, 50))
    story.append(PageBreak())

    # ===============================================================
    # カテゴリ別評価セクション - レーダーチャート
    # レイアウト: 左側に総合評価、右側に4つのカテゴリ別レーダー（2x2）
    # ===============================================================
    story.append(Paragraph("1. カテゴリ別評価チャート", styles["Header"]))
    story.append(Spacer(1, 10))

    # 画像サイズ設定
    main_radar_width = 380
    main_radar_height = 380
    sub_radar_width = 180
    sub_radar_height = 180

    # テーブルデータ作成
    # 左列: 総合評価レーダーチャート（2行分をマージ）
    # 右列: 4つのカテゴリ別レーダーチャート（2x2配置）
    
    main_radar_img = Image(radar_path, width=main_radar_width, height=main_radar_height)
    
    # カテゴリ別レーダーチャートのパス
    category_radar_paths = {
        'performance': 'output/figures/radar_chart_performance.png',
        'technical': 'output/figures/radar_chart_technical.png',
        'business': 'output/figures/radar_chart_business.png',
        'improvement': 'output/figures/radar_chart_improvement.png'
    }
    
    # カテゴリ別レーダーチャート画像を読み込み
    performance_img = Image(category_radar_paths['performance'], width=sub_radar_width, height=sub_radar_height)
    technical_img = Image(category_radar_paths['technical'], width=sub_radar_width, height=sub_radar_height)
    business_img = Image(category_radar_paths['business'], width=sub_radar_width, height=sub_radar_height)
    improvement_img = Image(category_radar_paths['improvement'], width=sub_radar_width, height=sub_radar_height)
    
    # 右側の2x2グリッドテーブル作成
    sub_radar_table = Table([
        [performance_img, technical_img],
        [business_img, improvement_img]
    ], colWidths=[sub_radar_width + 10, sub_radar_width + 10])
    
    sub_radar_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    # メインレイアウトテーブル（左: 総合評価、右: カテゴリ別4つ）
    radar_layout_table = Table([
        [main_radar_img, sub_radar_table]
    ], colWidths=[main_radar_width + 20, (sub_radar_width + 10) * 2 + 20])
    
    radar_layout_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(radar_layout_table)
    story.append(PageBreak())

    # ===============================================================
    # ヒートマップ
    # ===============================================================
    story.append(Paragraph("2. 詳細項目ヒートマップ", styles["Header"]))

    heatmap_img = Image(heatmap_path, width=600, height=380)
    story.append(heatmap_img)
    story.append(PageBreak())

    # ===============================================================
    # 箱ひげ図 - 補正前後比較 + 有意差検定
    # ===============================================================
    story.append(Paragraph("3. スコア分布比較（補正前後）", styles["Header"]))
    story.append(Spacer(1, 5))
    
    # 補正前後比較の箱ひげ図（横並び）- サイズを調整
    comparison_img = Image('output/figures/boxplot_comparison.png', width=680, height=290)
    story.append(comparison_img)
    story.append(Spacer(1, 8))
    
    # 説明文
    explanation = Paragraph(
        "左図は回答者バイアス補正前の生スコア、右図は補正後のスコアです。"
        "補正により、評価者ごとの甘辛バイアスが除去され、より公平な比較が可能になります。",
        styles["NormalJP"]
    )
    story.append(explanation)
    story.append(PageBreak())
    
    # ===============================================================
    # Z-score分布図
    # ===============================================================
    story.append(Paragraph("4. Z-score標準化値の分布分析", styles["Header"]))
    story.append(Spacer(1, 3))
    
    # 画像サイズを調整（高さを480pxに縮小して説明文との間隔を確保）
    zscore_img = Image('output/figures/zscore_distribution.png', width=650, height=480)
    story.append(zscore_img)
    story.append(Spacer(1, 5))
    
    # 説明文（CompactJPスタイルを使用して文字サイズを小さく）
    zscore_explanation = Paragraph(
        "各ベンダーのZ-score標準化値（平均0、標準偏差1）の分布を示します。"
        "標準正規分布（黒い破線）からの乖離は、評価の偏りを示しています。"
        "赤い実線は各ベンダーの平均値です。",
        styles["CompactJP"]
    )
    story.append(zscore_explanation)
    story.append(PageBreak())

    # ===============================================================
    # Positioning Maps（全組み合わせ）
    # ===============================================================
    story.append(Paragraph("5. ポジショニングマップ（全組み合わせ）", styles["Header"]))
    story.append(Spacer(1, 10))
    
    # カテゴリの日本語名マッピング
    category_names_ja = {
        "performance": "パフォーマンス",
        "technical": "技術レベル",
        "business": "ビジネス理解",
        "improvement": "改善提案"
    }
    
    # 組み合わせの定義（表示順序）
    combinations = [
        ("performance", "technical"),
        ("performance", "business"),
        ("performance", "improvement"),
        ("technical", "business"),
        ("technical", "improvement"),
        ("business", "improvement")
    ]
    
    # ========================================
    # 5-1. Raw版（項目単純平均）- 3列2行レイアウト
    # ========================================
    story.append(Paragraph("5-1. 項目単純平均によるポジショニングマップ", styles["SubHeader"]))
    story.append(Spacer(1, 5))
    
    # 画像サイズとマージン設定（横向きA4: 842x595pt）
    # ページ余白を考慮して調整
    img_width = 240
    img_height = 190
    
    # Raw版のテーブルデータ作成（3列2行）
    raw_table_data = []
    raw_images = []
    
    for cat_x, cat_y in combinations:
        raw_key = f"{cat_x}_{cat_y}_raw"
        if raw_key in positioning_map_paths:
            # 画像とキャプション
            img = Image(positioning_map_paths[raw_key], width=img_width, height=img_height)
            caption = f"{category_names_ja[cat_x]} × {category_names_ja[cat_y]}"
            # テーブルセルに画像とキャプションを組み合わせ（CompactJPスタイル使用）
            cell_content = [[img], [Paragraph(caption, styles["CompactJP"])]]
            raw_images.append(Table(cell_content, colWidths=[img_width]))
    
    # 3列2行に配置
    raw_table_data = [
        raw_images[0:3],  # 1行目: 0, 1, 2
        raw_images[3:6]   # 2行目: 3, 4, 5
    ]
    
    raw_table = Table(raw_table_data, colWidths=[img_width + 10] * 3)
    raw_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(raw_table)
    story.append(PageBreak())
    
    # ========================================
    # 5-2. Weighted版（カテゴリ重み付け平均）- 3列2行レイアウト
    # ========================================
    story.append(Paragraph("5-2. カテゴリ重み付け平均によるポジショニングマップ", styles["SubHeader"]))
    story.append(Spacer(1, 5))
    
    # Weighted版のテーブルデータ作成（3列2行）
    weighted_table_data = []
    weighted_images = []
    
    for cat_x, cat_y in combinations:
        weighted_key = f"{cat_x}_{cat_y}_weighted"
        if weighted_key in positioning_map_paths:
            # 画像とキャプション
            img = Image(positioning_map_paths[weighted_key], width=img_width, height=img_height)
            caption = f"{category_names_ja[cat_x]} × {category_names_ja[cat_y]}"
            # テーブルセルに画像とキャプションを組み合わせ（CompactJPスタイル使用）
            cell_content = [[img], [Paragraph(caption, styles["CompactJP"])]]
            weighted_images.append(Table(cell_content, colWidths=[img_width]))
    
    # 3列2行に配置
    weighted_table_data = [
        weighted_images[0:3],  # 1行目: 0, 1, 2
        weighted_images[3:6]   # 2行目: 3, 4, 5
    ]
    
    weighted_table = Table(weighted_table_data, colWidths=[img_width + 10] * 3)
    weighted_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(weighted_table)
    story.append(PageBreak())

    # ===============================================================
    # Rank Flow Chart（セグメント別ベンダーランキング推移）
    # ===============================================================
    if rank_flow_chart_path and os.path.exists(rank_flow_chart_path):
        story.append(Paragraph("6. セグメント別ベンダーランキング推移", styles["Header"]))
        story.append(Spacer(1, 10))
        
        # Rank Flow Chart画像を挿入（横向きページに最適化）
        rank_flow_img = Image(rank_flow_chart_path, width=750, height=400)
        story.append(rank_flow_img)
        story.append(Spacer(1, 10))
        
        # 説明文
        rank_flow_explanation = Paragraph(
            "評価者群、部門、利用頻度、インシデント経験、部門分類の各セグメントにおける"
            "ベンダーランキングの推移を示します。"
            "折れ線の上下移動はランク変動を表し、上方向はランク向上（順位が上がる）を意味します。"
            "セグメント間でのランク変動パターンから、各ベンダーの強み・弱みを把握できます。",
            styles["NormalJP"]
        )
        story.append(rank_flow_explanation)
        story.append(PageBreak())

    # PDF Export
    doc.build(story)
    print(f"✓ PDF Report saved: {pdf_path}")