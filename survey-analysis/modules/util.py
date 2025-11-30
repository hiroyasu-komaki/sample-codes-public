"""
ユーティリティ関数モジュール（代表性検証表示機能追加版）
共通で使用される補助関数を提供
"""


def print_statistics(stats: dict, title: str = "統計情報"):
    """
    統計情報を標準出力
    
    Args:
        stats: 統計情報の辞書
        title: 統計情報のタイトル
    """
    print("\n" + "-"*70)
    print(title)
    print("-"*70)
    
    # 総サンプル数
    if 'total_samples' in stats:
        print(f"総サンプル数: {stats['total_samples']}件")
    
    # 満足度評価の統計
    if stats.get('satisfaction_ratings'):
        print("\n満足度評価の統計:")
        print(f"{'項目':<35} {'平均':<8} {'標準偏差':<8}")
        print("-" * 70)
        
        for key, data in stats['satisfaction_ratings'].items():
            print(f"{key:<35} {data['mean']:<8.2f} {data['std']:<8.2f}")
    
    # 重要度評価の統計
    if stats.get('importance_ratings'):
        print("\n重要度評価の統計:")
        print(f"{'項目':<35} {'平均':<8} {'標準偏差':<8}")
        print("-" * 70)
        
        for key, data in stats['importance_ratings'].items():
            print(f"{key:<35} {data['mean']:<8.2f} {data['std']:<8.2f}")
    
    print("-" * 70)


def print_representativeness_report(representativeness: dict):
    """
    代表性検証結果を標準出力
    
    Args:
        representativeness: 代表性検証結果の辞書
    """
    if not representativeness:
        return
    
    print("\n" + "="*70)
    print("代表性検証結果")
    print("="*70)
    
    for attr, report in representativeness.items():
        print(f"\n【{attr}】")
        print(f"  総合判定: {report['status']} (最大乖離: ±{report['max_deviation']:.1f}%)")
        print(f"  総回答数: {report['total_responses']}名")
        print()
        print(f"  {'カテゴリ':<20} {'母集団':<10} {'回答者':<10} {'乖離':<10} {'実数':<8}")
        print("  " + "-"*60)
        
        for category, deviation in report['deviations'].items():
            expected = deviation['expected_pct']
            actual = deviation['actual_pct']
            diff = deviation['deviation_pct']
            count = deviation['actual_count']
            
            # 乖離が大きい場合は警告マーク
            warning = " ⚠️" if abs(diff) > 5.0 else ""
            
            print(f"  {category:<20} {expected:>6.1f}%  {actual:>6.1f}%  "
                  f"{diff:>+6.1f}%  {count:>6}名{warning}")
    
    # 総合判定サマリー
    print("\n" + "-"*70)
    print("総合評価:")
    
    good_count = sum(1 for r in representativeness.values() if r['status_en'] == 'good')
    acceptable_count = sum(1 for r in representativeness.values() if r['status_en'] == 'acceptable')
    needs_adjustment_count = sum(1 for r in representativeness.values() if r['status_en'] == 'needs_adjustment')
    
    total = len(representativeness)
    
    print(f"  良好: {good_count}/{total}項目")
    print(f"  許容範囲: {acceptable_count}/{total}項目")
    print(f"  要調整: {needs_adjustment_count}/{total}項目")
    
    if needs_adjustment_count == 0:
        print("\n  ✓ すべての属性で良好または許容範囲内の代表性が確保されています。")
    elif needs_adjustment_count <= total * 0.3:
        print("\n  △ 一部の属性で代表性に偏りがありますが、全体としては許容範囲です。")
    else:
        print("\n  ✗ 複数の属性で代表性に問題があります。結果の解釈に注意が必要です。")
    
    print("="*70)


