"""
統計的検定モジュール
vendor-qbr-analysis.md 第5.4章対応
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def perform_anova(df: pd.DataFrame, score_col: str) -> Dict:
    """
    一元配置分散分析（ANOVA）
    H0: 全ベンダーの平均スコアは等しい
    """
    vendor_groups = [group[score_col].values for _, group in df.groupby("vendor_id")]
    f_stat, p_value = stats.f_oneway(*vendor_groups)

    return {"F": f_stat, "p_value": p_value}


def perform_tukey_hsd(df: pd.DataFrame, score_col: str) -> pd.DataFrame:
    """
    多重比較検定（Tukey HSD）
    """
    tukey = pairwise_tukeyhsd(
        endog=df[score_col],      # 比較対象データ
        groups=df["vendor_id"],   # グループ（ベンダー）
        alpha=0.05
    )
    return pd.DataFrame(data=tukey.summary().data[1:], columns=tukey.summary().data[0])


def calculate_effect_sizes(df: pd.DataFrame, vendor_pairs: List[Tuple[str, str]], score_col: str) -> pd.DataFrame:
    """
    Cohen's d による効果量算出
    """
    results = []

    for v1, v2 in vendor_pairs:
        g1 = df[df["vendor_id"] == v1][score_col].values
        g2 = df[df["vendor_id"] == v2][score_col].values
        
        pooled_std = np.sqrt(((np.std(g1, ddof=1) ** 2) + (np.std(g2, ddof=1) ** 2)) / 2)
        d = (np.mean(g1) - np.mean(g2)) / pooled_std

        results.append({"pair": f"{v1} vs {v2}", "effect_size_d": d})

    return pd.DataFrame(results)

def create_significance_table(anova_result: Dict, tukey_df: pd.DataFrame, effect_df: pd.DataFrame) -> pd.DataFrame:
    """
    ANOVA + Tukey + 効果量 の統合サマリーテーブル
    """
    result = tukey_df.copy()

    # Tukeyのペア表記を pair として生成
    result["pair"] = result["group1"] + " vs " + result["group2"]

    # 効果量と結合
    result = result.merge(effect_df, on="pair", how="left")

    # ANOVAの p値を先頭列に追加
    result.insert(0, "anova_p_value", anova_result["p_value"])

    return result
