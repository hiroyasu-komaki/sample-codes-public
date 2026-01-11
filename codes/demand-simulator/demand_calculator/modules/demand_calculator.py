"""
IT人材需要計算クラス

プロジェクトポートフォリオデータからIT人材のスキル需要を計算します。
"""

import pandas as pd
import yaml
import sys


class DemandCalculator:
    """IT人材需要計算クラス"""
    
    def __init__(self, config_path='config/calc_assumptions.yaml'):
        """
        初期化
        
        Args:
            config_path: 設定ファイルのパス
        """
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path):
        """設定ファイルを読み込む"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"エラー: 設定ファイル '{config_path}' が見つかりません。")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"エラー: 設定ファイルの読み込みに失敗しました: {e}")
            sys.exit(1)
    
    def _estimate_project_size(self, investment):
        """
        投資金額からプロジェクト規模を推定
        
        Args:
            investment: 初期投資金額（千円）
            
        Returns:
            (規模名, 規模名英語, 推定人月)
        """
        # 投資金額から人月を計算
        params = self.config['investment_to_person_months']
        labor_ratio = params['labor_cost_ratio']
        unit_cost = params['average_unit_cost']
        in_house_ratio = params['in_house_ratio']
        
        # 人月数を算出（内製比率を考慮）
        # 外注費ベースの人月 ÷ (1 - 内製比率) = 総人月（内製工数含む）
        external_person_months = (investment * labor_ratio) / unit_cost
        total_person_months = external_person_months / (1 - in_house_ratio)
        person_months = int(total_person_months)
        
        # 人月数に基づいて規模を判定
        thresholds = self.config['project_size_thresholds']
        
        if person_months >= thresholds['large']['min_person_months']:
            size = 'large'
        elif person_months >= thresholds['medium']['min_person_months']:
            size = 'medium'
        elif person_months >= thresholds['small']['min_person_months']:
            size = 'small'
        else:
            size = 'extra_small'
        
        # 日本語の規模名に変換
        size_names = {
            'large': '大規模',
            'medium': '中規模',
            'small': '小規模',
            'extra_small': '極小規模'
        }
        
        return size_names[size], size, person_months
    
    def _identify_tech_area(self, project_name):
        """
        プロジェクト名から技術領域を判定
        
        Args:
            project_name: プロジェクト名
            
        Returns:
            技術領域名
        """
        keywords = self.config['tech_area_keywords']
        
        for tech_area, keyword_list in keywords.items():
            if tech_area == '従来型':
                continue
            for keyword in keyword_list:
                if keyword in project_name:
                    return tech_area
        
        return '従来型'
    
    def _identify_project_type(self, project_name):
        """
        プロジェクト名からプロジェクト種別を判定
        
        Args:
            project_name: プロジェクト名
            
        Returns:
            プロジェクト種別名
        """
        keywords = self.config['project_type_keywords']
        
        for proj_type, keyword_list in keywords.items():
            if proj_type == 'その他':
                continue
            for keyword in keyword_list:
                if keyword in project_name:
                    return proj_type
        
        return 'その他'
    
    def classify_projects(self, df):
        """
        プロジェクトの分類のみを実行（中間ファイル生成用）
        
        Args:
            df: 入力データフレーム
            
        Returns:
            分類情報が追加されたデータフレーム
        """
        # 元のCSVのすべての列を保持
        result_df = df.copy()
        
        # 必須列の存在確認
        required_cols = ['案件ID', '案件名', '初期投資金額', '運用費', 'システム利用開始時期']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"必要な列が見つかりません: {missing_cols}")
        
        # 日付型に変換
        result_df['稼働開始日'] = pd.to_datetime(result_df['システム利用開始時期'])
        result_df['稼働年度'] = result_df['稼働開始日'].dt.year
        
        # 活動期間月数を計算（活動開始月・活動終了月がある場合）
        if '活動開始月' in df.columns and '活動終了月' in df.columns:
            start_dates = pd.to_datetime(result_df['活動開始月'], format='mixed', dayfirst=False)
            end_dates = pd.to_datetime(result_df['活動終了月'], format='mixed', dayfirst=False)
            
            # 月数を計算（開始月と終了月を含む）
            result_df['活動期間月数'] = (
                (end_dates.dt.year - start_dates.dt.year) * 12 + 
                (end_dates.dt.month - start_dates.dt.month) + 1
            )
        else:
            # 活動期間情報がない場合はデフォルト12ヶ月
            result_df['活動期間月数'] = 12
        
        # プロジェクトの分類を行単位で実施
        classification_data = []
        
        for _, row in result_df.iterrows():
            # 分類
            size_jp, size_en, person_months = self._estimate_project_size(row['初期投資金額'])
            tech_area = self._identify_tech_area(row['案件名'])
            proj_type = self._identify_project_type(row['案件名'])
            
            # スキル構成比キーの決定（規模_種別）
            skill_key = f"{size_en}_{proj_type}"
            
            # 分類データ
            classification_data.append({
                'プロジェクト規模': size_jp,
                'プロジェクト規模_英語': size_en,
                '推定人月': person_months,
                '技術領域': tech_area,
                'プロジェクト種別': proj_type,
                'スキル構成比キー': skill_key
            })
        
        # 分類データを追加
        class_df = pd.DataFrame(classification_data)
        result_df = pd.concat([result_df.reset_index(drop=True), class_df], axis=1)
        
        return result_df
    
    def calculate_demand(self, df):
        """
        データフレームに対して需要計算を実行
        
        Args:
            df: 入力データフレーム
            
        Returns:
            スキル需要が追加されたデータフレーム
        """
        # 元のCSVのすべての列を保持（既存のスキル列は後で上書きされる）
        result_df = df.copy()
        
        # 必須列の存在確認
        required_cols = ['案件ID', '案件名', '初期投資金額', '運用費', 'システム利用開始時期']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"必要な列が見つかりません: {missing_cols}")
        
        # 日付型に変換
        result_df['稼働開始日'] = pd.to_datetime(result_df['システム利用開始時期'])
        result_df['稼働年度'] = result_df['稼働開始日'].dt.year
        
        # 活動期間月数を計算（活動開始月・活動終了月がある場合）
        if '活動開始月' in df.columns and '活動終了月' in df.columns:
            start_dates = pd.to_datetime(result_df['活動開始月'], format='mixed', dayfirst=False)
            end_dates = pd.to_datetime(result_df['活動終了月'], format='mixed', dayfirst=False)
            
            # 月数を計算（開始月と終了月を含む）
            result_df['活動期間月数'] = (
                (end_dates.dt.year - start_dates.dt.year) * 12 + 
                (end_dates.dt.month - start_dates.dt.month) + 1
            )
        else:
            # 活動期間情報がない場合はデフォルト12ヶ月
            result_df['活動期間月数'] = 12
        
        # プロジェクトの分類と需要計算を行単位で実施
        classification_data = []
        skill_data = []
        
        skill_dist = self.config['skill_distribution']
        op_params = self.config['operation_parameters']
        
        for _, row in result_df.iterrows():
            # 分類
            size_jp, size_en, person_months = self._estimate_project_size(row['初期投資金額'])
            tech_area = self._identify_tech_area(row['案件名'])
            proj_type = self._identify_project_type(row['案件名'])
            
            # スキル構成比キーの決定（規模_種別）
            skill_key = f"{size_en}_{proj_type}"
            
            # 分類データ
            classification_data.append({
                'プロジェクト規模': size_jp,
                'プロジェクト規模_英語': size_en,
                '推定人月': person_months,
                '技術領域': tech_area,
                'プロジェクト種別': proj_type,
                'スキル構成比キー': skill_key
            })
            
            # 標準構成比を取得（規模_種別の組み合わせで取得、なければ規模のみで取得）
            distribution = skill_dist.get(skill_key)
            if distribution is None:
                # フォールバック: 規模のみで取得を試みる
                fallback_key = f"{size_en}_その他"
                distribution = skill_dist.get(fallback_key, skill_dist.get('small_その他', {}))
            
            # スキル需要を計算
            skills = {}
            for skill, ratio in distribution.items():
                # 列名はスキル名のみ（_期間中月平均を除去）
                # 小数点以下第2位まで（第3位を四捨五入）
                skills[skill] = round(person_months * ratio, 2)
            
            # 運用需要の計算（小数点以下第2位まで）
            operation_annual = (row['運用費'] * op_params['labor_cost_ratio']) / op_params['average_unit_cost']
            skills['運用_年間人月'] = round(operation_annual, 2)
            skills['運用_月平均'] = round(operation_annual / 12, 2)
            
            skill_data.append(skills)
        
        # 分類データを追加
        class_df = pd.DataFrame(classification_data)
        result_df = pd.concat([result_df.reset_index(drop=True), class_df], axis=1)
        
        # スキルデータを追加
        skill_df = pd.DataFrame(skill_data)
        result_df = pd.concat([result_df, skill_df], axis=1)
        
        return result_df
    
    def calculate_demand_from_classified(self, df):
        """
        分類済みデータフレームに対してスキル需要計算のみを実行
        
        Args:
            df: 分類済みデータフレーム（classify_projectsの出力）
            
        Returns:
            スキル需要が追加されたデータフレーム
        """
        result_df = df.copy()
        
        # スキル需要計算を行単位で実施
        skill_data = []
        
        skill_dist = self.config['skill_distribution']
        op_params = self.config['operation_parameters']
        
        for _, row in result_df.iterrows():
            # 既に分類済みのデータを使用
            person_months = row['推定人月']
            skill_key = row['スキル構成比キー']
            
            # 活動期間月数を取得（なければ12ヶ月）
            activity_months = row.get('活動期間月数', 12)
            
            # 標準構成比を取得（規模_種別の組み合わせで取得）
            distribution = skill_dist.get(skill_key)
            if distribution is None:
                # フォールバック: その他を試みる
                size_en = row['プロジェクト規模_英語']
                fallback_key = f"{size_en}_その他"
                distribution = skill_dist.get(fallback_key, skill_dist.get('small_その他', {}))
            
            # スキル需要を計算
            skills = {}
            for skill, ratio in distribution.items():
                total_person_months = person_months * ratio
                # 活動期間中の月平均を計算
                # 列名はスキル名のみ（_期間中月平均を除去）
                # 小数点以下第2位まで（第3位を四捨五入）
                skills[skill] = round(total_person_months / activity_months, 2)
            
            # 運用需要の計算（小数点以下第2位まで）
            operation_annual = (row['運用費'] * op_params['labor_cost_ratio']) / op_params['average_unit_cost']
            skills['運用_年間人月'] = round(operation_annual, 2)
            skills['運用_月平均'] = round(operation_annual / 12, 2)
            
            skill_data.append(skills)
        
        # スキルデータを追加
        skill_df = pd.DataFrame(skill_data)
        result_df = pd.concat([result_df, skill_df], axis=1)
        
        return result_df
        """
        データフレームに対して需要計算を実行
        
        Args:
            df: 入力データフレーム
            
        Returns:
            スキル需要が追加されたデータフレーム
        """
        # 元のCSVから必要な列だけを抽出（既存のスキル列を除外）
        base_columns = ['案件ID', '案件名', '初期投資金額', '運用費', 'システム利用開始時期']
        result_df = df[base_columns].copy()
        
        # 日付型に変換
        result_df['稼働開始日'] = pd.to_datetime(result_df['システム利用開始時期'])
        result_df['稼働年度'] = result_df['稼働開始日'].dt.year
        
        # プロジェクトの分類と需要計算を行単位で実施
        classification_data = []
        skill_data = []
        
        skill_dist = self.config['skill_distribution']
        it_config = self.config['it_specialist_skill']
        op_params = self.config['operation_parameters']
        
        for _, row in result_df.iterrows():
            # 分類
            size_jp, size_en, person_months = self._estimate_project_size(row['初期投資金額'])
            tech_area = self._identify_tech_area(row['案件名'])
            sys_type = self._identify_system_type(row['案件名'])
            proj_type = self._identify_project_type(row['案件名'])
            
            # 分類データ
            classification_data.append({
                'プロジェクト規模': size_jp,
                'プロジェクト規模_英語': size_en,
                '推定人月': person_months,
                '技術領域': tech_area,
                'システムタイプ': sys_type,
                'プロジェクト種別': proj_type
            })
            
            # 標準構成比を取得
            distribution = skill_dist.get(size_en, skill_dist['small'])
            
            # スキル需要を計算
            skills = {}
            for skill, ratio in distribution.items():
                skills[skill] = person_months * ratio
            
            # 運用需要の計算
            operation_annual = (row['運用費'] * op_params['labor_cost_ratio']) / op_params['average_unit_cost']
            skills['運用_年間人月'] = operation_annual
            skills['運用_月平均'] = operation_annual / 12
            
            skill_data.append(skills)
        
        # 分類データを追加
        class_df = pd.DataFrame(classification_data)
        result_df = pd.concat([result_df.reset_index(drop=True), class_df], axis=1)
        
        # スキルデータを追加
        skill_df = pd.DataFrame(skill_data)
        result_df = pd.concat([result_df, skill_df], axis=1)
        
        return result_df
    
    def process_csv_file_classify(self, input_path, output_path):
        """
        1つのCSVファイルを処理（分類のみ、中間ファイル生成）
        
        Args:
            input_path: 入力CSVファイルのパス
            output_path: 出力CSVファイルのパス（中間ファイル）
        """
        print(f"\n【ステップ1: 分類処理】")
        print(f"処理中: {input_path.name}")
        print("-" * 60)
        
        try:
            # CSVファイルを読み込む
            df = pd.read_csv(input_path)
            print(f"  ✓ データ読み込み: {len(df)}件")
            
            # 必要な列が存在するかチェック
            required_cols = ['案件ID', '案件名', '初期投資金額', '運用費', 'システム利用開始時期']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"  ✗ エラー: 必要な列が見つかりません: {missing_cols}")
                return
            
            # 分類処理を実行
            result_df = self.classify_projects(df)
            print(f"  ✓ 分類処理完了")
            
            # 出力用の列順を整理（入力CSVの列順を保持）
            # 1. 入力CSVのオリジナル列を取得
            input_columns = [col for col in df.columns if col in result_df.columns]
            
            # 2. プログラムで追加された列
            added_columns = [
                '稼働開始日',
                '稼働年度',
                '活動期間月数',
                'プロジェクト規模',
                'プロジェクト規模_英語',
                '推定人月',
                '技術領域',
                'プロジェクト種別',
                'スキル構成比キー'
            ]
            
            # 3. 入力列 + 追加列の順序で出力
            output_cols = input_columns + [col for col in added_columns if col in result_df.columns]
            
            # 重複を除去（念のため）
            seen = set()
            output_cols = [col for col in output_cols if col not in seen and not seen.add(col)]
            
            # CSVファイルに出力（中間ファイル）
            result_df[output_cols].to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"  ✓ 中間ファイル出力完了: {output_path}")
            
            # 分類結果のサマリーを表示
            self._print_classification_summary(result_df)
            
        except Exception as e:
            print(f"  ✗ エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def process_csv_file_demand(self, input_path, output_path):
        """
        中間CSVファイルを読み込んでスキル需要計算を実行
        
        Args:
            input_path: 入力CSVファイルのパス（中間ファイル）
            output_path: 出力CSVファイルのパス（最終結果）
        """
        print(f"\n【ステップ2: スキル需要計算】")
        print(f"処理中: {input_path.name}")
        print("-" * 60)
        
        try:
            # 中間CSVファイルを読み込む
            df = pd.read_csv(input_path)
            print(f"  ✓ 中間ファイル読み込み: {len(df)}件")
            
            # 必要な列が存在するかチェック
            required_cols = ['案件ID', '案件名', '初期投資金額', '運用費', 
                           'プロジェクト規模_英語', '推定人月', '技術領域', 'スキル構成比キー']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"  ✗ エラー: 必要な列が見つかりません: {missing_cols}")
                return
            
            # スキル需要計算を実行
            result_df = self.calculate_demand_from_classified(df)
            print(f"  ✓ スキル需要計算完了")
            
            # 出力用の列順を整理（入力CSVの列順を保持）
            # 1. 中間ファイルのオリジナル列を取得
            input_columns = [col for col in df.columns if col in result_df.columns]
            
            # 2. スキル需要計算で追加された列
            skill_columns = [
                'ビジネスケイパビリティ',
                'デリバリケイパビリティ',
                'テクニカルケイパビリティ',
                'リーダーシップケイパビリティ',
                '運用_年間人月',
                '運用_月平均'
            ]
            
            # 3. 入力列 + スキル列の順序で出力
            output_cols = input_columns + [col for col in skill_columns if col in result_df.columns]
            
            # 重複を除去（念のため）
            seen = set()
            output_cols = [col for col in output_cols if col not in seen and not seen.add(col)]
            
            # CSVファイルに出力
            result_df[output_cols].to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"  ✓ 最終結果出力完了: {output_path}")
            
            # サマリーを表示
            self._print_summary(result_df)
            
        except Exception as e:
            print(f"  ✗ エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def process_csv_file(self, input_path, output_path):
        """
        1つのCSVファイルを処理
        
        Args:
            input_path: 入力CSVファイルのパス
            output_path: 出力CSVファイルのパス
        """
        print(f"\n処理中: {input_path.name}")
        print("-" * 60)
        
        try:
            # CSVファイルを読み込む
            df = pd.read_csv(input_path)
            print(f"  ✓ データ読み込み: {len(df)}件")
            
            # 必要な列が存在するかチェック
            required_cols = ['案件ID', '案件名', '初期投資金額', '運用費', 'システム利用開始時期']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"  ✗ エラー: 必要な列が見つかりません: {missing_cols}")
                return
            
            # 需要計算を実行
            result_df = self.calculate_demand(df)
            print(f"  ✓ 需要計算完了")
            
            # 出力用の列順を整理（入力CSVの列順を保持）
            # 1. 入力CSVのオリジナル列を取得
            input_columns = [col for col in df.columns if col in result_df.columns]
            
            # 2. プログラムで追加された列
            added_columns = [
                '稼働開始日',
                '稼働年度',
                '活動期間月数',
                'プロジェクト規模',
                'プロジェクト規模_英語',
                '推定人月',
                '技術領域',
                'プロジェクト種別',
                'スキル構成比キー',
                'ビジネスケイパビリティ',
                'デリバリケイパビリティ',
                'テクニカルケイパビリティ',
                'リーダーシップケイパビリティ',
                '運用_年間人月',
                '運用_月平均'
            ]
            
            # 3. 入力列 + 追加列の順序で出力
            output_cols = input_columns + [col for col in added_columns if col in result_df.columns]
            
            # 重複を除去（念のため）
            seen = set()
            output_cols = [col for col in output_cols if col not in seen and not seen.add(col)]
            
            # CSVファイルに出力
            result_df[output_cols].to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"  ✓ 出力完了: {output_path}")
            
            # サマリーを表示
            self._print_summary(result_df)
            
        except Exception as e:
            print(f"  ✗ エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def _print_classification_summary(self, df):
        """
        分類結果のサマリーを表示
        
        Args:
            df: 分類結果のデータフレーム
        """
        print(f"\n  【分類サマリー】")
        
        # プロジェクト規模別の件数
        if 'プロジェクト規模' in df.columns:
            print(f"\n  プロジェクト規模別:")
            size_counts = df['プロジェクト規模'].value_counts()
            for size, count in size_counts.items():
                print(f"    {size:12s}: {count:3d}件")
        
        # 技術領域別の件数
        if '技術領域' in df.columns:
            print(f"\n  技術領域別:")
            tech_counts = df['技術領域'].value_counts()
            for tech, count in tech_counts.items():
                print(f"    {tech:12s}: {count:3d}件")
        
        # プロジェクト種別の件数
        if 'プロジェクト種別' in df.columns:
            print(f"\n  プロジェクト種別:")
            proj_counts = df['プロジェクト種別'].value_counts()
            for proj_type, count in proj_counts.items():
                print(f"    {proj_type:12s}: {count:3d}件")

    
    def _print_summary(self, df):
        """
        計算結果のサマリーを表示
        
        Args:
            df: 計算結果のデータフレーム
        """
        print(f"\n  【サマリー】")
        
        # ケイパビリティ別の合計
        capability_cols = ['ビジネスケイパビリティ', 'デリバリケイパビリティ', 
                          'テクニカルケイパビリティ', 'リーダーシップケイパビリティ']
        capability_names = ['ビジネスケイパビリティ', 'デリバリケイパビリティ', 
                           'テクニカルケイパビリティ', 'リーダーシップケイパビリティ']
        
        print(f"\n  全体ケイパビリティ別需要（合計）:")
        for col, name in zip(capability_cols, capability_names):
            if col in df.columns:
                # 列のデータ型をチェック
                col_data = df[col]
                
                # NaNを除外して合計を計算
                total = col_data.sum()
                
                # numpy型やpandas型をPythonのfloatに変換
                if pd.isna(total):
                    total = 0.0
                else:
                    total = float(total)
                
                print(f"    {name:24s}: {total:6.2f}名")
        
        # ケイパビリティごとのプロジェクト規模×種別の集計
        if 'プロジェクト規模' in df.columns and 'プロジェクト種別' in df.columns:
            # 規模の順序を定義
            size_order = {'大規模': 1, '中規模': 2, '小規模': 3, '極小規模': 4}
            
            for col, name in zip(capability_cols, capability_names):
                if col not in df.columns:
                    continue
                
                print(f"\n  【{name}】プロジェクト規模・種別ごとの需要（合計）:")
                print(f"  {'-' * 100}")
                
                # 規模と種別でグループ化
                grouped = df.groupby(['プロジェクト規模', 'プロジェクト種別'])
                
                for (size, proj_type), group in sorted(grouped, key=lambda x: (size_order.get(x[0][0], 99), x[0][1])):
                    count = len(group)
                    total = float(group[col].sum())
                    
                    if total > 0.01:  # 0.01名以上の場合のみ表示
                        print(f"    [{size:6s} × {proj_type:8s}] ({count:3d}件): {total:6.2f}名")

