"""
データベース検索専用モジュール
ベクトルデータベースからの検索機能を提供
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from langchain_community.vectorstores import Chroma

from .utils import (
    setup_logging,
    create_embeddings_model,
    suppress_output
)


class DatabaseSearcher:
    """
    ベクトルデータベース検索クラス
    既存のベクトルデータベースから類似検索を実行
    """
    
    def __init__(
        self, 
        db_folder: str = "vectordb",
        collection_name: str = "rag_documents",
        verbose: bool = True
    ):
        """
        初期化
        
        Args:
            db_folder: ベクトルデータベースが保存されているフォルダ
            collection_name: Chromaコレクション名
            verbose: 詳細ログを出力するかどうか
        """
        self.db_folder = Path(db_folder)
        self.collection_name = collection_name
        self.verbose = verbose
        
        # ロギング設定
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 埋め込みモデルを初期化
        self.embeddings = create_embeddings_model()
        
        # ベクトルストア
        self.vectorstore = None
    
    def load_database(self) -> bool:
        """
        既存のベクトルデータベースを読み込む
        
        Returns:
            成功した場合True、失敗した場合False
        """
        # Chromaデータベースファイルの存在確認
        chroma_db_path = self.db_folder / "chroma.sqlite3"
        
        if not chroma_db_path.exists():
            print(f"❌ データベースが見つかりません: {self.db_folder}")
            print("💡 先にデータベースを構築してください。")
            return False
        
        try:
            print("📂 既存のベクトルデータベースを読み込み中...")
            
            # 警告を抑制しながら既存のChromaデータベースを読み込み
            with suppress_output():
                self.vectorstore = Chroma(
                    persist_directory=str(self.db_folder),
                    embedding_function=self.embeddings,
                    collection_name=self.collection_name
                )
            
            # データベース動作確認
            try:
                test_results = self.vectorstore.similarity_search("test", k=1)
                print("✅ 既存のChromaデータベースを読み込みました。")
            except Exception as e:
                print(f"📊 データベースを読み込みました")
            
            return True
            
        except Exception as e:
            print(f"❌ データベース読み込みエラー: {str(e)}")
            self.logger.error(f"データベース読み込みエラー: {str(e)}")
            return False
    
    def search(
        self, 
        query: str, 
        k: int = 5, 
        filter_metadata: Optional[dict] = None
    ) -> List[Dict[str, Any]]:
        """
        類似検索を実行
        
        Args:
            query: 検索クエリ
            k: 取得する結果数
            filter_metadata: メタデータフィルター（例: {'file_type': 'pdf'}）
            
        Returns:
            検索結果のリスト
        """
        if not self.vectorstore:
            print("❌ ベクトルデータベースが読み込まれていません。")
            print("💡 先に load_database() を実行してください。")
            return []
        
        try:
            # メタデータフィルターがある場合
            if filter_metadata:
                docs_with_scores = self.vectorstore.similarity_search_with_score(
                    query, 
                    k=k,
                    filter=filter_metadata
                )
            else:
                docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs_with_scores:
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': score,
                    'source_file': doc.metadata.get('source_file', 'Unknown'),
                    'file_type': doc.metadata.get('file_type', 'Unknown'),
                    'page': doc.metadata.get('page', 'N/A')
                })
            
            return results
        
        except Exception as e:
            print(f"🔍 検索エラー: {str(e)}")
            self.logger.error(f"検索エラー: {str(e)}")
            return []
    
    def search_by_file_type(
        self, 
        query: str, 
        file_type: str, 
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        特定のファイルタイプに絞って検索
        
        Args:
            query: 検索クエリ
            file_type: ファイルタイプ ('pdf', 'txt', 'md')
            k: 取得する結果数
            
        Returns:
            検索結果のリスト
        """
        return self.search(query, k=k, filter_metadata={'file_type': file_type})
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        データベース統計情報を取得
        
        Returns:
            統計情報の辞書
        """
        if not self.vectorstore:
            print("❌ ベクトルデータベースが読み込まれていません。")
            return {}
        
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            # ファイル別・タイプ別統計
            results = collection.get()
            file_stats = {}
            type_stats = {'pdf': 0, 'txt': 0, 'md': 0}
            
            for metadata in results['metadatas']:
                source_file = metadata.get('source_file', 'Unknown')
                file_type = metadata.get('file_type', 'Unknown')
                
                file_stats[source_file] = file_stats.get(source_file, 0) + 1
                
                if file_type in type_stats:
                    type_stats[file_type] += 1
            
            return {
                'total_documents': count,
                'file_stats': file_stats,
                'type_stats': type_stats
            }
        except Exception as e:
            print(f"❌ 統計情報取得エラー: {str(e)}")
            self.logger.error(f"統計情報取得エラー: {str(e)}")
            return {}
    
    def is_loaded(self) -> bool:
        """
        データベースが読み込まれているかチェック
        
        Returns:
            読み込まれている場合True
        """
        return self.vectorstore is not None