def print_preprocessing_summary(preprocessor):
    """
    前処理サマリーを標準出力
    
    Args:
        preprocessor: DataPreprocessorインスタンス
    """
    print("\n" + "-"*70)
    print("前処理結果サマリー")
    print("-"*70)
    
    # データサイズ
    if preprocessor.raw_data is not None and preprocessor.processed_data is not None:
        print(f"データサイズ: {preprocessor.raw_data.shape[0]}行 → {preprocessor.processed_data.shape[0]}行")
        print(f"カラム数: {preprocessor.raw_data.shape[1]}列 → {preprocessor.processed_data.shape[1]}列")
    
    # 標準化前後の統計比較
    report = preprocessor.preprocessing_report
    if 'standardization' in report and report['standardization']:
        # 満足度評価の統計
        satisfaction_items = {}
        importance_items = {}
        
        for col, info in report['standardization'].items():
            if 'importance' in col:
                importance_items[col] = info
            else:
                satisfaction_items[col] = info
        
        # 満足度評価
        if satisfaction_items:
            print("\n満足度評価の統計:")
            print(f"{'項目':<35} {'前処理前':<18} {'前処理後（リスケール）':<18}")
            print(f"{'':<35} {'平均':<8} {'標準偏差':<8} {'平均':<8} {'標準偏差':<8}")
            print("-" * 70)
            
            for col, info in satisfaction_items.items():
                # 前処理前の統計
                before_mean = info['mean']
                before_std = info['std']
                
                # 前処理後の統計（リスケール）
                rescaled_col = info.get('rescaled_column', f'{col}_rescaled')
                if rescaled_col in preprocessor.processed_data.columns:
                    after_mean = preprocessor.processed_data[rescaled_col].mean()
                    after_std = preprocessor.processed_data[rescaled_col].std()
                else:
                    after_mean = before_mean
                    after_std = before_std
                
                print(f"{col:<35} {before_mean:<8.2f} {before_std:<8.2f} {after_mean:<8.2f} {after_std:<8.2f}")
        
        # 重要度評価
        if importance_items:
            print("\n重要度評価の統計:")
            print(f"{'項目':<35} {'前処理前':<18} {'前処理後（リスケール）':<18}")
            print(f"{'':<35} {'平均':<8} {'標準偏差':<8} {'平均':<8} {'標準偏差':<8}")
            print("-" * 70)
            
            for col, info in importance_items.items():
                # 前処理前の統計
                before_mean = info['mean']
                before_std = info['std']
                
                # 前処理後の統計（リスケール）
                rescaled_col = info.get('rescaled_column', f'{col}_rescaled')
                if rescaled_col in preprocessor.processed_data.columns:
                    after_mean = preprocessor.processed_data[rescaled_col].mean()
                    after_std = preprocessor.processed_data[rescaled_col].std()
                else:
                    after_mean = before_mean
                    after_std = before_std
                
                print(f"{col:<35} {before_mean:<8.2f} {before_std:<8.2f} {after_mean:<8.2f} {after_std:<8.2f}")
    
    # エンコーディング・欠損値処理のサマリー
    if 'encoding' in report and report['encoding']:
        encode_count = len(report['encoding'])
        print(f"\nエンコーディング済み項目: {encode_count}個")
    
    if 'missing_values' in report and report['missing_values']:
        total_missing = sum(
            v['count'] for v in report['missing_values'].values() 
            if isinstance(v, dict) and 'count' in v
        )
        print(f"欠損値処理: {total_missing}個")
    
    print("-" * 70)
    
    # 代表性検証結果の表示
    if 'representativeness' in report and report['representativeness']:
        print_representativeness_report(report['representativeness'])


def print_header(title: str, width: int = 70):
    """
    ヘッダーを標準出力
    
    Args:
        title: ヘッダータイトル
        width: ヘッダーの幅
    """
    print("\n" + "="*width)
    print(title)
    print("="*width)


def print_section(title: str, width: int = 70):
    """
    セクションヘッダーを標準出力
    
    Args:
        title: セクションタイトル
        width: セクションの幅
    """
    print("\n" + "-"*width)
    print(title)
    print("-"*width)


def print_success(message: str):
    """
    成功メッセージを標準出力
    
    Args:
        message: 成功メッセージ
    """
    print(f"\n✓ {message}")


def print_error(message: str):
    """
    エラーメッセージを標準出力
    
    Args:
        message: エラーメッセージ
    """
    print(f"\n❌ エラー: {message}")


def print_info(message: str):
    """
    情報メッセージを標準出力
    
    Args:
        message: 情報メッセージ
    """
    print(f"\n{message}")