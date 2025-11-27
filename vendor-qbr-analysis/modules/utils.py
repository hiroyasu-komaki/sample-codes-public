"""
ユーティリティ関数モジュール
"""

import os
import yaml
import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import json


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """設定ファイルを読み込む"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """ロギングをセットアップ"""
    logging_config = config.get('logging', {})
    level = getattr(logging, logging_config.get('level', 'INFO'))
    format_str = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.FileHandler(logging_config.get('file', 'analysis.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('VendorQBR')


def ensure_output_dirs(config: Dict[str, Any]) -> None:
    """出力ディレクトリが存在することを確認"""
    output_config = config.get('output', {})
    dirs = [
        output_config.get('csv_dir', 'output/csv'),
        output_config.get('figures_dir', 'output/figures'),
        output_config.get('reports_dir', 'output/reports')
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)


def get_category_items(config: Dict[str, Any]) -> Dict[str, List[str]]:
    """カテゴリごとの評価項目を取得"""
    categories = config.get('categories', {})
    return {category: info['items'] for category, info in categories.items()}


def get_category_weights(config: Dict[str, Any]) -> Dict[str, float]:
    """カテゴリの重み付けを取得"""
    categories = config.get('categories', {})
    return {category: info['weight'] for category, info in categories.items()}


def save_dataframe(df: pd.DataFrame, filename: str, config: Dict[str, Any]) -> None:
    """DataFrameをCSVファイルとして保存"""
    csv_dir = config['output']['csv_dir']
    filepath = os.path.join(csv_dir, filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    logging.info(f"Saved CSV: {filepath}")

def save_dict(data: dict, filename: str, config: dict) -> None:
    output_dir = config["output"]["csv_dir"]  # または reports_dir など任意
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ CSV saved: {filepath}")

def save_test(data: dict, filename: str, config: dict) -> None:
    output_dir = config["output"]["tests_dir"]  # または reports_dir など任意
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ TESTS saved: {filepath}")
