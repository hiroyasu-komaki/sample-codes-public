"""
データ読み込みと前処理を行うモジュール
"""
import pandas as pd
import os


class SkillDataLoader:
    """スキルデータの読み込みと前処理を行うクラス"""
    
    def __init__(self, csv_path='csv/consolidated_skill_data.csv'):
        """
        Args:
            csv_path: CSVファイルのパス
        """
        self.csv_path = csv_path
        self.df = None
        self.df_aggregated = None
        
    def load_data(self):
        """データを読み込む"""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSVファイルが見つかりません: {self.csv_path}")
        
        self.df = pd.read_csv(self.csv_path)
        print(f"データを読み込みました: {len(self.df)}レコード")
        return self.df
    
    def preprocess_data(self):
        """データの前処理を行う"""
        if self.df is None:
            self.load_data()
        
        # ファイル名を人物IDとして扱う
        self.df['人物ID'] = self.df['ファイル名']
        
        # 人物ごとに集約（ファイル名が同一=同一人物）
        self.df_aggregated = self.df.copy()
        
        return self.df_aggregated
    
    def get_category_avg_by_role(self):
        """ロール×カテゴリー別の平均スキルレベルを取得"""
        if self.df_aggregated is None:
            self.preprocess_data()
        
        pivot_data = self.df_aggregated.pivot_table(
            values='スキルレベル_数値',
            index='ロール',
            columns='カテゴリー',
            aggfunc='mean'
        )
        return pivot_data
    
    def get_category_avg_by_specialty(self):
        """専門性×カテゴリー別の平均スキルレベルを取得"""
        if self.df_aggregated is None:
            self.preprocess_data()
        
        result = self.df_aggregated.groupby(['専門性', 'カテゴリー'])['スキルレベル_数値'].mean().unstack()
        return result
    
    def get_skill_level_distribution(self):
        """スキルレベルの分布を取得"""
        if self.df_aggregated is None:
            self.preprocess_data()
        
        # カテゴリー別のスキルレベル分布
        distribution = pd.crosstab(
            self.df_aggregated['カテゴリー'],
            self.df_aggregated['スキルレベル']
        )
        return distribution
    
    def get_role_skill_distribution(self):
        """ロール別のスキルレベル分布を取得"""
        if self.df_aggregated is None:
            self.preprocess_data()
        
        distribution = pd.crosstab(
            self.df_aggregated['ロール'],
            self.df_aggregated['スキルレベル']
        )
        return distribution
    
    def get_two_axis_data(self, category1='ビジネス変革', category2='テクノロジー'):
        """2軸のスキルレベルデータを取得"""
        if self.df_aggregated is None:
            self.preprocess_data()
        
        # 各ロール・専門性での2つのカテゴリーの平均スキルレベルを取得
        cat1_data = self.df_aggregated[self.df_aggregated['カテゴリー'] == category1].groupby(
            ['ロール', '専門性'])['スキルレベル_数値'].mean()
        cat2_data = self.df_aggregated[self.df_aggregated['カテゴリー'] == category2].groupby(
            ['ロール', '専門性'])['スキルレベル_数値'].mean()
        
        result = pd.DataFrame({
            category1: cat1_data,
            category2: cat2_data
        }).reset_index()
        
        return result
    
    def get_specialty_stats(self):
        """専門性別のスキルレベル統計を取得"""
        if self.df_aggregated is None:
            self.preprocess_data()
        
        # パーソナルスキル(z)を除外
        df_filtered = self.df_aggregated[self.df_aggregated['スキルレベル'] != 'z']
        
        return df_filtered
    
    def get_priority_map_data(self):
        """優先度マップ用のデータを取得"""
        if self.df_aggregated is None:
            self.preprocess_data()
        
        # カテゴリー別の平均スキルレベルと人数
        result = self.df_aggregated.groupby('カテゴリー').agg({
            'スキルレベル_数値': 'mean',
            '人物ID': 'count'
        }).reset_index()
        
        result.columns = ['カテゴリー', '平均スキルレベル', 'レコード数']
        
        # 重要度を定義（仮の値、実際はビジネス要件に応じて調整）
        importance_map = {
            'ビジネス変革': 5,
            'データ活用': 5,
            'テクノロジー': 4,
            'デザイン': 3,
            'セキュリティ': 4,
            'パーソナルスキル': 4
        }
        result['重要度'] = result['カテゴリー'].map(importance_map)
        
        return result
