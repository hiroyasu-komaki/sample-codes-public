"""
ベンダー総合評価モジュール
vendor-qbr-analysis.md 第5.3章対応
"""

import pandas as pd
import numpy as np
from typing import Dict, List


def aggregate_by_category(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    大分類レベルの集計（平均、標準偏差、95%信頼区間）
    """
    results = []

    for cat_key, cat_info in config["categories"].items():
        items = cat_info["items"]

        for vendor in config["vendors"]:
            vendor_id = vendor["id"]
            df_vendor = df[df["vendor_id"] == vendor_id]

            if len(df_vendor) == 0:
                continue

            mean_val = df_vendor[items].mean().mean()
            std_val = df_vendor[items].stack().std()
            n = len(df_vendor)

            ci95 = 1.96 * (std_val / np.sqrt(n))

            results.append({
                "vendor_id": vendor_id,
                "category": cat_key,
                "category_ja": cat_info["name_ja"],
                "mean_score": mean_val,
                "std": std_val,
                "n": n,
                "ci95_low": mean_val - ci95,
                "ci95_high": mean_val + ci95,
                "weighted": mean_val * cat_info["weight"]
            })

    return pd.DataFrame(results)


def calculate_weighted_scores(category_scores: pd.DataFrame) -> pd.DataFrame:
    """
    重み付け総合スコアの計算
    """
    weighted_scores = (
        category_scores.groupby("vendor_id")["weighted"].sum().reset_index()
        .rename(columns={"weighted": "weighted_score"})
    )
    return weighted_scores


def calculate_reliability_coefficient(n_respondents: int, threshold: int = 20) -> float:
    """
    信頼性係数
    係数 = min(1.0, sqrt(n / threshold))
    """
    return min(1.0, np.sqrt(n_respondents / threshold))


def calculate_composite_scores(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    複合評価スコアの計算
    最終評価スコア = z * 0.5 + rank * 0.3 + raw * 0.2
    """

    # 生スコア平均
    raw_scores = df.groupby("vendor_id")[config["categories"]["performance"]["items"]
                                           + config["categories"]["technical"]["items"]
                                           + config["categories"]["business"]["items"]
                                           + config["categories"]["improvement"]["items"]].mean().mean(axis=1)

    # Z-score(1-5換算)平均
    z_scores = df.groupby("vendor_id")[[c for c in df.columns if c.endswith("_z5")]].mean().mean(axis=1)

    # 順位スコア（小さい方が上位）
    rank_scores = z_scores.rank(ascending=False)

    # 複合スコア計算
    composite = (
        z_scores * config["correction"]["composite_weights"]["zscore"]
        + rank_scores * config["correction"]["composite_weights"]["rank"] * -1
        + raw_scores * config["correction"]["composite_weights"]["raw"]
    )

    result = pd.DataFrame({
        "vendor_id": composite.index,
        "raw_score": raw_scores.values,
        "z_avg_score": z_scores.values,
        "rank": rank_scores.values,
        "composite_score": composite.values
    }).reset_index(drop=True)

    # 信頼性係数適用
    respondent_counts = df.groupby("vendor_id")["respondent_id"].nunique()
    result["reliability_coef"] = respondent_counts.apply(
        lambda x: calculate_reliability_coefficient(x, config["correction"]["reliability"]["threshold"])
    )

    result["final_score"] = result["composite_score"] * result["reliability_coef"]

    return result.sort_values("final_score", ascending=False)
