import pandas as pd
import os
from datetime import datetime

def read_docs_excel():
    # スクリプトファイルの場所を基準にパスを構築
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xls_path = os.path.join(script_dir, 'docs/業務棚卸しスプレッドシート.xlsx')
    
    # print(f"スクリプトの場所: {script_dir}")
    # print(f"探しているファイル: {xls_path}")
    
    try:
        # Excelファイル読み込み（シート名指定、ヘッダーを2行目に設定、200行まで読み込み）
        df = pd.read_excel(xls_path, sheet_name='業務棚卸し', header=1, nrows=200)
        print("=" * 50)
        print("業務棚卸しスプレッドシート読み込み成功!")
        print("=" * 50)
        print(f"読み込み後のデータ形状: {df.shape}")
        
        # 空白行を削除
        df_cleaned = df.dropna(how='all')  # 全ての列が空白の行を削除
        
        # print(f"空白行削除後のデータ形状: {df_cleaned.shape}")
        # print(f"削除された行数: {df.shape[0] - df_cleaned.shape[0]}")
        # print(f"列名: {list(df_cleaned.columns)}")
        
        # print("\n--- 最初の10行 ---")
        # print(df_cleaned.head(10))
        
        # print("\n--- データ型情報 ---")
        # print(df_cleaned.info())
        
        # 必要に応じて、さらに詳細な空白処理
        # df_cleaned = df_cleaned.dropna(subset=['重要な列名'])  # 特定の列が空白の行を削除
        # df_cleaned = df_cleaned.dropna()  # いずれかの列が空白の行を全て削除
        
        # outフォルダにCSV出力
        output_dir = os.path.join(script_dir, 'out')
        
        # outフォルダが存在しない場合は作成
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"\noutフォルダを作成しました: {output_dir}")
        
        # タイムスタンプ付きのファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f'業務棚卸し_{timestamp}.csv'
        csv_path = os.path.join(output_dir, csv_filename)
        
        # CSV出力（UTF-8 BOM付きで出力してExcelで文字化けを防ぐ）
        df_cleaned.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # print("\n" + "=" * 50)
        print("CSV出力成功!")
        # print("=" * 50)
        print(f"出力先: {csv_path}")
        print(f"出力行数: {len(df_cleaned)}")
        
        # JSON出力
        json_filename = f'業務棚卸し_{timestamp}.json'
        json_path = os.path.join(output_dir, json_filename)
        
        # JSON出力（日本語をそのまま出力、インデント付き）
        df_cleaned.to_json(json_path, orient='records', force_ascii=False, indent=2)
        
        # print("\n" + "=" * 50)
        print("JSON出力成功!")
        # print("=" * 50)
        print(f"出力先: {json_path}")
        print(f"出力行数: {len(df_cleaned)}")
        
        return df_cleaned
        
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {xls_path}")
        # デバッグ用：docsディレクトリにあるファイル一覧を表示
        docs_dir = os.path.join(script_dir, 'docs')
        if os.path.exists(docs_dir):
            print("docsディレクトリのファイル:")
            for file in os.listdir(docs_dir):
                print(f"  - {file}")
        else:
            print("docsディレクトリが存在しません")
        return None
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None