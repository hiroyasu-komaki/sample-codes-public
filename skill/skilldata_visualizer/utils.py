"""
ユーティリティモジュール

共通機能や設定を提供
"""

import matplotlib.pyplot as plt
from matplotlib import font_manager
import sys
from pathlib import Path


def setup_japanese_font():
    """日本語フォントを設定"""
    try:
        # 利用可能なフォント一覧を取得
        font_names = [f.name for f in font_manager.fontManager.ttflist]
        
        # 日本語フォントの候補（優先順）
        japanese_fonts = [
            'Hiragino Sans',           # macOS
            'Hiragino Kaku Gothic Pro', # macOS
            'Yu Gothic',               # Windows/macOS
            'Yu Gothic UI',            # Windows
            'Meiryo',                  # Windows
            'MS Gothic',               # Windows
            'Noto Sans CJK JP',        # Linux
            'IPAexGothic',             # Linux
            'IPAPGothic',              # Linux
            'VL PGothic',              # Linux
            'DejaVu Sans'              # フォールバック
        ]
        
        # 利用可能な日本語フォントを検索
        available_font = None
        for font in japanese_fonts:
            if any(font in name for name in font_names):
                available_font = font
                break
        
        if available_font and available_font != 'DejaVu Sans':
            plt.rcParams['font.family'] = [available_font]
        # フォント設定メッセージを削除（サイレント設定）
            
        # マイナス記号の文字化け対策
        plt.rcParams['axes.unicode_minus'] = False
        
        # その他のmatplotlib設定
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['legend.fontsize'] = 9
        
    except Exception as e:
        # エラー時のみメッセージ表示
        print(f"警告: フォント設定でエラーが発生しました: {e}")


def check_dependencies():
    """必要なライブラリの存在確認"""
    required_packages = {
        'pandas': 'データ処理',
        'matplotlib': '基本グラフ作成',
        'seaborn': '統計可視化',
        'numpy': '数値計算'
    }
    
    optional_packages = {
        'plotly': 'インタラクティブグラフ'
    }
    
    missing_required = []
    missing_optional = []
    
    # 必須パッケージの確認
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"{package}: {description}")
        except ImportError:
            missing_required.append(package)
            print(f"{package}: {description} - 未インストール")
    
    # オプションパッケージの確認
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"{package}: {description}")
        except ImportError:
            missing_optional.append(package)
            print(f"{package}: {description} - 未インストール (オプション)")
    
    if missing_required:
        print(f"\n必須パッケージが不足しています: {', '.join(missing_required)}")
        print("以下のコマンドでインストールしてください:")
        print(f"pip install {' '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\nオプション機能が制限されます: {', '.join(missing_optional)}")
        print("フル機能を使用するには以下をインストール:")
        print(f"pip install {' '.join(missing_optional)}")
    
    return True


def get_system_info():
    """システム情報を表示"""
    print(f"\nシステム情報:")
    print(f"Python バージョン: {sys.version.split()[0]}")
    print(f"プラットフォーム: {sys.platform}")
    print(f"作業ディレクトリ: {Path.cwd()}")
    
    # Matplotlibバックエンド情報
    try:
        backend = plt.get_backend()
        print(f"Matplotlib バックエンド: {backend}")
    except:
        print("Matplotlib バックエンド: 取得できませんでした")


def validate_csv_structure(df):
    """CSVファイルの構造を検証"""
    import pandas as pd
    
    required_columns = [
        'カテゴリー', 'サブカテゴリー', 'スキル項目', 
        'ロール', '専門性', 'スキルレベル', 'スキルレベル_数値'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"必要なカラムが不足しています: {missing_columns}")
        print(f"現在のカラム: {list(df.columns)}")
        return False
    
    # データ型チェック
    issues = []
    
    # 文字列カラムの確認
    string_columns = ['カテゴリー', 'サブカテゴリー', 'スキル項目', 'ロール', '専門性', 'スキルレベル']
    for col in string_columns:
        if col in df.columns and not df[col].dtype == 'object':
            issues.append(f"'{col}'が文字列型ではありません")
    
    # 数値カラムの確認
    if 'スキルレベル_数値' in df.columns:
        numeric_col = df['スキルレベル_数値']
        if not pd.api.types.is_numeric_dtype(numeric_col):
            issues.append("'スキルレベル_数値'が数値型ではありません")
        else:
            # 数値範囲チェック
            min_val, max_val = numeric_col.min(), numeric_col.max()
            if min_val < 0 or max_val > 10:
                issues.append(f"'スキルレベル_数値'の範囲が異常です (最小: {min_val}, 最大: {max_val})")
    
    if issues:
        print("データ構造に関する問題:")
        for issue in issues:
            print(f"• {issue}")
        return False
    
    print("データ構造の検証完了")
    return True


def create_output_directory(base_dir="output"):
    """出力ディレクトリを作成"""
    output_path = Path(base_dir)
    plots_path = output_path / "plots"
    reports_path = output_path / "reports"
    
    try:
        plots_path.mkdir(parents=True, exist_ok=True)
        reports_path.mkdir(parents=True, exist_ok=True)
        
        print(f"出力ディレクトリを作成しました:")
        print(f"グラフ: {plots_path}")
        print(f"レポート: {reports_path}")
        
        return output_path, plots_path, reports_path
    
    except Exception as e:
        print(f"ディレクトリ作成エラー: {e}")
        return None, None, None


def format_number(num):
    """数値を読みやすい形式でフォーマット"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(int(num))


def safe_division(numerator, denominator, default=0):
    """安全な除算（ゼロ除算対策）"""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default


def truncate_text(text, max_length=30, suffix="..."):
    """テキストを指定長で切り詰め"""
    if isinstance(text, str) and len(text) > max_length:
        return text[:max_length - len(suffix)] + suffix
    return str(text)


def get_color_palette(n_colors=6, palette_name='husl'):
    """カラーパレットを取得"""
    try:
        import seaborn as sns
        return sns.color_palette(palette_name, n_colors)
    except ImportError:
        # seabornが利用できない場合のフォールバック
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        return colors[:n_colors] if n_colors <= len(colors) else colors * (n_colors // len(colors) + 1)


def print_progress(current, total, prefix="Progress", bar_length=50):
    """プログレスバーを表示"""
    percent = current / total
    filled_length = int(bar_length * percent)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f'\r{prefix}: |{bar}| {current}/{total} ({percent:.1%})', end='', flush=True)
    if current == total:
        print()  # 完了時に改行