"""
data_loaderモジュール

vendor-qbr-analysis.md 第3章「データ構造」に基づく実装
CSVファイルからデータを読み込み、スキーマ検証と基本統計を提供
"""

import pandas as pd
import numpy as np
import yaml
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path

logger = logging.getLogger('VendorQBR.data_loader')


def load_data(filepath: str, config: Dict[str, Any]) -> pd.DataFrame:
    """
    CSVファイルからデータを読み込む
    
    Args:
        filepath: CSVファイルのパス
        config: 設定辞書
        
    Returns:
        読み込んだDataFrame
        
    Raises:
        FileNotFoundError: ファイルが存在しない場合
        pd.errors.ParserError: CSVの解析に失敗した場合
    """
    logger.info(f"データ読み込み開始: {filepath}")
    
    # ファイルの存在確認
    if not Path(filepath).exists():
        raise FileNotFoundError(f"データファイルが見つかりません: {filepath}")
    
    try:
        # CSV読み込み（BOM付きUTF-8対応）
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        
        # 基本的なデータ型変換
        df = _convert_data_types(df)
        
        logger.info(f"データ読み込み完了: {len(df)} レコード")
        return df
        
    except pd.errors.ParserError as e:
        logger.error(f"CSVの解析に失敗しました: {e}")
        raise
    except Exception as e:
        logger.error(f"データ読み込み中にエラーが発生しました: {e}")
        raise


def _convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    基本的なデータ型変換
    
    Args:
        df: DataFrame
        
    Returns:
        データ型変換後のDataFrame
    """
    df = df.copy()
    
    # タイムスタンプをdatetime型に変換
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # boolean型の変換
    if 'incident_experience' in df.columns:
        df['incident_experience'] = df['incident_experience'].astype(bool)
    
    # ID系をintに変換
    for col in ['response_id', 'respondent_id']:
        if col in df.columns:
            df[col] = df[col].astype(int)
    
    # スコア列を数値型に変換
    score_columns = [col for col in df.columns if any(
        prefix in col for prefix in ['performance_', 'technical_', 'business_', 'improvement_']
    )]
    for col in score_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def load_schema(schema_path: str) -> Dict[str, Any]:
    """
    YAMLスキーマファイルを読み込む
    
    Args:
        schema_path: YAMLファイルのパス
        
    Returns:
        スキーマ辞書
    """
    logger.info(f"スキーマ読み込み: {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = yaml.safe_load(f)
    
    return schema


def validate_schema(df: pd.DataFrame, schema: Dict[str, Any], config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    YAMLスキーマに基づいてデータを検証
    
    Args:
        df: 検証対象のDataFrame
        schema: YAMLスキーマ
        config: 設定辞書
        
    Returns:
        (検証成功フラグ, エラーメッセージリスト)
    """
    logger.info("スキーマ検証開始")
    errors = []
    
    # スキーマ構造の確認（'table'/'fields'キーのどちらか）
    if 'table' in schema and 'fields' in schema['table']:
        fields = schema['table']['fields']
    elif 'fields' in schema:
        fields = schema['fields']
    else:
        logger.error("スキーマ構造が不正です")
        return False, ["スキーマファイルの構造が不正です"]
    
    # 1. 必須カラムの存在確認
    required_fields = [
        field['name'] for field in fields
        if field.get('required', False)
    ]
    
    missing_columns = set(required_fields) - set(df.columns)
    if missing_columns:
        error_msg = f"必須カラムが不足しています: {', '.join(missing_columns)}"
        errors.append(error_msg)
        logger.error(error_msg)
    
    # 2. データ型の確認
    for field in fields:
        field_name = field['name']
        if field_name not in df.columns:
            continue
        
        field_type = field['type']
        
        # integer型のチェック
        if field_type == 'integer':
            if not pd.api.types.is_integer_dtype(df[field_name]):
                # NaNを除いて整数かチェック
                non_null_values = df[field_name].dropna()
                if len(non_null_values) > 0:
                    if not all(non_null_values == non_null_values.astype(int)):
                        errors.append(f"{field_name}は整数型である必要があります")
        
        # datetime型のチェック
        elif field_type == 'datetime':
            if not pd.api.types.is_datetime64_any_dtype(df[field_name]):
                errors.append(f"{field_name}は日時型である必要があります")
        
        # boolean型のチェック
        elif field_type == 'boolean':
            if not pd.api.types.is_bool_dtype(df[field_name]):
                errors.append(f"{field_name}はboolean型である必要があります")
    
    # 3. 値の範囲チェック（スコア: 1-5）
    score_min = config['cleansing']['score_min']
    score_max = config['cleansing']['score_max']
    
    score_columns = [col for col in df.columns if any(
        prefix in col for prefix in ['performance_', 'technical_', 'business_', 'improvement_']
    )]
    
    for col in score_columns:
        if col in df.columns:
            valid_scores = df[col].dropna()
            if len(valid_scores) > 0:
                out_of_range = valid_scores[(valid_scores < score_min) | (valid_scores > score_max)]
                if len(out_of_range) > 0:
                    error_msg = f"{col}に範囲外の値があります（{score_min}-{score_max}の範囲外）: {len(out_of_range)}件"
                    errors.append(error_msg)
                    logger.warning(error_msg)
    
    # 4. ベンダーIDの整合性チェック
    if 'enums' in schema and 'vendorId' in schema['enums']:
        vendor_ids = schema['enums']['vendorId']['values']
        valid_vendor_ids = [v['id'] for v in vendor_ids]
        
        if 'vendor_id' in df.columns:
            invalid_vendors = df[~df['vendor_id'].isin(valid_vendor_ids)]['vendor_id'].unique()
            if len(invalid_vendors) > 0:
                error_msg = f"無効なベンダーIDが含まれています: {', '.join(map(str, invalid_vendors))}"
                errors.append(error_msg)
                logger.error(error_msg)
    
    # 検証結果のログ出力
    if errors:
        logger.warning(f"スキーマ検証で{len(errors)}件の問題が見つかりました")
        for error in errors:
            logger.warning(f"  - {error}")
        return False, errors
    else:
        logger.info("スキーマ検証完了: 問題なし")
        return True, []


