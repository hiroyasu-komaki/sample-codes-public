"""
ベンダーQBR評価分析システム - メインエントリポイント

vendor-qbr-analysis.mdに基づいた分析を実行します
"""

import sys
import argparse
import pandas as pd
from itertools import combinations

from modules import utils
from modules import data_loader
from modules import data_cleansing
from modules import bias_analysis
from modules import vendor_evaluation
from modules import statistical_tests
from modules import segment_analysis
from modules import visualization
from modules import report_generator


def main():
    """メイン実行関数"""
    
    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(description='ベンダーQBR評価分析システム')
    parser.add_argument('--config', default='config/config.yaml', help='設定ファイルパス')
    parser.add_argument('--steps', help='実行するステップ（カンマ区切り）')
    args = parser.parse_args()
    
    # 設定読み込み
    print("=" * 60)
    print("ベンダーQBR評価分析システム")
    print("=" * 60)
    print()
    
    config = utils.load_config(args.config)
    logger = utils.setup_logging(config)
    utils.ensure_output_dirs(config)
    
    logger.info("分析を開始します")
    logger.info(f"設定ファイル: {args.config}")
    
    try:
        # ==================================================
        # ステップ1: データ読み込み
        # ==================================================
        logger.info("="*60)
        logger.info("ステップ1: データ読み込みと検証")
        logger.info("="*60)
        
        df, stats = data_loader.validate_and_load(config)
        logger.info(f"✓ データ読み込み完了: {len(df)}レコード")
        
        # ==================================================
        # ステップ2: データクレンジング
        # ==================================================
        logger.info("")
        logger.info("="*60)
        logger.info("ステップ2: データクレンジング")
        logger.info("="*60)
        
        df_clean, cleansing_results = data_cleansing.cleanse_data(df, config)
        
        # クレンジング結果のサマリー表示
        data_cleansing.display_cleansing_summary(cleansing_results)
        
        logger.info(f"✓ データクレンジング完了: {len(df_clean)}レコード")
        
        # クレンジング結果をCSVに保存
        utils.save_dataframe(df_clean, 'cleaned_data.csv', config)

        # ==================================================
        # ステップ3: バイアス分析 (bias_analysis)
        # ==================================================
        logger.info("")
        logger.info("="*60)
        logger.info("ステップ3: 回答者バイアス分析とスコア補正")
        logger.info("="*60)

        # 評価項目列の抽出
        item_cols = (
            config["categories"]["performance"]["items"]
            + config["categories"]["technical"]["items"]
            + config["categories"]["business"]["items"]
            + config["categories"]["improvement"]["items"]
        )

        # 回答者プロファイル作成
        profile_df = bias_analysis.profile_respondents(df_clean, item_cols)

        # 異常回答パターン検出
        profile_df = bias_analysis.detect_anomaly_patterns(profile_df, config)

        # Z-score補正とZ-score(1-5)変換
        df_bias_adjusted = bias_analysis.apply_zscore_normalization(df_clean, item_cols)

        # CSV保存
        utils.save_dataframe(profile_df, "respondent_profile.csv", config)
        utils.save_dataframe(df_bias_adjusted, "bias_adjusted_scores.csv", config)

        logger.info(f"✓ バイアス分析完了: プロファイル {len(profile_df)}件")
        logger.info("✓ Z-score補正データを保存しました")

        # ==================================================
        # ステップ4: ベンダー総合評価
        # ==================================================
        logger.info("")
        logger.info("="*60)
        logger.info("ステップ4: ベンダー総合評価")
        logger.info("="*60)

        category_scores_df = vendor_evaluation.aggregate_by_category(df_bias_adjusted, config)
        weighted_scores_df = vendor_evaluation.calculate_weighted_scores(category_scores_df)
        final_scores_df = vendor_evaluation.calculate_composite_scores(df_bias_adjusted, config)

        utils.save_dataframe(category_scores_df, "category_scores.csv", config)
        utils.save_dataframe(weighted_scores_df, "weighted_scores.csv", config)
        utils.save_dataframe(final_scores_df, "final_scores.csv", config)

        logger.info("✓ ベンダー評価計算完了")

        # ==================================================
        # 詳細項目別ベンダースコア生成（heatmap用）
        # ==================================================
        detailed_scores_df = (
            df_bias_adjusted.groupby("vendor_id")[item_cols]
            .mean()
            .reset_index()
            .melt(id_vars="vendor_id", var_name="item", value_name="score")
        )
        utils.save_dataframe(detailed_scores_df, "detailed_scores.csv", config)

        logger.info("✓ 詳細項目別ベンダースコア生成（heatmap用）完了")

        # ==================================================
        # Positioning Map 用データ作成（全組み合わせ）
        # ==================================================
        logger.info("")
        logger.info("="*60)
        logger.info("Positioning Map 用データ作成（全組み合わせ）")
        logger.info("="*60)

        categories = ["performance", "technical", "business", "improvement"]
        respondent_counts = df_bias_adjusted.groupby("vendor_id")["respondent_id"].nunique()

        # 全ての組み合わせを生成（6パターン）
        category_combinations = list(combinations(categories, 2))
        
        positioning_data = {}

        for cat_x, cat_y in category_combinations:
            # Raw版（項目の単純平均）
            x_items = config["categories"][cat_x]["items"]
            y_items = config["categories"][cat_y]["items"]
            
            x_values = df_bias_adjusted.groupby("vendor_id")[x_items].mean().mean(axis=1)
            y_values = df_bias_adjusted.groupby("vendor_id")[y_items].mean().mean(axis=1)
            
            positioning_raw = pd.DataFrame({
                "vendor_id": x_values.index,
                "x": x_values.values,
                "y": y_values.values,
                "respondent_count": respondent_counts.values
            })
            
            # Weighted版（カテゴリ平均スコア）
            x_weighted = category_scores_df[category_scores_df["category"] == cat_x] \
                .groupby("vendor_id")["mean_score"].mean()
            y_weighted = category_scores_df[category_scores_df["category"] == cat_y] \
                .groupby("vendor_id")["mean_score"].mean()
            
            positioning_weighted = pd.DataFrame({
                "vendor_id": x_weighted.index,
                "x": x_weighted.values,
                "y": y_weighted.values,
                "respondent_count": respondent_counts.values
            })
            
            # データ保存
            key_raw = f"{cat_x}_{cat_y}_raw"
            key_weighted = f"{cat_x}_{cat_y}_weighted"
            
            positioning_data[key_raw] = positioning_raw
            positioning_data[key_weighted] = positioning_weighted
            
            utils.save_dataframe(positioning_raw, f"positioning_{key_raw}.csv", config)
            utils.save_dataframe(positioning_weighted, f"positioning_{key_weighted}.csv", config)
            
            logger.info(f"✓ {cat_x} × {cat_y} データ作成完了")

        logger.info("✓ 全Positioning Map用データ作成完了")

        # ==================================================
        # ステップ5: 統計的検定
        # ==================================================
        logger.info("")
        logger.info("="*60)
        logger.info("ステップ5: 統計的検定")
        logger.info("="*60)

        anova_res = statistical_tests.perform_anova(df_bias_adjusted, score_col="performance_incident_response_speed_z5")
        tukey_res = statistical_tests.perform_tukey_hsd(df_bias_adjusted, score_col="performance_incident_response_speed_z5")

        vendor_ids = [v["id"] for v in config["vendors"]]
        pairs = [(vendor_ids[i], vendor_ids[j]) for i in range(len(vendor_ids)) for j in range(i+1, len(vendor_ids))]
        effect_df = statistical_tests.calculate_effect_sizes(df_bias_adjusted, pairs, score_col="performance_incident_response_speed_z5")

        significance_df = statistical_tests.create_significance_table(anova_res, tukey_res, effect_df)

        utils.save_dataframe(significance_df, "significance_tests.csv", config)

        logger.info("✓ 統計検定完了")

        # ==================================================
        # ステップ6: セグメント分析
        # ==================================================
        logger.info("")
        logger.info("="*60)
        logger.info("ステップ6: セグメント分析")
        logger.info("="*60)

        # 6.1 評価者群別分析（ランキング付き）
        profile_df = segment_analysis.classify_respondents(profile_df, config)
        segment_group_scores = segment_analysis.analyze_by_respondent_group(df_bias_adjusted, profile_df, item_cols)
        logger.info("✓ 評価者群別分析完了")

        # 6.2 属性別分析（ランキング付き）
        segment_department = segment_analysis.analyze_by_attribute(df_bias_adjusted, "department", item_cols)
        segment_usage = segment_analysis.analyze_by_attribute(df_bias_adjusted, "usage_frequency", item_cols)
        segment_incident = segment_analysis.analyze_by_attribute(df_bias_adjusted, "incident_experience", item_cols)
        logger.info("✓ 属性別分析完了")

        # 6.3 業務部門 vs IT部門分析
        segment_business_it = segment_analysis.analyze_business_vs_it(df_bias_adjusted, item_cols)
        logger.info("✓ 業務部門 vs IT部門分析完了")

        # 6.4 結果の保存
        utils.save_dataframe(segment_group_scores, "segment_group_scores.csv", config)
        utils.save_dataframe(segment_department, "segment_department.csv", config)
        utils.save_dataframe(segment_usage, "segment_usage_frequency.csv", config)
        utils.save_dataframe(segment_incident, "segment_incident_experience.csv", config)
        utils.save_dataframe(segment_business_it, "segment_business_it.csv", config)

        # 6.5 セグメント統合ランキングデータ作成（Rank Flow Chart用）
        logger.info("✓ セグメント統合ランキングデータ作成中...")
        
        segment_integrated = segment_analysis.integrate_segment_rankings(
            segment_group_scores,
            segment_department,
            segment_usage,
            segment_incident,
            segment_business_it
        )
        utils.save_dataframe(segment_integrated, "segment_ranking_integrated.csv", config)
        logger.info("✓ セグメント統合ランキングデータ作成完了")

        # ==================================================
        # ステップ6-2: セグメント分析に対する統計検定（有意差の検証）
        # ==================================================
        logger.info("")
        logger.info("="*60)
        logger.info("ステップ6-2: セグメント分析に対する統計検定（有意差の検証）")
        logger.info("="*60)

        # セグメント間スコア差の統計検定
        test_department = segment_analysis.test_segment_score_differences(df_bias_adjusted, "department", item_cols)
        test_usage = segment_analysis.test_segment_score_differences(df_bias_adjusted, "usage_frequency", item_cols)
        test_incident = segment_analysis.test_segment_score_differences(df_bias_adjusted, "incident_experience", item_cols)
        
        logger.info(f"✓ 統計検定完了:")
        logger.info(f"  - 部門別: {test_department['interpretation']}")
        logger.info(f"  - 利用頻度別: {test_usage['interpretation']}")
        logger.info(f"  - インシデント経験別: {test_incident['interpretation']}")
        
        utils.save_test(test_department, "segment_test_department.json", config)
        utils.save_test(test_usage, "segment_test_usage.json", config)
        utils.save_test(test_incident, "segment_test_incident.json", config)

        logger.info("✓ セグメント分析完了")

        # ==================================================
        # ステップ7: 可視化
        # ==================================================
        logger.info("")
        logger.info("="*60)
        logger.info("ステップ7: 可視化")
        logger.info("="*60)

        # Radar chart - 総合評価
        visualization.plot_radar_chart(category_scores_df, config)

        # Radar chart - カテゴリ別詳細（4つ）
        categories = ["performance", "technical", "business", "improvement"]
        for category in categories:
            visualization.plot_category_radar_chart(df_bias_adjusted, category, config)
            logger.info(f"✓ {config['categories'][category]['name_ja']} レーダーチャート生成完了")

        # Heatmap: 要 detailed_scores 形式
        visualization.plot_heatmap(detailed_scores_df, config)

        # Boxplot - 従来版（補正後のみ）
        visualization.plot_boxplot_with_significance(df_bias_adjusted, significance_df, item_cols, config)

        # Boxplot - 補正前後比較（新規）
        visualization.plot_boxplot_comparison(df_clean, df_bias_adjusted, significance_df, item_cols, config)
        logger.info("✓ 箱ひげ図（補正前後比較）生成完了")

        # Z-score分布図（新規）
        visualization.plot_zscore_distribution(df_bias_adjusted, item_cols, config)
        logger.info("✓ Z-score分布図生成完了")

        # Rank Flow Chart（セグメント分析）
        visualization.plot_rank_flow_chart(segment_integrated, config)
        logger.info("✓ Rank Flow Chart生成完了")

        # Positioning maps（全組み合わせ）
        for cat_x, cat_y in category_combinations:
            key_raw = f"{cat_x}_{cat_y}_raw"
            key_weighted = f"{cat_x}_{cat_y}_weighted"
            
            # 軸ラベル名を取得
            x_label = config["categories"][cat_x]["name_ja"]
            y_label = config["categories"][cat_y]["name_ja"]
            
            # Raw版
            visualization.plot_positioning_map(
                positioning_data[key_raw], 
                config, 
                filename=f"positioning_{key_raw}.png",
                x_label=x_label,
                y_label=y_label
            )
            
            # Weighted版
            visualization.plot_positioning_map(
                positioning_data[key_weighted], 
                config, 
                filename=f"positioning_{key_weighted}.png",
                x_label=x_label,
                y_label=y_label
            )
            
            logger.info(f"✓ {x_label} × {y_label} マップ生成完了")

        logger.info("✓ 可視化完了")

        # ==================================================
        # ステップ8: レポート作成
        # ==================================================
        logger.info("")
        logger.info("="*60)
        logger.info("ステップ8: レポート作成")
        logger.info("="*60)

        # レポート生成時に全てのポジショニングマップのパスを渡す
        positioning_map_paths = {}
        for cat_x, cat_y in category_combinations:
            key_raw = f"{cat_x}_{cat_y}_raw"
            key_weighted = f"{cat_x}_{cat_y}_weighted"
            positioning_map_paths[key_raw] = f"output/figures/positioning_{key_raw}.png"
            positioning_map_paths[key_weighted] = f"output/figures/positioning_{key_weighted}.png"

        report_generator.generate_report(
            final_scores_df,
            category_scores_df,
            significance_df,
            config,
            config["output"]["reports_dir"],
            radar_path="output/figures/radar_chart.png",
            heatmap_path="output/figures/heatmap.png",
            boxplot_path="output/figures/boxplot_significance.png",
            positioning_map_paths=positioning_map_paths,
            rank_flow_chart_path="output/figures/rank_flow_chart.png"
        )

        logger.info("✓ レポート作成完了")

        # ==================================================
        # 処理終了
        # ==================================================
        logger.info("分析処理が正常に完了しました")

        return 0
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
        print(f"\nエラー: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())