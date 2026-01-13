"""
IT人材需要計算 - データバリデーションクラス

CSVファイルのデータ品質をチェックし、エラーや警告を報告します。
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
import re


class ValidationError:
    """バリデーションエラー情報"""
    
    def __init__(self, severity: str, category: str, message: str, 
                 row_index: int = None, column: str = None):
        """
        Args:
            severity: 'ERROR' または 'WARNING'
            category: エラーカテゴリ（'構造', 'データ型', '必須項目', '値範囲', 'フォーマット'等）
            message: エラーメッセージ
            row_index: 該当行のインデックス（行単位のエラーの場合）
            column: 該当列名（列単位のエラーの場合）
        """
        self.severity = severity
        self.category = category
        self.message = message
        self.row_index = row_index
        self.column = column
    
    def __str__(self):
        location = ""
        if self.row_index is not None:
            location = f"[行 {self.row_index + 2}]"  # +2: ヘッダー行+0始まり
        if self.column:
            location += f"[{self.column}列]"
        
        return f"  [{self.severity}] {self.category}: {location} {self.message}"


class DataValidator:
    """CSVデータのバリデーションクラス"""
    
    # 必須列の定義
    REQUIRED_COLUMNS = [
        '案件ID',
        '案件名',
        '初期投資金額',
        '運用費',
        'システム利用開始時期'
    ]
    
    # 推奨列（あると計算精度が上がる）
    RECOMMENDED_COLUMNS = [
        '活動開始月',
        '活動終了月'
    ]
    
    # 日付列の定義
    DATE_COLUMNS = {
        'システム利用開始時期': {
            'formats': ['%Y/%m/%d', '%Y-%m-%d', '%Y/%m', '%Y-%m'],
            'allow_future': True
        },
        '活動開始月': {
            'formats': ['%Y/%m', '%Y-%m', '%Y/%m/%d', '%Y-%m-%d'],
            'allow_future': True
        },
        '活動終了月': {
            'formats': ['%Y/%m', '%Y-%m', '%Y/%m/%d', '%Y-%m-%d'],
            'allow_future': True
        }
    }
    
    # 数値列の定義
    NUMERIC_COLUMNS = {
        '初期投資金額': {
            'min': 0,
            'max': 100000000,  # 1000億円
            'allow_zero': False
        },
        '運用費': {
            'min': 0,
            'max': 10000000,  # 100億円/年
            'allow_zero': True
        }
    }
    
    def __init__(self):
        """初期化"""
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def validate_config_file(self, config_path: Path = None) -> bool:
        """
        設定ファイル（calc_assumptions.yaml）のバリデーション
        
        Args:
            config_path: 設定ファイルのパス（デフォルトはconfig/calc_assumptions.yaml）
            
        Returns:
            検証成功フラグ
        """
        if config_path is None:
            config_path = Path('config/calc_assumptions.yaml')
        
        print(f"\n{'=' * 80}")
        print(f"設定ファイルバリデーション: {config_path}")
        print(f"{'=' * 80}")
        
        if not config_path.exists():
            self.errors.append(ValidationError(
                'ERROR', 'ファイル', f"設定ファイルが見つかりません: {config_path}"
            ))
            return False
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            self.errors.append(ValidationError(
                'ERROR', 'ファイル', f"設定ファイルの読み込みに失敗: {str(e)}"
            ))
            return False
        
        # ゼロ除算の原因となる設定値をチェック
        
        # 1. investment_to_person_monthsのチェック
        if 'investment_to_person_months' in config:
            params = config['investment_to_person_months']
            
            # average_unit_costがゼロまたは負
            unit_cost = params.get('average_unit_cost', 0)
            if unit_cost <= 0:
                self.errors.append(ValidationError(
                    'ERROR', '設定値', 
                    f"investment_to_person_months.average_unit_cost がゼロまたは負です: {unit_cost}（ゼロ除算の原因）"
                ))
            
            # in_house_ratioが1.0以上
            in_house_ratio = params.get('in_house_ratio', 0)
            if in_house_ratio >= 1.0:
                self.errors.append(ValidationError(
                    'ERROR', '設定値', 
                    f"investment_to_person_months.in_house_ratio が1.0以上です: {in_house_ratio}（ゼロ除算の原因）"
                ))
            
            if in_house_ratio < 0:
                self.errors.append(ValidationError(
                    'ERROR', '設定値', 
                    f"investment_to_person_months.in_house_ratio が負です: {in_house_ratio}"
                ))
        else:
            self.errors.append(ValidationError(
                'ERROR', '設定値', "investment_to_person_months が設定ファイルに存在しません"
            ))
        
        # 2. operation_parametersのチェック
        if 'operation_parameters' in config:
            params = config['operation_parameters']
            
            # average_unit_costがゼロまたは負
            unit_cost = params.get('average_unit_cost', 0)
            if unit_cost <= 0:
                self.errors.append(ValidationError(
                    'ERROR', '設定値', 
                    f"operation_parameters.average_unit_cost がゼロまたは負です: {unit_cost}（ゼロ除算の原因）"
                ))
        else:
            self.errors.append(ValidationError(
                'ERROR', '設定値', "operation_parameters が設定ファイルに存在しません"
            ))
        
        # 結果表示
        if len(self.errors) > 0:
            print(f"\n❌ エラー: {len(self.errors)}件")
            print("-" * 80)
            for error in self.errors:
                print(error)
            print(f"\n{'=' * 80}")
            print("❌ 設定ファイルバリデーション失敗")
            print(f"{'=' * 80}\n")
            return False
        else:
            print(f"\n✅ エラー: 0件")
            print(f"\n{'=' * 80}")
            print("✅ 設定ファイルバリデーション成功")
            print(f"{'=' * 80}\n")
            return True
    
    def validate_csv_file(self, file_path: Path) -> Tuple[bool, pd.DataFrame]:
        """
        CSVファイルをバリデーション
        
        Args:
            file_path: CSVファイルのパス
            
        Returns:
            (検証成功フラグ, データフレーム)
            エラーがある場合は False, エラーがない場合は True
        """
        self.errors = []
        self.warnings = []
        
        print(f"\n{'=' * 80}")
        print(f"データバリデーション: {file_path.name}")
        print(f"{'=' * 80}")
        
        # ファイル存在チェック
        if not file_path.exists():
            self.errors.append(ValidationError(
                'ERROR', 'ファイル', f"ファイルが見つかりません: {file_path}"
            ))
            self._print_results()
            return False, None
        
        # ファイルサイズチェック
        file_size = file_path.stat().st_size
        if file_size == 0:
            self.errors.append(ValidationError(
                'ERROR', 'ファイル', "ファイルが空です"
            ))
            self._print_results()
            return False, None
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            self.warnings.append(ValidationError(
                'WARNING', 'ファイル', 
                f"ファイルサイズが大きいです ({file_size / 1024 / 1024:.1f}MB)"
            ))
        
        # CSV読み込み
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            # Shift-JISで再試行
            try:
                df = pd.read_csv(file_path, encoding='shift_jis')
                self.warnings.append(ValidationError(
                    'WARNING', 'エンコーディング', 
                    "ファイルがShift-JISでエンコードされています。UTF-8を推奨します。"
                ))
            except Exception as e:
                self.errors.append(ValidationError(
                    'ERROR', 'ファイル', f"CSVファイルの読み込みに失敗: {str(e)}"
                ))
                self._print_results()
                return False, None
        except Exception as e:
            self.errors.append(ValidationError(
                'ERROR', 'ファイル', f"CSVファイルの読み込みに失敗: {str(e)}"
            ))
            self._print_results()
            return False, None
        
        # 基本構造チェック
        self._validate_structure(df)
        
        # 列名チェック
        self._validate_columns(df)
        
        # データ内容チェック
        if len(self.errors) == 0:  # 構造的なエラーがない場合のみ
            self._validate_data_content(df)
        
        # 結果表示
        self._print_results()
        
        # エラーがあるかどうかを返す
        has_errors = len(self.errors) > 0
        return not has_errors, df
    
    def validate_multiple_files(self, file_paths: List[Path]) -> bool:
        """
        複数のCSVファイルをバリデーション
        
        Args:
            file_paths: CSVファイルパスのリスト
            
        Returns:
            全てのファイルが検証を通過した場合 True
        """
        all_valid = True
        
        for file_path in file_paths:
            is_valid, _ = self.validate_csv_file(file_path)
            if not is_valid:
                all_valid = False
        
        return all_valid
    
    def _validate_structure(self, df: pd.DataFrame):
        """基本構造をチェック"""
        
        # 空のデータフレームチェック
        if len(df) == 0:
            self.errors.append(ValidationError(
                'ERROR', '構造', "データが1件も含まれていません"
            ))
            return
        
        # 列数チェック
        if len(df.columns) < len(self.REQUIRED_COLUMNS):
            self.errors.append(ValidationError(
                'ERROR', '構造', 
                f"列数が不足しています（最低{len(self.REQUIRED_COLUMNS)}列必要）"
            ))
        
        # 重複列名チェック
        if len(df.columns) != len(set(df.columns)):
            duplicate_cols = [col for col in df.columns if list(df.columns).count(col) > 1]
            self.errors.append(ValidationError(
                'ERROR', '構造', f"重複する列名があります: {set(duplicate_cols)}"
            ))
        
        # 完全に空の行チェック
        empty_rows = df[df.isna().all(axis=1)]
        if len(empty_rows) > 0:
            for idx in empty_rows.index:
                self.warnings.append(ValidationError(
                    'WARNING', '構造', "完全に空の行があります", row_index=idx
                ))
    
    def _validate_columns(self, df: pd.DataFrame):
        """列名をチェック"""
        
        # 必須列の存在チェック
        missing_required = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_required:
            for col in missing_required:
                self.errors.append(ValidationError(
                    'ERROR', '必須列', f"必須列が見つかりません: {col}"
                ))
        
        # 推奨列の存在チェック
        missing_recommended = [col for col in self.RECOMMENDED_COLUMNS if col not in df.columns]
        if missing_recommended:
            for col in missing_recommended:
                self.warnings.append(ValidationError(
                    'WARNING', '推奨列', 
                    f"推奨列が見つかりません: {col}（デフォルト値が使用されます）"
                ))
        
        # 列名の空白チェック
        for col in df.columns:
            if col != col.strip():
                self.warnings.append(ValidationError(
                    'WARNING', 'フォーマット', 
                    f"列名に余分な空白があります: '{col}'", column=col
                ))
    
    def _validate_data_content(self, df: pd.DataFrame):
        """データ内容をチェック"""
        
        # 必須列の欠損値チェック
        self._validate_required_values(df)
        
        # 数値列のチェック
        self._validate_numeric_columns(df)
        
        # 日付列のチェック
        self._validate_date_columns(df)
        
        # テキスト列のチェック
        self._validate_text_columns(df)
        
        # 論理整合性チェック
        self._validate_logical_consistency(df)
        
        # データ品質の統計情報
        self._validate_data_quality(df)
    
    def _validate_required_values(self, df: pd.DataFrame):
        """必須項目の値チェック"""
        
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                continue
            
            # 欠損値チェック
            null_rows = df[df[col].isna()]
            if len(null_rows) > 0:
                for idx in null_rows.index:
                    self.errors.append(ValidationError(
                        'ERROR', '必須項目', 
                        f"必須項目が空です", row_index=idx, column=col
                    ))
            
            # 空文字列チェック（テキスト列の場合）
            if df[col].dtype == 'object':
                empty_rows = df[df[col].astype(str).str.strip() == '']
                if len(empty_rows) > 0:
                    for idx in empty_rows.index:
                        self.errors.append(ValidationError(
                            'ERROR', '必須項目', 
                            "必須項目が空文字です", row_index=idx, column=col
                        ))
    
    def _validate_numeric_columns(self, df: pd.DataFrame):
        """数値列をチェック"""
        
        for col, rules in self.NUMERIC_COLUMNS.items():
            if col not in df.columns:
                continue
            
            # 数値型への変換試行
            for idx, value in df[col].items():
                if pd.isna(value):
                    continue
                
                # 数値変換チェック
                try:
                    numeric_value = float(value)
                except (ValueError, TypeError):
                    self.errors.append(ValidationError(
                        'ERROR', 'データ型', 
                        f"数値に変換できません: '{value}'", 
                        row_index=idx, column=col
                    ))
                    continue
                
                # 範囲チェック
                if numeric_value < rules['min']:
                    self.errors.append(ValidationError(
                        'ERROR', '値範囲', 
                        f"値が小さすぎます: {numeric_value} (最小: {rules['min']})",
                        row_index=idx, column=col
                    ))
                
                if numeric_value > rules['max']:
                    self.warnings.append(ValidationError(
                        'WARNING', '値範囲', 
                        f"値が異常に大きいです: {numeric_value:,.0f} (上限目安: {rules['max']:,.0f})",
                        row_index=idx, column=col
                    ))
                
                # ゼロチェック
                if not rules['allow_zero'] and numeric_value == 0:
                    self.errors.append(ValidationError(
                        'ERROR', '値範囲', 
                        "値がゼロです（ゼロ除算の原因となるため処理できません）", row_index=idx, column=col
                    ))
                
                # 負の値チェック
                if numeric_value < 0:
                    self.errors.append(ValidationError(
                        'ERROR', '値範囲', 
                        f"負の値は許可されていません: {numeric_value}",
                        row_index=idx, column=col
                    ))
    
    def _validate_date_columns(self, df: pd.DataFrame):
        """日付列をチェック"""
        
        for col, rules in self.DATE_COLUMNS.items():
            if col not in df.columns:
                continue
            
            for idx, value in df[col].items():
                if pd.isna(value):
                    continue
                
                # 日付変換チェック
                date_parsed = False
                for date_format in rules['formats']:
                    try:
                        parsed_date = pd.to_datetime(value, format=date_format)
                        date_parsed = True
                        
                        # 未来日チェック
                        if not rules['allow_future'] and parsed_date > pd.Timestamp.now():
                            self.warnings.append(ValidationError(
                                'WARNING', 'フォーマット', 
                                f"未来の日付です: {value}",
                                row_index=idx, column=col
                            ))
                        
                        # 過去過ぎる日付チェック
                        if parsed_date < pd.Timestamp('2000-01-01'):
                            self.warnings.append(ValidationError(
                                'WARNING', 'フォーマット', 
                                f"日付が古すぎます: {value}",
                                row_index=idx, column=col
                            ))
                        
                        break
                    except:
                        continue
                
                if not date_parsed:
                    self.errors.append(ValidationError(
                        'ERROR', 'フォーマット', 
                        f"日付フォーマットが不正です: '{value}' "
                        f"(推奨フォーマット: {', '.join(rules['formats'])})",
                        row_index=idx, column=col
                    ))
    
    def _validate_text_columns(self, df: pd.DataFrame):
        """テキスト列をチェック"""
        
        text_columns = ['案件ID', '案件名']
        
        for col in text_columns:
            if col not in df.columns:
                continue
            
            # 案件IDの重複チェック
            if col == '案件ID':
                duplicates = df[df[col].duplicated(keep=False)]
                if len(duplicates) > 0:
                    dup_ids = duplicates[col].unique()
                    for dup_id in dup_ids:
                        dup_rows = df[df[col] == dup_id].index.tolist()
                        self.errors.append(ValidationError(
                            'ERROR', 'データ整合性', 
                            f"案件IDが重複しています: '{dup_id}' (行: {[i+2 for i in dup_rows]})",
                            column=col
                        ))
            
            # 異常に長いテキストチェック
            for idx, value in df[col].items():
                if pd.isna(value):
                    continue
                
                text = str(value)
                
                if col == '案件ID' and len(text) > 100:
                    self.warnings.append(ValidationError(
                        'WARNING', 'フォーマット', 
                        f"案件IDが長すぎます ({len(text)}文字): '{text[:50]}...'",
                        row_index=idx, column=col
                    ))
                
                if col == '案件名' and len(text) > 200:
                    self.warnings.append(ValidationError(
                        'WARNING', 'フォーマット', 
                        f"案件名が長すぎます ({len(text)}文字): '{text[:50]}...'",
                        row_index=idx, column=col
                    ))
                
                # 制御文字チェック
                if re.search(r'[\x00-\x1f\x7f-\x9f]', text):
                    self.warnings.append(ValidationError(
                        'WARNING', 'フォーマット', 
                        "制御文字が含まれています",
                        row_index=idx, column=col
                    ))
    
    def _validate_logical_consistency(self, df: pd.DataFrame):
        """論理整合性をチェック"""
        
        # 活動開始月と終了月の整合性
        if '活動開始月' in df.columns and '活動終了月' in df.columns:
            for idx, row in df.iterrows():
                start = row.get('活動開始月')
                end = row.get('活動終了月')
                
                if pd.isna(start) or pd.isna(end):
                    continue
                
                try:
                    start_date = pd.to_datetime(start, format='mixed')
                    end_date = pd.to_datetime(end, format='mixed')
                    
                    if start_date > end_date:
                        self.errors.append(ValidationError(
                            'ERROR', 'データ整合性', 
                            f"活動開始月が終了月より後です: {start} > {end}",
                            row_index=idx
                        ))
                    
                    # 異常に長い期間チェック
                    duration_months = (end_date.year - start_date.year) * 12 + \
                                     (end_date.month - start_date.month) + 1
                    
                    # ゼロまたは負の期間チェック
                    if duration_months <= 0:
                        self.errors.append(ValidationError(
                            'ERROR', 'データ整合性', 
                            f"活動期間が0ヶ月以下です（ゼロ除算の原因となります）: {duration_months}ヶ月",
                            row_index=idx
                        ))
                    elif duration_months > 60:  # 5年以上
                        self.warnings.append(ValidationError(
                            'WARNING', 'データ整合性', 
                            f"活動期間が異常に長いです: {duration_months}ヶ月",
                            row_index=idx
                        ))
                except:
                    pass  # 日付パースエラーは別で検出済み
        

    
    def _validate_data_quality(self, df: pd.DataFrame):
        """データ品質の統計情報をチェック"""
        
        # 案件名にキーワードがない行をチェック
        if '案件名' in df.columns:
            keywords = ['開発', '構築', '導入', '刷新', 'リプレース', '移行', 
                       'AI', 'クラウド', 'DX', 'システム']
            
            rows_without_keywords = []
            for idx, value in df['案件名'].items():
                if pd.isna(value):
                    continue
                
                text = str(value)
                if not any(kw in text for kw in keywords):
                    rows_without_keywords.append(idx)
            
            if len(rows_without_keywords) > 0:
                ratio = len(rows_without_keywords) / len(df) * 100
                if ratio > 20:  # 20%以上
                    self.warnings.append(ValidationError(
                        'WARNING', 'データ品質', 
                        f"案件名に一般的なキーワードが含まれない行が{len(rows_without_keywords)}件 "
                        f"({ratio:.1f}%)あります。プロジェクト分類の精度が低下する可能性があります。"
                    ))
        
        # 初期投資と運用費の関係チェック
        if '初期投資金額' in df.columns and '運用費' in df.columns:
            for idx, row in df.iterrows():
                try:
                    investment = float(row['初期投資金額'])
                    operation = float(row['運用費'])
                    
                    # 運用費が初期投資の10倍以上の場合は警告
                    if operation > investment * 10:
                        self.warnings.append(ValidationError(
                            'WARNING', 'データ品質', 
                            f"運用費が初期投資の10倍以上です（初期投資: {investment:,.0f}, 運用費: {operation:,.0f}）",
                            row_index=idx
                        ))
                except (ValueError, TypeError):
                    pass  # 数値変換エラーは別で検出済み
    
    def _print_results(self):
        """検証結果を表示"""
        
        print(f"\n{'=' * 80}")
        print("バリデーション結果")
        print(f"{'=' * 80}")
        
        # エラー表示
        if len(self.errors) > 0:
            print(f"\n❌ エラー: {len(self.errors)}件")
            print("-" * 80)
            for error in self.errors:
                print(error)
        else:
            print(f"\n✅ エラー: 0件")
        
        # 警告表示
        if len(self.warnings) > 0:
            print(f"\n⚠️  警告: {len(self.warnings)}件")
            print("-" * 80)
            for warning in self.warnings:
                print(warning)
        else:
            print(f"\n✅ 警告: 0件")
        
        # 結論
        print(f"\n{'=' * 80}")
        if len(self.errors) > 0:
            print("❌ バリデーション失敗: 処理を続行できません")
            print("上記のエラーを修正してから再実行してください。")
        elif len(self.warnings) > 0:
            print("⚠️  バリデーション成功（警告あり）: 処理を続行できます")
            print("警告を確認し、必要に応じてデータを修正することを推奨します。")
        else:
            print("✅ バリデーション成功: データ品質に問題ありません")
        print(f"{'=' * 80}\n")