def get_basic_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    基本統計情報を取得
    
    Args:
        df: DataFrame
        
    Returns:
        基本統計情報の辞書
    """
    logger.info("基本統計情報を計算中")
    
    stats = {
        'n_records': len(df),
        'n_respondents': df['respondent_id'].nunique(),
        'n_vendors': df['vendor_id'].nunique(),
        'date_range': {
            'start': df['timestamp'].min().strftime('%Y-%m-%d') if pd.notna(df['timestamp'].min()) else None,
            'end': df['timestamp'].max().strftime('%Y-%m-%d') if pd.notna(df['timestamp'].max()) else None
        },
        'vendor_distribution': df['vendor_id'].value_counts().to_dict(),
        'department_distribution': df['department_ja'].value_counts().to_dict(),
        'role_distribution': df['role_ja'].value_counts().to_dict(),
        'usage_frequency_distribution': df['usage_frequency_ja'].value_counts().to_dict(),
        'incident_experience_rate': (df['incident_experience'].sum() / len(df) * 100) if 'incident_experience' in df.columns else None
    }
    
    # 欠損値の割合
    score_columns = [col for col in df.columns if any(
        prefix in col for prefix in ['performance_', 'technical_', 'business_', 'improvement_']
    )]
    
    if score_columns:
        missing_rate = df[score_columns].isnull().sum().sum() / (len(df) * len(score_columns)) * 100
        stats['missing_rate_percent'] = round(missing_rate, 2)
    
    return stats


def display_data_summary(df: pd.DataFrame, stats: Dict[str, Any]) -> None:
    """
    データサマリーを表示
    
    Args:
        df: DataFrame
        stats: 基本統計情報
    """
    print("\n" + "="*60)
    print("データ読み込みサマリー")
    print("="*60)
    print(f"総レコード数: {stats['n_records']:,}")
    print(f"回答者数: {stats['n_respondents']:,}")
    print(f"評価対象ベンダー数: {stats['n_vendors']}")
    print(f"期間: {stats['date_range']['start']} 〜 {stats['date_range']['end']}")
    print(f"欠損値率: {stats.get('missing_rate_percent', 0):.2f}%")
    
    if stats.get('incident_experience_rate') is not None:
        print(f"インシデント経験率: {stats['incident_experience_rate']:.1f}%")
    
    print("\nベンダー別回答数:")
    for vendor_id, count in sorted(stats['vendor_distribution'].items()):
        print(f"  {vendor_id}: {count:,}件")
    
    print("\n部門別回答数:")
    for dept, count in sorted(stats['department_distribution'].items(), key=lambda x: -x[1])[:5]:
        print(f"  {dept}: {count:,}件")
    
    print("\n利用頻度別:")
    for freq, count in stats['usage_frequency_distribution'].items():
        print(f"  {freq}: {count:,}件")
    
    print("="*60 + "\n")


def validate_and_load(config: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    データを読み込み、検証し、統計情報と共に返す
    
    Args:
        config: 設定辞書
        
    Returns:
        (DataFrame, 統計情報辞書)
    """
    # データ読み込み
    df = load_data(config['data']['input_csv'], config)
    
    # スキーマ読み込みと検証
    schema = load_schema(config['data']['schema_yaml'])
    is_valid, errors = validate_schema(df, schema, config)
    
    if not is_valid:
        logger.warning("スキーマ検証でエラーが見つかりましたが、処理を続行します")
    
    # 基本統計
    stats = get_basic_statistics(df)
    
    # サマリー表示
    display_data_summary(df, stats)
    
    return df, stats