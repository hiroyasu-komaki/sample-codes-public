#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import os
from typing import Dict, Any, Optional, List
import logging

class ConfigLoader:
    """設定ファイル読み込みクラス"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初期化
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_path = config_path
        self.config = None
        self._setup_logging()
    
    def _setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict[str, Any]:
        """
        設定ファイルを読み込む
        
        Returns:
            Dict[str, Any]: 設定データ
        
        Raises:
            FileNotFoundError: 設定ファイルが見つからない場合
            yaml.YAMLError: YAML解析エラーの場合
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
            
            self.logger.info(f"設定ファイルを読み込みました: {self.config_path}")
            self._validate_config()
            return self.config
            
        except yaml.YAMLError as e:
            self.logger.error(f"YAML解析エラー: {e}")
            raise
        except Exception as e:
            self.logger.error(f"設定ファイル読み込みエラー: {e}")
            raise
    
    def _validate_config(self):
        """設定ファイルの基本検証"""
        required_sections = [
            'project_categories',
            'industry_modifiers',
            'departments',
            'complexity_calculation',
            'project_generation'
        ]
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"必須セクションが見つかりません: {section}")
        
        self.logger.info("設定ファイルの検証が完了しました")
    
    def get_project_categories(self) -> Dict[str, Dict]:
        """プロジェクトカテゴリー設定を取得"""
        if self.config is None:
            self.load_config()
        return self.config['project_categories']
    
    def get_industry_modifiers(self) -> Dict[str, Dict]:
        """業界修正値設定を取得"""
        if self.config is None:
            self.load_config()
        return self.config['industry_modifiers']
    
    def get_departments(self) -> list:
        """部門リストを取得"""
        if self.config is None:
            self.load_config()
        return self.config['departments']
    
    def get_complexity_settings(self) -> Dict[str, Any]:
        """複雑度計算設定を取得"""
        if self.config is None:
            self.load_config()
        return self.config['complexity_calculation']
    
    def get_generation_settings(self) -> Dict[str, Any]:
        """プロジェクト生成設定を取得"""
        if self.config is None:
            self.load_config()
        return self.config['project_generation']
    
    def get_output_settings(self) -> Dict[str, Any]:
        """出力設定を取得"""
        if self.config is None:
            self.load_config()
        return self.config.get('output', {})
    
    def get_portfolio_attributes(self) -> List[str]:
        """
        ポートフォリオ分析属性を取得
        
        Returns:
            List[str]: ポートフォリオ属性のリスト
        """
        if self.config is None:
            self.load_config()
        return self.config.get('analysis_attributes', {}).get('portfolio_attributes', [])
    
    def get_signal_attributes(self) -> List[str]:
        """
        シグナル分析属性を取得
        
        Returns:
            List[str]: シグナル属性のリスト
        """
        if self.config is None:
            self.load_config()
        return self.config.get('analysis_attributes', {}).get('signal_attributes', [])
    
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """
        ドット記法でネストした設定値を取得
        
        Args:
            key_path (str): 設定キーのパス (例: "complexity_calculation.weights.risk")
            default (Any): デフォルト値
        
        Returns:
            Any: 設定値
        """
        if self.config is None:
            self.load_config()
        
        keys = key_path.split('.')
        current = self.config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            self.logger.warning(f"設定キーが見つかりません: {key_path}, デフォルト値を返します: {default}")
            return default
    
    def update_config(self, updates: Dict[str, Any]):
        """
        設定を動的に更新
        
        Args:
            updates (Dict[str, Any]): 更新する設定
        """
        if self.config is None:
            self.load_config()
        
        def deep_update(base_dict, update_dict):
            """辞書の深いマージ"""
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self.config, updates)
        self.logger.info("設定を更新しました")
    
    def save_config(self, output_path: Optional[str] = None):
        """
        現在の設定をファイルに保存
        
        Args:
            output_path (str, optional): 出力パス。指定しない場合は元のパスに保存
        """
        if self.config is None:
            raise ValueError("設定が読み込まれていません")
        
        save_path = output_path or self.config_path
        
        try:
            with open(save_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            
            self.logger.info(f"設定ファイルを保存しました: {save_path}")
            
        except Exception as e:
            self.logger.error(f"設定ファイル保存エラー: {e}")
            raise

# 使用例とテスト用の関数
def test_config_loader():
    """設定ローダーのテスト"""
    try:
        loader = ConfigLoader()
        config = loader.load_config()
        
        print("✓ 設定ファイル読み込み成功")
        print(f"プロジェクトカテゴリー数: {len(loader.get_project_categories())}")
        print(f"業界数: {len(loader.get_industry_modifiers())}")
        print(f"部門数: {len(loader.get_departments())}")
        
        # ドット記法テスト
        risk_weight = loader.get_setting("complexity_calculation.weights.risk")
        print(f"リスク重み: {risk_weight}")
        
        # 新しいメソッドのテスト
        portfolio_attrs = loader.get_portfolio_attributes()
        signal_attrs = loader.get_signal_attributes()
        print(f"ポートフォリオ属性数: {len(portfolio_attrs)}")
        print(f"シグナル属性数: {len(signal_attrs)}")
        
        return True
        
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False

if __name__ == "__main__":
    test_config_loader()
