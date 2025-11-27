"""
data_cleansingモジュール

vendor-qbr-analysis.md 第4章「データクレンジング」に基づく実装
無効な回答の除外、欠損値処理、データ品質検証を提供
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime

logger = logging.getLogger('VendorQBR.data_cleansing')


def get_score_columns(df: pd.DataFrame) -> List[str]:
    """
    スコア列を取得
    
    Args:
        df: DataFrame
        
    Returns:
        スコア列名のリスト
    """
    return [col for col in df.columns if any(
        prefix in col for prefix in ['performance_', 'technical_', 'business_', 'improvement_']
    )]


def check_all_same_score(row: pd.Series, item_cols: List[str]) -> bool:
    """
    全項目が同じスコアかチェック
    
    Args:
        row: データ行
        item_cols: チェック対象の列名リスト
        
    Returns:
        すべて同一スコアの場合True
    """
    scores = row[item_cols].dropna()
    
    # 有効なスコアが0または1つの場合はチェック不要
    if len(scores) <= 1:
        return False
    
    # すべてのスコアが同一かチェック
    return scores.nunique() == 1


def check_single_vendor_evaluation(respondent_id: int, df: pd.DataFrame) -> bool:
    """
    回答者が1社のみを評価しているかチェック
    
    Args:
        respondent_id: 回答者ID
        df: DataFrame
        
    Returns:
        1社のみ評価の場合True
    """
    respondent_data = df[df['respondent_id'] == respondent_id]
    n_vendors = respondent_data['vendor_id'].nunique()
    return n_vendors <= 1


def calculate_missing_rate(row: pd.Series, item_cols: List[str]) -> float:
    """
    未回答率を計算
    
    Args:
        row: データ行
        item_cols: チェック対象の列名リスト
        
    Returns:
        未回答率（0.0-1.0）
    """
    total = len(item_cols)
    missing = row[item_cols].isnull().sum()
    return missing / total if total > 0 else 0.0


def calculate_std_dev(row: pd.Series, item_cols: List[str]) -> float:
    """
    標準偏差を計算
    
    Args:
        row: データ行
        item_cols: チェック対象の列名リスト
        
    Returns:
        標準偏差
    """
    scores = row[item_cols].dropna()
    if len(scores) <= 1:
        return 0.0
    return scores.std()


def exclude_invalid_responses(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    除外基準に基づいて無効な回答を除外
    
    Args:
        df: DataFrame
        config: 設定辞書
        
    Returns:
        (クリーニング済みDataFrame, 除外統計辞書)
    """
    logger.info("無効な回答の除外を開始")
    
    df_clean = df.copy()
    initial_count = len(df_clean)
    
    # 除外統計
    exclusion_stats = {
        'initial_count': initial_count,
        'all_same_score': 0,
        'single_vendor': 0,
        'high_missing_rate': 0,
        'zero_std_dev': 0,
        'final_count': 0
    }
    
    # スコア列を取得
    score_columns = get_score_columns(df_clean)
    
    cleansing_config = config['cleansing']
    
    # 除外フラグを初期化
    exclude_mask = pd.Series([False] * len(df_clean), index=df_clean.index)
    
    # 1. すべて同一評価の除外
    if cleansing_config.get('exclude_all_same_score', True):
        same_score_mask = df_clean.apply(
            lambda row: check_all_same_score(row, score_columns), 
            axis=1
        )
        exclusion_stats['all_same_score'] = same_score_mask.sum()
        exclude_mask |= same_score_mask
        logger.info(f"すべて同一スコア: {exclusion_stats['all_same_score']}件除外")
    
    # 2. 評価ベンダー数不足（1社のみ）の除外
    if cleansing_config.get('exclude_single_vendor', True):
        single_vendor_mask = df_clean['respondent_id'].apply(
            lambda rid: check_single_vendor_evaluation(rid, df_clean)
        )
        exclusion_stats['single_vendor'] = single_vendor_mask.sum()
        exclude_mask |= single_vendor_mask
        logger.info(f"単一ベンダー評価: {exclusion_stats['single_vendor']}件除外")
    
    # 3. 未回答率が閾値以上の除外
    missing_threshold = cleansing_config.get('missing_threshold', 0.5)
    missing_rates = df_clean.apply(
        lambda row: calculate_missing_rate(row, score_columns),
        axis=1
    )
    high_missing_mask = missing_rates >= missing_threshold
    exclusion_stats['high_missing_rate'] = high_missing_mask.sum()
    exclude_mask |= high_missing_mask
    logger.info(f"未回答率{missing_threshold*100}%以上: {exclusion_stats['high_missing_rate']}件除外")
    
    # 4. 標準偏差が閾値以下（0）の除外
    min_std_dev = cleansing_config.get('min_std_dev', 0.0)
    std_devs = df_clean.apply(
        lambda row: calculate_std_dev(row, score_columns),
        axis=1
    )
    zero_std_mask = std_devs <= min_std_dev
    exclusion_stats['zero_std_dev'] = zero_std_mask.sum()
    exclude_mask |= zero_std_mask
    logger.info(f"標準偏差{min_std_dev}以下: {exclusion_stats['zero_std_dev']}件除外")
    
    # 除外実行
    df_clean = df_clean[~exclude_mask].copy()
    exclusion_stats['final_count'] = len(df_clean)
    
    excluded_count = initial_count - exclusion_stats['final_count']
    logger.info(f"除外完了: {excluded_count}件除外、{exclusion_stats['final_count']}件残存")
    
    return df_clean, exclusion_stats


