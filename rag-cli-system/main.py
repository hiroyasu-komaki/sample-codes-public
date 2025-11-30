#!/usr/bin/env python3
"""
コマンドライン版RAG検索システム（対話型・拡張版）
PDF、TXT、MDファイル対応
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 分割されたクラスをインポート
from modules.database_builder import DatabaseBuilder
from modules.database_searcher import DatabaseSearcher

def print_banner():
    """バナー表示"""
    print("=" * 60)
    print("🔍 ローカルRAG検索システム (対話型・拡張版)")
    print("Powered by Chroma Vector Database")
    print("対応フォーマット: PDF / TXT / MD")
    print("=" * 60)


def print_menu():
    """メインメニュー表示"""
    print("\n" + "=" * 60)
    print("📋 メニュー")
    print("=" * 60)
    print("1. ベクトルデータベースを再構築")
    print("2. ベクトルデータベースを検索")
    print("9. プログラムを終了")
    print("=" * 60)


def get_menu_choice() -> str:
    """メニュー選択を取得"""
    while True:
        choice = input("\n選択してください (1/2/9): ").strip()
        if choice in ['1', '2', '9']:
            return choice
        else:
            print("⚠️  1, 2, または 9 を入力してください。")


def print_search_results(results: List[Dict[str, Any]], query: str, show_scores: bool = True, output_file: str = None):
    """検索結果を整形して表示・保存"""
    output_content = []
    
    # 検索ワードを追加
    search_info = [
        f"🔍 検索ワード: \"{query}\"",
        ""
    ]
    
    if not results:
        message = [
            f"⚠️  「{query}」に関連する文書が見つかりませんでした。",
            "",
            "検索のヒント:",
            "• より具体的なキーワードを使用してみてください",
            "• 異なる表現や同義語を試してみてください",
            "• より短いフレーズで検索してみてください"
        ]
        
        # コンソール出力
        for line in search_info + message:
            print(line)
        
        # ファイル出力
        output_content = search_info + message
    else:
        # スコア分布から動的に閾値を計算
        scores = [r['similarity_score'] for r in results]
        if len(scores) > 1:
            min_score = min(scores)
            max_score = max(scores)
            range_score = max_score - min_score
            threshold_high = min_score + range_score * 0.33
            threshold_mid = min_score + range_score * 0.67
        else:
            # 結果が1件の場合は固定値
            threshold_high = 10.0
            threshold_mid = 20.0
        
        header = [
            f"✅ 「{query}」に関連する {len(results)} 件の文書が見つかりました。",
            f"📊 動的閾値: 高類似度 < {threshold_high:.4f}, 中類似度 < {threshold_mid:.4f}",
            "=" * 60
        ]
        
        # コンソール出力
        for line in search_info + header:
            print(line)
        
        # ファイル出力用
        output_content.extend(search_info + header)
        
        for i, result in enumerate(results, 1):
            score = result['similarity_score']
            file_type = result['file_type']
            
            # ファイルタイプに応じたアイコン
            type_icons = {
                'pdf': '📕',
                'txt': '📝',
                'md': '📋'
            }
            type_icon = type_icons.get(file_type, '📄')
            
            # スコアに応じてアイコンを変更（動的閾値）
            if score < threshold_high:
                console_icon = "🎯"
                file_icon = "[高類似度]"
            elif score < threshold_mid:
                console_icon = "📄"
                file_icon = "[中類似度]"
            else:
                console_icon = "📋"
                file_icon = "[低類似度]"
            
            console_lines = [f"\n{console_icon} {type_icon} 結果 {i}: {result['source_file']} ({file_type.upper()})"]
            file_lines = [f"\n{file_icon} 結果 {i}: {result['source_file']} ({file_type.upper()})"]
            
            if show_scores:
                score_line = f"   類似度スコア: {score:.4f}"
                console_lines.append(score_line)
                file_lines.append(score_line)
            
            # PDFの場合のみページ番号を表示
            if file_type == 'pdf' and result['page'] != 'N/A':
                page_line = f"   ページ: {result['page'] + 1}"
                console_lines.append(page_line)
                file_lines.append(page_line)
            
            console_lines.append("   内容:")
            file_lines.append("   内容:")
            
            # 内容を80文字で折り返し表示
            content = result['content']
            words = content.split()
            line = ""
            for word in words:
                if len(line + word) > 80:
                    content_line = f"   {line}"
                    console_lines.append(content_line)
                    file_lines.append(content_line)
                    line = word + " "
                else:
                    line += word + " "
            if line:
                content_line = f"   {line}"
                console_lines.append(content_line)
                file_lines.append(content_line)
            
            separator = "-" * 60
            console_lines.append(separator)
            file_lines.append(separator)
            
            # コンソール出力
            for line in console_lines:
                print(line)
            
            # ファイル出力用
            output_content.extend(file_lines)
    
    # ファイルに保存
    if output_file:
        try:
            # resultsフォルダを作成
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)
            
            # ファイルパスを構築
            output_path = results_dir / output_file
            
            # 検索情報をヘッダーに追加
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header_info = [
                f"検索実行日時: {timestamp}",
                f"検索結果ファイル: {output_file}",
                "=" * 60,
                ""
            ]
            
            # ヘッダー + 検索結果を結合
            full_content = header_info + output_content
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(full_content))
            
            print(f"\n💾 検索結果を保存しました: {output_path}")
            
        except Exception as e:
            print(f"❌ ファイル保存エラー: {str(e)}")


def generate_output_filename(query: str) -> str:
    """検索クエリから出力ファイル名を生成"""
    # 現在時刻を取得
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # クエリを安全なファイル名に変換
    safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_query = safe_query.replace(' ', '_')[:30]  # 30文字制限
    
    # ファイル名を生成
    filename = f"search_{timestamp}_{safe_query}.txt"
    return filename


def run_search_mode(searcher: DatabaseSearcher):
    """検索モードを実行"""
    print("\n✅ 準備完了！すべてのファイルタイプから検索します。")
    
    # 検索ループ
    while True:
        print("\n" + "=" * 60)
        query = input("🔍 検索ワードを入力してください (メニューに戻る: 'menu', 終了: 'exit'): ").strip()
        
        # メニューに戻る
        if query.lower() == 'menu':
            return 'menu'
        
        # 終了条件
        if query.lower() in ['exit', 'quit', '']:
            return 'exit'
        
        # 検索実行（固定5件）
        print(f"\n🔍 検索中: '{query}'")
        results = searcher.search(query, k=5)
        
        # 出力ファイル名を生成
        output_file = generate_output_filename(query)
        
        # 結果表示
        print()
        print_search_results(
            results, 
            query,
            show_scores=True, 
            output_file=output_file
        )


def main():
    # バナー表示
    print_banner()
    
    try:
        print(f"📁 PDFフォルダ: data/pdf")
        print(f"📁 TXTフォルダ: data/txt")
        print(f"📁 MDフォルダ: data/md")
        print(f"💾 データベースフォルダ: vectordb")
        print()
        
        # DatabaseBuilderとDatabaseSearcherを初期化
        builder = DatabaseBuilder(
            pdf_folder="data/pdf",
            txt_folder="data/txt",
            md_folder="data/md",
            db_folder="vectordb",
            verbose=True
        )
        print()
        
        searcher = DatabaseSearcher(
            db_folder="vectordb",
            verbose=True
        )
        print()
        
        # メインループ
        while True:
            # メニュー表示
            print_menu()
            choice = get_menu_choice()
            
            if choice == '1':
                # データベース再構築
                print("\n🔄 データベースを再構築します...")
                try:
                    success = builder.rebuild_database()
                    if success:
                        print("✅ データベースの再構築が完了しました。")
                    else:
                        print("❌ データベースの再構築に失敗しました。")
                        print("メニューに戻ります。")
                    
                except Exception as e:
                    print("\n❌ データベース再構築に失敗しました。")
                    print(f"エラー: {str(e)}")
                    print("メニューに戻ります。")
                    continue
                    
            elif choice == '2':
                # 既存のベクトルストアを読み込み
                print("\n📂 既存のデータベースを読み込みます...")
                try:
                    if searcher.load_database():
                        print()
                        
                        # 検索モードへ
                        result = run_search_mode(searcher)
                        if result == 'exit':
                            print("\n👋 プログラムを終了します。")
                            break
                    else:
                        print("メニューに戻ります。")
                    
                except Exception as e:
                    print("\n❌ データベース読み込みに失敗しました。")
                    print(f"エラー: {str(e)}")
                    print("メニューに戻ります。")
                    continue
                    
            elif choice == '9':
                # 終了
                print("\n👋 プログラムを終了します。")
                break
            
    except KeyboardInterrupt:
        print("\n\n👋 プログラムを終了します。")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()