"""
セグメント分析モジュール
vendor-qbr-analysis.md 第5.5章対応

更新内容:
- ベンダーランキング算出機能を追加
- 業務部門 vs IT部門の分類分析を追加
- セグメント間スコア差の統計検定を追加（Kruskal-Wallis検定）
- perform_chi_square_test() を削除（データ構造と検定の前提条件が不適合のため）
"""

import pandas as pd
import numpy as np

from typing import Dict, List
from scipy.stats import kruskal


def classify_respondents(profile_df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    回答者分類:
      - 厳格評価者: 平均スコア < 3.0
      - 標準評価者: 3.0–4.0
      - 寛容評価者: >4.0
    """
    strict_max = config["respondent_classification"]["strict"]["max_avg"]
    standard_min = config["respondent_classification"]["standard"]["min_avg"]
    standard_max = config["respondent_classification"]["standard"]["max_avg"]

    def classify(row):
        if row["avg_score"] < strict_max:
            return "strict"
        elif standard_min <= row["avg_score"] <= standard_max:
            return "standard"
        else:
            return "lenient"

    profile_df["respondent_group"] = profile_df.apply(classify, axis=1)
    return profile_df


def analyze_by_respondent_group(df: pd.DataFrame, profile_df: pd.DataFrame, item_cols: List[str]) -> pd.DataFrame:
    """
    評価者群別ベンダー比較（ランキング付き）
    
    Returns:
        DataFrame: respondent_group, vendor_id, avg_score, rank を含むデータフレーム
    """
    df = df.merge(profile_df[["respondent_id", "respondent_group"]], on="respondent_id", how="left")
    group_scores = (
        df.groupby(["respondent_group", "vendor_id"])[item_cols]
        .mean()
        .mean(axis=1)
        .reset_index(name="avg_score")
    )
    
    # 各評価者群内でのベンダーランキングを算出（降順、同スコアは同順位）
    group_scores["rank"] = group_scores.groupby("respondent_group")["avg_score"].rank(
        ascending=False, method="dense"
    ).astype(int)
    
    # 並び替え（評価者群、ランク順）
    group_scores = group_scores.sort_values(["respondent_group", "rank"])
    
    return group_scores


def analyze_by_attribute(df: pd.DataFrame, attribute: str, item_cols: List[str]) -> pd.DataFrame:
    """
    属性別スコア比較（ランキング付き）
    
    Args:
        df: 評価データフレーム
        attribute: 分析する属性列名 (department / usage_frequency / incident_experience)
        item_cols: 評価項目列のリスト
        
    Returns:
        DataFrame: attribute, vendor_id, avg_score, rank を含むデータフレーム
    """
    results = (
        df.groupby([attribute, "vendor_id"])[item_cols]
        .mean()
        .mean(axis=1)
        .reset_index(name="avg_score")
    )
    
    # 各属性値内でのベンダーランキングを算出
    results["rank"] = results.groupby(attribute)["avg_score"].rank(
        ascending=False, method="dense"
    ).astype(int)
    
    # 並び替え（属性、ランク順）
    results = results.sort_values([attribute, "rank"])
    
    return results


def analyze_business_vs_it(df: pd.DataFrame, item_cols: List[str]) -> pd.DataFrame:
    """
    業務部門 vs IT部門の比較分析（ランキング付き）
    
    部門を以下の2つのカテゴリに分類:
    - 業務部門: business, finance, hr, logistics
    - IT部門: it
    
    Args:
        df: 評価データフレーム（department列を含む）
        item_cols: 評価項目列のリスト
        
    Returns:
        DataFrame: dept_category, vendor_id, avg_score, rank を含むデータフレーム
    """
    # 部門分類のマッピング
    dept_mapping = {
        "it": "IT部門",
        "business": "業務部門",
        "finance": "業務部門",
        "hr": "業務部門",
        "sales": "営業部門",
        "logistics": "業務部門"
    }
    
    # 新しい列を作成（元データは変更しない）
    df = df.copy()
    df["dept_category"] = df["department"].map(dept_mapping)
    
    # 欠損値チェック（未知の部門がある場合）
    if df["dept_category"].isna().any():
        unknown_depts = df[df["dept_category"].isna()]["department"].unique()
        print(f"警告: 未定義の部門が見つかりました: {unknown_depts}")
        df = df.dropna(subset=["dept_category"])
    
    # 部門カテゴリ別にベンダースコアを集計
    results = (
        df.groupby(["dept_category", "vendor_id"])[item_cols]
        .mean()
        .mean(axis=1)
        .reset_index(name="avg_score")
    )
    
    # 各部門カテゴリ内でのベンダーランキングを算出
    results["rank"] = results.groupby("dept_category")["avg_score"].rank(
        ascending=False, method="dense"
    ).astype(int)
    
    # 並び替え（部門カテゴリ、ランク順）
    results = results.sort_values(["dept_category", "rank"])
    
    return results

def test_segment_score_differences(df: pd.DataFrame, attribute: str, item_cols: List[str]) -> Dict:
    df = df.copy()
    df["overall_score"] = df[item_cols].mean(axis=1)

    segments = df[attribute].unique()
    segment_scores = [df[df[attribute] == seg]["overall_score"].values for seg in segments]

    statistic, p_value = kruskal(*segment_scores)

    segment_stats = []
    for seg in segments:
        seg_scores = df[df[attribute] == seg]["overall_score"]
        segment_stats.append({
            "segment": str(seg),
            "n": len(seg_scores),
            "mean": float(seg_scores.mean()),
            "median": float(seg_scores.median()),
            "std": float(seg_scores.std())
        })

    # numpy.bool_ → Python bool に変換
    segments_converted = [
        bool(seg) if isinstance(seg, (np.bool_,)) else seg
        for seg in segments
    ]

    return {
        "attribute": attribute,
        "test": "Kruskal-Wallis",
        "statistic": float(statistic),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05),
        "alpha": 0.05,
        "n_segments": len(segments),
        "segments": segments_converted,
        "segment_stats": segment_stats,
        "interpretation": (
            f"セグメント間に有意な差が{'あります' if p_value < 0.05 else 'ありません'} "
            f"(p={p_value:.4f}, α=0.05)"
        )
    }


def integrate_segment_rankings(
    segment_group_scores: pd.DataFrame,
    segment_department: pd.DataFrame,
    segment_usage: pd.DataFrame,
    segment_incident: pd.DataFrame,
    segment_business_it: pd.DataFrame
) -> pd.DataFrame:
    """
    5つのセグメント分析結果を統合してRank Flow Chart用のデータフレームを作成
    
    Args:
        segment_group_scores: 評価者群別スコア
        segment_department: 部門別スコア
        segment_usage: 利用頻度別スコア
        segment_incident: インシデント経験別スコア
        segment_business_it: 業務部門vsIT部門スコア
        
    Returns:
        DataFrame: category, axis, vendor_id, rank を含む統合データフレーム
                  categoryはセグメント分類の種類
                  axisは各セグメント内の具体的な値
    """
    integrated_data = []
    
    # 1. 評価者群別（respondent_group）
    for _, row in segment_group_scores.iterrows():
        integrated_data.append({
            "category": "評価者群",
            "axis": row["respondent_group"],
            "vendor_id": row["vendor_id"],
            "rank": row["rank"],
            "avg_score": row["avg_score"]
        })
    
    # 2. 部門別（department）
    for _, row in segment_department.iterrows():
        integrated_data.append({
            "category": "部門",
            "axis": row["department"],
            "vendor_id": row["vendor_id"],
            "rank": row["rank"],
            "avg_score": row["avg_score"]
        })
    
    # 3. 利用頻度別（usage_frequency）
    for _, row in segment_usage.iterrows():
        integrated_data.append({
            "category": "利用頻度",
            "axis": row["usage_frequency"],
            "vendor_id": row["vendor_id"],
            "rank": row["rank"],
            "avg_score": row["avg_score"]
        })
    
    # 4. インシデント経験別（incident_experience）
    for _, row in segment_incident.iterrows():
        integrated_data.append({
            "category": "インシデント経験",
            "axis": row["incident_experience"],
            "vendor_id": row["vendor_id"],
            "rank": row["rank"],
            "avg_score": row["avg_score"]
        })
    
    # 5. 業務部門vsIT部門（dept_category）
    for _, row in segment_business_it.iterrows():
        integrated_data.append({
            "category": "部門分類",
            "axis": row["dept_category"],
            "vendor_id": row["vendor_id"],
            "rank": row["rank"],
            "avg_score": row["avg_score"]
        })
    
    result_df = pd.DataFrame(integrated_data)
    
    # axis列を保持順に並べるための順序定義
    axis_order = {
        # 評価者群
        "strict": 1,
        "standard": 2,
        "lenient": 3,
        # 部門
        "it": 10,
        "business": 11,
        "finance": 12,
        "hr": 13,
        "sales": 14,
        "logistics": 15,
        # 利用頻度
        "daily": 20,
        "weekly": 21,
        "monthly": 22,
        "rarely": 23,
        # インシデント経験（Trueが先）
        True: 30,
        False: 31,
        # 部門分類
        "IT部門": 40,
        "業務部門": 41,
        "営業部門": 42
    }
    
    # 順序列を追加（存在しないキーは99にする）
    result_df["axis_order"] = result_df["axis"].map(
        lambda x: axis_order.get(x, 99)
    )
    
    # category順序も定義
    category_order = {
        "評価者群": 1,
        "部門": 2,
        "利用頻度": 3,
        "インシデント経験": 4,
        "部門分類": 5
    }
    result_df["category_order"] = result_df["category"].map(category_order)
    
    # 並び替え
    result_df = result_df.sort_values(["category_order", "axis_order"])
    
    # 作業用カラムを削除
    result_df = result_df.drop(columns=["axis_order", "category_order"])
    
    return result_df