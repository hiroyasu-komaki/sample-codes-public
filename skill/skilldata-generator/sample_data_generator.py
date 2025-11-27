"""
サンプルデータ生成モジュール
スキル標準データから分析用のサンプルデータを生成
"""

import os
import random
import numpy as np
import pandas as pd
from typing import List, Dict, Callable
from skill_standard_processor import SkillStandardProcessor
from user_interface import UserInterface


class SampleDataGenerator:
    """
    スキル標準データからバリエーションに富んだサンプルデータを生成するクラス
    """
    
    def __init__(self, processor: SkillStandardProcessor, random_seed: int = None):
        """
        サンプルデータジェネレーターを初期化
        
        Args:
            processor (SkillStandardProcessor): スキル標準プロセッサー
            random_seed (int, optional): ランダムシード（再現性のため）
        """
        self.processor = processor
        self.base_data = None
        
        # ランダムシードの設定
        if random_seed:
            np.random.seed(random_seed)
            random.seed(random_seed)
        
        # バリエーション戦略の初期化
        self.variation_strategies = self._initialize_strategies()
    
    def _initialize_strategies(self) -> Dict[str, Dict]:
        """
        バリエーション戦略の定義を初期化
        
        Returns:
            Dict[str, Dict]: 戦略名と戦略情報のマッピング
        """
        return {
            'engineer_focused': {
                'func': self._engineer_focused_variation,
                'description': 'Engineer-focused skills enhancement'
            },
            'designer_focused': {
                'func': self._designer_focused_variation,
                'description': 'Designer-focused skills enhancement'
            },
            'business_focused': {
                'func': self._business_focused_variation,
                'description': 'Business-focused skills enhancement'
            },
            'beginner_level': {
                'func': self._beginner_level_variation,
                'description': 'Beginner level skill distribution'
            },
            'intermediate_level': {
                'func': self._intermediate_level_variation,
                'description': 'Intermediate level skill distribution'
            },
            'expert_level': {
                'func': self._expert_level_variation,
                'description': 'Expert level skill distribution'
            },
            'data_specialized': {
                'func': self._data_specialized_variation,
                'description': 'Data utilization specialized'
            },
            'tech_specialized': {
                'func': self._tech_specialized_variation,
                'description': 'Technology specialized'
            },
            'balanced': {
                'func': self._balanced_variation,
                'description': 'Balanced skill distribution'
            },
            'random': {
                'func': self._random_variation,
                'description': 'Random skill variation'
            }
        }
    
    def generate_samples(self, num_samples: int = 10) -> List[str]:
        """
        サンプルデータを生成してファイルに保存
        
        Args:
            num_samples (int): 生成するサンプル数
            
        Returns:
            List[str]: 生成されたファイルパスのリスト
        """
        # 出力ディレクトリの作成
        output_dir = 'output/samples'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # ベースデータを取得
        self.base_data = self.processor.process_data()
        
        generated_files = []
        strategy_names = list(self.variation_strategies.keys())[:num_samples]
        
        print("\n" + "="*60)
        print("📊 Generating Sample Data")
        print("="*60)
        
        for i, strategy in enumerate(strategy_names, 1):
            # 進捗表示
            strategy_info = self.variation_strategies[strategy]
            UserInterface.display_sample_generation_progress(
                i, len(strategy_names), strategy_info['description']
            )
            
            try:
                # バリエーション適用
                sample_df = self._apply_variation(self.base_data.copy(), strategy)
                
                # ファイル保存
                filename = f'sample_{i:03d}_{strategy}.csv'
                filepath = os.path.join(output_dir, filename)
                sample_df.to_csv(filepath, index=False, encoding='utf-8')
                
                generated_files.append(filepath)
                
            except Exception as e:
                print(f"❌ Error generating sample {i} ({strategy}): {str(e)}")
                continue
        
        print(f"✅ Successfully generated {len(generated_files)} sample files")
        return generated_files
    
    def _apply_variation(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """
        指定された戦略でバリエーションを適用
        
        Args:
            df (pd.DataFrame): ベースデータ
            strategy (str): 適用する戦略名
            
        Returns:
            pd.DataFrame: バリエーション適用後のデータ
        """
        try:
            strategy_info = self.variation_strategies.get(strategy)
            if not strategy_info:
                raise ValueError(f"Unknown strategy: {strategy}")
            
            strategy_func = strategy_info['func']
            result_df = strategy_func(df)
            
            # スキルレベル_数値を再計算
            skill_level_mapping = self.processor.master_manager.get_skill_level_mapping()
            result_df['スキルレベル_数値'] = result_df['スキルレベル'].map(skill_level_mapping)
            
            # データ整合性チェック
            if not self._validate_generated_data(result_df):
                raise ValueError(f"Generated data validation failed for strategy: {strategy}")
            
            return result_df
            
        except Exception as e:
            print(f"Error applying strategy {strategy}: {str(e)}")
            return df  # フォールバック: 元のデータを返す
    
    # ===========================================
    # 職種特化型バリエーション
    # ===========================================
    
    def _engineer_focused_variation(self, df: pd.DataFrame) -> pd.DataFrame:
        """エンジニア系職種のスキルレベルを向上"""
        engineer_roles = [
            "フロントエンドエンジニア", "バックエンドエンジニア", 
            "クラウドエンジニア/SRE", "データエンジニア"
        ]
        tech_categories = ["テクノロジー", "データ活用"]
        
        # エンジニア系職種 × 技術系カテゴリーのスキルレベルを上昇
        mask = (df['ロール'].isin(engineer_roles)) & (df['カテゴリー'].isin(tech_categories))
        df.loc[mask, 'スキルレベル'] = df.loc[mask, 'スキルレベル'].apply(
            lambda x: self._upgrade_level(x) if np.random.random() < 0.8 else x
        )
        
        return df
    
    def _designer_focused_variation(self, df: pd.DataFrame) -> pd.DataFrame:
        """デザイナー系職種のスキルレベルを向上"""
        designer_roles = ["サービスデザイナー", "UX/UIデザイナー"]
        design_categories = ["デザイン", "ビジネス変革"]
        
        # デザイナー系職種 × デザイン系カテゴリーのスキルレベルを上昇
        mask = (df['ロール'].isin(designer_roles)) & (df['カテゴリー'].isin(design_categories))
        df.loc[mask, 'スキルレベル'] = df.loc[mask, 'スキルレベル'].apply(
            lambda x: self._upgrade_level(x) if np.random.random() < 0.8 else x
        )
        
        return df
    
    def _business_focused_variation(self, df: pd.DataFrame) -> pd.DataFrame:
        """ビジネス系職種のスキルレベルを向上"""
        business_roles = [
            "新規事業開発", "既存事業の高度化", 
            "社内業務の高度化・効率化", "データビジネス"
        ]
        business_categories = ["ビジネス変革", "データ活用"]
        
        # ビジネス系職種 × ビジネス系カテゴリーのスキルレベルを上昇
        mask = (df['ロール'].isin(business_roles)) & (df['カテゴリー'].isin(business_categories))
        df.loc[mask, 'スキルレベル'] = df.loc[mask, 'スキルレベル'].apply(
            lambda x: self._upgrade_level(x) if np.random.random() < 0.8 else x
        )
        
        return df
    
    # ===========================================
    # 経験レベル型バリエーション
    # ===========================================
    
    def _beginner_level_variation(self, df: pd.DataFrame) -> pd.DataFrame:
        """新人レベル: 全体的にスキルレベルを下げる"""
        df['スキルレベル'] = df['スキルレベル'].apply(
            lambda x: self._downgrade_level(x) if np.random.random() < 0.7 else x
        )
        return df
    
    def _intermediate_level_variation(self, df: pd.DataFrame) -> pd.DataFrame:
        """中堅レベル: バランスの取れた調整"""
        df['スキルレベル'] = df['スキルレベル'].apply(self._moderate_adjustment)
        return df
    
    def _expert_level_variation(self, df: pd.DataFrame) -> pd.DataFrame:
        """エキスパートレベル: 全体的にスキルレベルを上げる"""
        df['スキルレベル'] = df['スキルレベル'].apply(
            lambda x: self._upgrade_level(x) if np.random.random() < 0.6 else x
        )
        return df
    
    # ===========================================
    # 専門分野型バリエーション
    # ===========================================
    
    def _data_specialized_variation(self, df: pd.DataFrame) -> pd.DataFrame:
        """データ活用分野に特化"""
        data_categories = ["データ活用"]
        data_skills = [
            "数理統計・多変量解析・データ可視化", 
            "機械学習・深層学習", 
            "データ活用基盤設計",
            "データ活用基盤実装・運用"
        ]
        
        # データ関連スキルのレベル向上
        mask = (df['カテゴリー'].isin(data_categories)) | (df['スキル項目'].isin(data_skills))
        df.loc[mask, 'スキルレベル'] = df.loc[mask, 'スキルレベル'].apply(
            lambda x: self._upgrade_level(x) if np.random.random() < 0.7 else x
        )
        
        return df
    
    def _tech_specialized_variation(self, df: pd.DataFrame) -> pd.DataFrame:
        """テクノロジー分野に特化"""
        tech_categories = ["テクノロジー", "セキュリティ"]
        
        # テクノロジー関連スキルのレベル向上
        mask = df['カテゴリー'].isin(tech_categories)
        df.loc[mask, 'スキルレベル'] = df.loc[mask, 'スキルレベル'].apply(
            lambda x: self._upgrade_level(x) if np.random.random() < 0.7 else x
        )
        
        return df
    
    # ===========================================
    # バランス型バリエーション
    # ===========================================
    
    def _balanced_variation(self, df: pd.DataFrame) -> pd.DataFrame:
        """均等分散: 各カテゴリーを均等に調整"""
        categories = df['カテゴリー'].unique()
        
        for category in categories:
            mask = df['カテゴリー'] == category
            # カテゴリー内でランダムに30%をアップグレード
            category_indices = df[mask].index
            sample_size = max(1, int(len(category_indices) * 0.3))
            sample_indices = np.random.choice(category_indices, size=sample_size, replace=False)
            
            df.loc[sample_indices, 'スキルレベル'] = df.loc[sample_indices, 'スキルレベル'].apply(
                self._upgrade_level
            )
        
        return df
    
    def _random_variation(self, df: pd.DataFrame) -> pd.DataFrame:
        """完全ランダム: 全体からランダムに調整"""
        total_rows = len(df)
        
        # 20%をアップグレード
        upgrade_size = int(total_rows * 0.2)
        upgrade_indices = np.random.choice(df.index, size=upgrade_size, replace=False)
        df.loc[upgrade_indices, 'スキルレベル'] = df.loc[upgrade_indices, 'スキルレベル'].apply(
            self._upgrade_level
        )
        
        # 10%をダウングレード（アップグレード対象以外から）
        remaining_indices = df.index.difference(upgrade_indices)
        downgrade_size = int(total_rows * 0.1)
        if len(remaining_indices) >= downgrade_size:
            downgrade_indices = np.random.choice(remaining_indices, size=downgrade_size, replace=False)
            df.loc[downgrade_indices, 'スキルレベル'] = df.loc[downgrade_indices, 'スキルレベル'].apply(
                self._downgrade_level
            )
        
        return df
    
    # ===========================================
    # スキルレベル変換ユーティリティ
    # ===========================================
    
    def _upgrade_level(self, current_level: str) -> str:
        """スキルレベルを1段階上げる"""
        level_progression = {'d': 'c', 'c': 'b', 'b': 'a', 'a': 'a', 'z': 'b'}
        return level_progression.get(current_level, current_level)
    
    def _downgrade_level(self, current_level: str) -> str:
        """スキルレベルを1段階下げる"""
        level_regression = {'a': 'b', 'b': 'c', 'c': 'd', 'd': 'd', 'z': 'c'}
        return level_regression.get(current_level, current_level)
    
    def _moderate_adjustment(self, current_level: str) -> str:
        """中程度の調整（ランダムにアップ・ダウン・維持）"""
        adjustment = np.random.choice(['up', 'down', 'same'], p=[0.3, 0.2, 0.5])
        
        if adjustment == 'up':
            return self._upgrade_level(current_level)
        elif adjustment == 'down':
            return self._downgrade_level(current_level)
        else:
            return current_level
    
    def _validate_generated_data(self, df: pd.DataFrame) -> bool:
        """
        生成されたデータの整合性を検証
        
        Args:
            df (pd.DataFrame): 検証するデータ
            
        Returns:
            bool: 検証結果
        """
        try:
            # スキルレベルの有効性チェック
            valid_levels = {'a', 'b', 'c', 'd', 'z'}
            if not set(df['スキルレベル'].unique()).issubset(valid_levels):
                return False
            
            # NULL値のチェック
            if df.isnull().any().any():
                return False
            
            # 行数のチェック
            expected_rows = len(self.base_data)
            if len(df) != expected_rows:
                return False
            
            return True
            
        except Exception:
            return False
    
    def add_custom_strategy(self, name: str, strategy_func: Callable, description: str = "Custom strategy"):
        """
        カスタムバリエーション戦略の追加
        
        Args:
            name (str): 戦略名
            strategy_func (Callable): 戦略関数
            description (str): 戦略の説明
        """
        self.variation_strategies[name] = {
            'func': strategy_func,
            'description': description
        }