def get_category_columns(config: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    カテゴリごとの列名を取得
    
    Args:
        config: 設定辞書
        
    Returns:
        カテゴリ名をキー、列名リストを値とする辞書
    """
    categories = config.get('categories', {})
    return {
        category: info['items']
        for category, info in categories.items()
    }


def handle_missing_values(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    欠損値処理
    
    Args:
        df: DataFrame
        config: 設定辞書
        
    Returns:
        (欠損値処理済みDataFrame, 処理統計辞書)
    """
    logger.info("欠損値処理を開始")
    
    df_filled = df.copy()
    fill_method = config['cleansing'].get('fill_method', 'category_mean')
    
    # 処理統計
    stats = {
        'initial_missing': 0,
        'filled_by_category_mean': 0,
        'remaining_missing': 0,
        'method': fill_method
    }
    
    # スコア列を取得
    score_columns = get_score_columns(df_filled)
    
    # 初期欠損数
    stats['initial_missing'] = df_filled[score_columns].isnull().sum().sum()
    logger.info(f"初期欠損数: {stats['initial_missing']}件")
    
    if fill_method == 'category_mean':
        # カテゴリごとの列名を取得
        category_columns = get_category_columns(config)
        
        # カテゴリごとに欠損値を補完
        for category, cols in category_columns.items():
            # このカテゴリの列が存在するか確認
            existing_cols = [col for col in cols if col in df_filled.columns]
            if not existing_cols:
                continue
            
            # 各行について、カテゴリ内の平均で補完
            for idx in df_filled.index:
                row_data = df_filled.loc[idx, existing_cols]
                missing_mask = row_data.isnull()
                
                if missing_mask.any():
                    # カテゴリ内の他項目の平均を計算
                    valid_scores = row_data[~missing_mask]
                    
                    if len(valid_scores) > 0:
                        mean_score = valid_scores.mean()
                        # 欠損値を平均で補完
                        df_filled.loc[idx, row_data[missing_mask].index] = mean_score
                        stats['filled_by_category_mean'] += missing_mask.sum()
        
        logger.info(f"カテゴリ内平均で補完: {stats['filled_by_category_mean']}件")
    
    elif fill_method == 'respondent_mean':
        # 回答者ごとの平均で補完
        for idx in df_filled.index:
            row_data = df_filled.loc[idx, score_columns]
            missing_mask = row_data.isnull()
            
            if missing_mask.any():
                valid_scores = row_data[~missing_mask]
                
                if len(valid_scores) > 0:
                    mean_score = valid_scores.mean()
                    df_filled.loc[idx, row_data[missing_mask].index] = mean_score
                    stats['filled_by_category_mean'] += missing_mask.sum()
    
    elif fill_method == 'drop':
        # 欠損値を含む行を削除
        df_filled = df_filled.dropna(subset=score_columns)
        logger.info(f"欠損値を含む行を削除: {len(df) - len(df_filled)}行")
    
    # 残存欠損数
    stats['remaining_missing'] = df_filled[score_columns].isnull().sum().sum()
    logger.info(f"欠損値処理完了: 残存欠損数 {stats['remaining_missing']}件")
    
    return df_filled, stats


def validate_data_quality(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    データ品質検証
    
    Args:
        df: DataFrame
        config: 設定辞書
        
    Returns:
        検証結果辞書
    """
    logger.info("データ品質検証を開始")
    
    validation_results = {
        'total_records': len(df),
        'issues': []
    }
    
    # 1. スコア範囲チェック（1-5）
    score_min = config['cleansing']['score_min']
    score_max = config['cleansing']['score_max']
    score_columns = get_score_columns(df)
    
    out_of_range_count = 0
    for col in score_columns:
        valid_scores = df[col].dropna()
        out_of_range = valid_scores[(valid_scores < score_min) | (valid_scores > score_max)]
        if len(out_of_range) > 0:
            out_of_range_count += len(out_of_range)
            validation_results['issues'].append({
                'type': 'score_out_of_range',
                'column': col,
                'count': len(out_of_range),
                'details': f"{score_min}-{score_max}の範囲外"
            })
    
    if out_of_range_count == 0:
        logger.info("✓ スコア範囲チェック: 問題なし")
    else:
        logger.warning(f"スコア範囲外: {out_of_range_count}件")
    
    validation_results['score_out_of_range_count'] = out_of_range_count
    
    # 2. ベンダーIDの整合性チェック
    valid_vendor_ids = [v['id'] for v in config['vendors']]
    invalid_vendors = df[~df['vendor_id'].isin(valid_vendor_ids)]['vendor_id'].unique()
    
    if len(invalid_vendors) > 0:
        validation_results['issues'].append({
            'type': 'invalid_vendor_id',
            'count': len(invalid_vendors),
            'details': f"無効なベンダーID: {', '.join(map(str, invalid_vendors))}"
        })
        logger.warning(f"無効なベンダーID: {len(invalid_vendors)}種類")
    else:
        logger.info("✓ ベンダーID整合性: 問題なし")
    
    validation_results['invalid_vendor_count'] = len(invalid_vendors)
    
    # 3. 回答者IDの重複チェック（同一ベンダーへの複数回答）
    duplicates = df.groupby(['respondent_id', 'vendor_id']).size()
    duplicate_count = (duplicates > 1).sum()
    
    if duplicate_count > 0:
        validation_results['issues'].append({
            'type': 'duplicate_response',
            'count': duplicate_count,
            'details': '同一回答者・ベンダーの重複'
        })
        logger.warning(f"重複回答: {duplicate_count}件")
    else:
        logger.info("✓ 回答者ID重複チェック: 問題なし")
    
    validation_results['duplicate_response_count'] = duplicate_count
    
    # 4. タイムスタンプの妥当性チェック
    if 'timestamp' in df.columns:
        # 未来の日付チェック
        now = pd.Timestamp.now()
        future_dates = df[df['timestamp'] > now]
        
        if len(future_dates) > 0:
            validation_results['issues'].append({
                'type': 'future_timestamp',
                'count': len(future_dates),
                'details': '未来の日付'
            })
            logger.warning(f"未来の日付: {len(future_dates)}件")
        else:
            logger.info("✓ タイムスタンプ妥当性: 問題なし")
        
        validation_results['future_timestamp_count'] = len(future_dates)
        
        # NaT（無効な日付）チェック
        nat_count = df['timestamp'].isna().sum()
        if nat_count > 0:
            validation_results['issues'].append({
                'type': 'invalid_timestamp',
                'count': nat_count,
                'details': '無効な日付形式'
            })
            logger.warning(f"無効な日付: {nat_count}件")
        
        validation_results['invalid_timestamp_count'] = nat_count
    
    # サマリー
    validation_results['total_issues'] = len(validation_results['issues'])
    validation_results['is_valid'] = validation_results['total_issues'] == 0
    
    if validation_results['is_valid']:
        logger.info("✓ データ品質検証完了: すべて正常")
    else:
        logger.warning(f"データ品質検証完了: {validation_results['total_issues']}種類の問題を検出")
    
    return validation_results


def cleanse_data(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    データクレンジングの統合関数
    
    Args:
        df: DataFrame
        config: 設定辞書
        
    Returns:
        (クレンジング済みDataFrame, 統計情報辞書)
    """
    logger.info("="*60)
    logger.info("データクレンジング開始")
    logger.info("="*60)
    
    results = {
        'initial_count': len(df)
    }
    
    # 1. 無効な回答を除外
    df_clean, exclusion_stats = exclude_invalid_responses(df, config)
    results['exclusion'] = exclusion_stats
    
    # 2. 欠損値処理
    df_clean, missing_stats = handle_missing_values(df_clean, config)
    results['missing_values'] = missing_stats
    
    # 3. データ品質検証
    validation_results = validate_data_quality(df_clean, config)
    results['validation'] = validation_results
    
    results['final_count'] = len(df_clean)
    results['total_excluded'] = results['initial_count'] - results['final_count']
    results['exclusion_rate'] = results['total_excluded'] / results['initial_count'] * 100
    
    logger.info("="*60)
    logger.info(f"データクレンジング完了")
    logger.info(f"初期レコード数: {results['initial_count']}")
    logger.info(f"最終レコード数: {results['final_count']}")
    logger.info(f"除外レコード数: {results['total_excluded']} ({results['exclusion_rate']:.1f}%)")
    logger.info("="*60)
    
    return df_clean, results


def display_cleansing_summary(results: Dict[str, Any]) -> None:
    """
    クレンジング結果のサマリーを表示
    
    Args:
        results: クレンジング結果辞書
    """
    print("\n" + "="*60)
    print("データクレンジング結果サマリー")
    print("="*60)
    print(f"初期レコード数: {results['initial_count']:,}")
    print(f"最終レコード数: {results['final_count']:,}")
    print(f"除外レコード数: {results['total_excluded']:,} ({results['exclusion_rate']:.1f}%)")
    
    print("\n【除外内訳】")
    excl = results['exclusion']
    print(f"  すべて同一スコア: {excl['all_same_score']:,}件")
    print(f"  単一ベンダー評価: {excl['single_vendor']:,}件")
    print(f"  高未回答率: {excl['high_missing_rate']:,}件")
    print(f"  標準偏差ゼロ: {excl['zero_std_dev']:,}件")
    
    print("\n【欠損値処理】")
    missing = results['missing_values']
    print(f"  初期欠損数: {missing['initial_missing']:,}件")
    print(f"  補完数: {missing['filled_by_category_mean']:,}件")
    print(f"  残存欠損数: {missing['remaining_missing']:,}件")
    print(f"  処理方法: {missing['method']}")
    
    print("\n【データ品質検証】")
    validation = results['validation']
    if validation['is_valid']:
        print("  ✓ すべての検証項目をクリア")
    else:
        print(f"  ⚠ {validation['total_issues']}種類の問題を検出")
        for issue in validation['issues']:
            print(f"    - {issue['type']}: {issue['count']}件 ({issue['details']})")
    
    print("="*60 + "\n")