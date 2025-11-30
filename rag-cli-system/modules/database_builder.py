"""
データベース構築専用モジュール
ドキュメントの読み込み、ベクトル化、データベース構築を担当
"""

import time
import logging
from pathlib import Path
from typing import Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from .utils import (
    setup_logging,
    create_embeddings_model,
    load_all_documents,
    safe_remove_directory,
    ensure_folders_exist,
    suppress_output
)


class DatabaseBuilder:
    """
    ベクトルデータベース構築クラス
    ドキュメントの読み込み、ベクトル化、データベース構築を担当
    """
    
    def __init__(
        self, 
        pdf_folder: str = "data/pdf",
        txt_folder: str = "data/txt", 
        md_folder: str = "data/md",
        db_folder: str = "vectordb",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        collection_name: str = "rag_documents",
        verbose: bool = True
    ):
        """
        初期化
        
        Args:
            pdf_folder: PDFファイルが格納されているフォルダ
            txt_folder: TXTファイルが格納されているフォルダ
            md_folder: MDファイルが格納されているフォルダ
            db_folder: ベクトルデータベースを保存するフォルダ
            chunk_size: テキスト分割時のチャンクサイズ
            chunk_overlap: チャンク間のオーバーラップ文字数
            collection_name: Chromaコレクション名
            verbose: 詳細ログを出力するかどうか
        """
        self.pdf_folder = Path(pdf_folder)
        self.txt_folder = Path(txt_folder)
        self.md_folder = Path(md_folder)
        self.db_folder = Path(db_folder)
        self.collection_name = collection_name
        self.verbose = verbose
        
        # ロギング設定
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # フォルダ作成
        ensure_folders_exist(
            self.pdf_folder, 
            self.txt_folder, 
            self.md_folder, 
            self.db_folder
        )
        
        # 埋め込みモデルを初期化
        self.embeddings = create_embeddings_model()
        
        # テキスト分割設定
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def build_database(self) -> bool:
        """
        データベースを新規構築
        
        Returns:
            成功した場合True、失敗した場合False
        """
        try:
            print("🔨 データベースを構築中...")
            
            # 既存のデータベースが存在する場合は警告
            if self.db_folder.exists() and any(self.db_folder.iterdir()):
                print("⚠️  既存のデータベースが検出されました。")
                print("💡 rebuild_database() を使用して再構築してください。")
                return False
            
            # ドキュメントを読み込み
            documents = load_all_documents(
                self.pdf_folder,
                self.txt_folder,
                self.md_folder,
                self.logger
            )
            
            if not documents:
                print("⚠️  ドキュメントが見つかりません。")
                return False
            
            # テキストを分割
            texts = self.text_splitter.split_documents(documents)
            print(f"📄 テキストを {len(texts)} 個のチャンクに分割しました。")
            
            # ベクトルストアを作成
            print("🔄 Chromaベクトルデータベースを作成中...")
            with suppress_output():
                vectorstore = Chroma.from_documents(
                    documents=texts,
                    embedding=self.embeddings,
                    persist_directory=str(self.db_folder),
                    collection_name=self.collection_name
                )
            
            print("🎉 ベクトルデータベースの作成が完了しました！")
            print(f"📊 保存されたドキュメント数: {len(texts)}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ データベース構築エラー: {str(e)}")
            self.logger.error(f"データベース構築エラー: {str(e)}")
            return False
    
    def rebuild_database(self) -> bool:
        """
        データベースを再構築（既存を削除して新規作成）
        
        Returns:
            成功した場合True、失敗した場合False
        """
        try:
            print("🔄 データベースを再構築中...")
            
            # 既存のデータベースを削除
            if self.db_folder.exists():
                print("🗑️  既存のデータベースを削除中...")
                safe_remove_directory(self.db_folder)
                print("✅ 既存のデータベースを削除しました")
                
                # 削除完了を確実にするため待機
                time.sleep(1)
            
            # 新しいディレクトリを作成
            self.db_folder.mkdir(parents=True, exist_ok=True)
            
            # ドキュメントを読み込み
            documents = load_all_documents(
                self.pdf_folder,
                self.txt_folder,
                self.md_folder,
                self.logger
            )
            
            if not documents:
                print("⚠️  再構築するドキュメントが見つかりません。")
                return False
            
            # テキストを分割
            texts = self.text_splitter.split_documents(documents)
            print(f"📄 テキストを {len(texts)} 個のチャンクに分割しました。")
            
            # ベクトルストアを作成
            print("🔄 Chromaベクトルデータベースを作成中...")
            with suppress_output():
                vectorstore = Chroma.from_documents(
                    documents=texts,
                    embedding=self.embeddings,
                    persist_directory=str(self.db_folder),
                    collection_name=self.collection_name
                )
            
            print("🎉 ベクトルデータベースの作成が完了しました！")
            print(f"📊 保存されたドキュメント数: {len(texts)}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ データベース再構築エラー: {str(e)}")
            print("\n💡 解決方法:")
            print(f"   1. プログラムを終了してください (Ctrl+C)")
            print(f"   2. 以下のコマンドでデータベースを削除してください:")
            print(f"      rm -rf {self.db_folder}")
            print(f"   3. プログラムを再起動してください")
            self.logger.error(f"データベース再構築エラー: {str(e)}")
            return False
    
    def get_folder_info(self) -> dict:
        """
        フォルダ情報を取得
        
        Returns:
            フォルダ情報の辞書
        """
        return {
            'pdf_folder': str(self.pdf_folder),
            'txt_folder': str(self.txt_folder),
            'md_folder': str(self.md_folder),
            'db_folder': str(self.db_folder),
            'pdf_count': len(list(self.pdf_folder.glob("*.pdf"))) if self.pdf_folder.exists() else 0,
            'txt_count': len(list(self.txt_folder.glob("*.txt"))) if self.txt_folder.exists() else 0,
            'md_count': len(list(self.md_folder.glob("*.md"))) if self.md_folder.exists() else 0,
        }
