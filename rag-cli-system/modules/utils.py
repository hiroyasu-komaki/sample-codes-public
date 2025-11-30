"""
共通ユーティリティモジュール
ログ設定、出力抑制、埋め込みモデル、ドキュメントローダー等の共通機能を提供
"""

import os
import sys
import platform
import stat
import shutil
import subprocess
import warnings
from pathlib import Path
from typing import List
from contextlib import contextmanager
import io
import logging

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

# 全ての警告を非表示
warnings.filterwarnings('ignore')


@contextmanager
def suppress_output():
    """標準出力と標準エラー出力を一時的に抑制"""
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def setup_logging():
    """ロギング設定を初期化（ERROR以上のみ表示）"""
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
    logging.getLogger('chromadb').setLevel(logging.ERROR)
    logging.getLogger('langchain').setLevel(logging.ERROR)
    logging.getLogger('langchain_community').setLevel(logging.ERROR)


def create_embeddings_model():
    """
    埋め込みモデルを作成
    
    Returns:
        HuggingFaceEmbeddings: 日本語対応の埋め込みモデル
    """
    print("🤖 埋め込みモデルを初期化中...")
    
    with suppress_output():
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    
    return embeddings


def load_pdf_documents(pdf_folder: Path, logger: logging.Logger = None) -> List[Document]:
    """
    PDFフォルダから全てのPDFファイルを読み込む
    
    Args:
        pdf_folder: PDFファイルが格納されているフォルダ
        logger: ロガーインスタンス（オプション）
        
    Returns:
        読み込んだドキュメントのリスト
    """
    documents = []
    
    if not pdf_folder.exists():
        print(f"⚠️  PDFフォルダ '{pdf_folder}' が見つかりません。")
        return documents
    
    pdf_files = list(pdf_folder.glob("*.pdf"))
    
    if not pdf_files:
        print(f"ℹ️  PDFフォルダ '{pdf_folder}' にPDFファイルが見つかりません。")
        return documents
    
    print(f"📚 {len(pdf_files)} 個のPDFファイルを処理中...")
    
    for i, pdf_file in enumerate(pdf_files):
        try:
            print(f"📖 読み込み中: {pdf_file.name} ({i+1}/{len(pdf_files)})")
            
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            
            # ファイル名とタイプをメタデータに追加
            for doc in docs:
                doc.metadata['source_file'] = pdf_file.name
                doc.metadata['file_path'] = str(pdf_file)
                doc.metadata['file_type'] = 'pdf'
            
            documents.extend(docs)
            
            print(f"✅ 完了: {pdf_file.name} ({len(docs)} ページ)")
            
        except Exception as e:
            print(f"❌ エラー - {pdf_file.name}: {str(e)}")
            if logger:
                logger.error(f"PDF読み込みエラー - {pdf_file.name}: {str(e)}")
    
    return documents


def load_txt_documents(txt_folder: Path, logger: logging.Logger = None) -> List[Document]:
    """
    TXTフォルダから全てのTXTファイルを読み込む
    
    Args:
        txt_folder: TXTファイルが格納されているフォルダ
        logger: ロガーインスタンス（オプション）
        
    Returns:
        読み込んだドキュメントのリスト
    """
    documents = []
    
    if not txt_folder.exists():
        print(f"⚠️  TXTフォルダ '{txt_folder}' が見つかりません。")
        return documents
    
    txt_files = list(txt_folder.glob("*.txt"))
    
    if not txt_files:
        print(f"ℹ️  TXTフォルダ '{txt_folder}' にTXTファイルが見つかりません。")
        return documents
    
    print(f"📝 {len(txt_files)} 個のTXTファイルを処理中...")
    
    for i, txt_file in enumerate(txt_files):
        try:
            print(f"📄 読み込み中: {txt_file.name} ({i+1}/{len(txt_files)})")
            
            # UTF-8でテキストファイルを読み込み
            loader = TextLoader(str(txt_file), encoding='utf-8')
            docs = loader.load()
            
            # ファイル名とタイプをメタデータに追加
            for doc in docs:
                doc.metadata['source_file'] = txt_file.name
                doc.metadata['file_path'] = str(txt_file)
                doc.metadata['file_type'] = 'txt'
            
            documents.extend(docs)
            
            print(f"✅ 完了: {txt_file.name}")
            
        except Exception as e:
            print(f"❌ エラー - {txt_file.name}: {str(e)}")
            if logger:
                logger.error(f"TXT読み込みエラー - {txt_file.name}: {str(e)}")
    
    return documents


def load_md_documents(md_folder: Path, logger: logging.Logger = None) -> List[Document]:
    """
    MDフォルダから全てのMarkdownファイルを読み込む
    
    Args:
        md_folder: MDファイルが格納されているフォルダ
        logger: ロガーインスタンス（オプション）
        
    Returns:
        読み込んだドキュメントのリスト
    """
    documents = []
    
    if not md_folder.exists():
        print(f"⚠️  MDフォルダ '{md_folder}' が見つかりません。")
        return documents
    
    md_files = list(md_folder.glob("*.md"))
    
    if not md_files:
        print(f"ℹ️  MDフォルダ '{md_folder}' にMDファイルが見つかりません。")
        return documents
    
    print(f"📋 {len(md_files)} 個のMDファイルを処理中...")
    
    for i, md_file in enumerate(md_files):
        try:
            print(f"📃 読み込み中: {md_file.name} ({i+1}/{len(md_files)})")
            
            # シンプルなテキストローダーを使用（Markdown構造は保持）
            loader = TextLoader(str(md_file), encoding='utf-8')
            docs = loader.load()
            
            # ファイル名とタイプをメタデータに追加
            for doc in docs:
                doc.metadata['source_file'] = md_file.name
                doc.metadata['file_path'] = str(md_file)
                doc.metadata['file_type'] = 'md'
            
            documents.extend(docs)
            
            print(f"✅ 完了: {md_file.name}")
            
        except Exception as e:
            print(f"❌ エラー - {md_file.name}: {str(e)}")
            if logger:
                logger.error(f"MD読み込みエラー - {md_file.name}: {str(e)}")
    
    return documents


def load_all_documents(
    pdf_folder: Path, 
    txt_folder: Path, 
    md_folder: Path,
    logger: logging.Logger = None
) -> List[Document]:
    """
    全てのドキュメント（PDF、TXT、MD）を読み込む
    
    Args:
        pdf_folder: PDFフォルダ
        txt_folder: TXTフォルダ
        md_folder: MDフォルダ
        logger: ロガーインスタンス（オプション）
        
    Returns:
        全てのドキュメントのリスト
    """
    all_documents = []
    
    # PDF読み込み
    pdf_docs = load_pdf_documents(pdf_folder, logger)
    all_documents.extend(pdf_docs)
    
    # TXT読み込み
    txt_docs = load_txt_documents(txt_folder, logger)
    all_documents.extend(txt_docs)
    
    # MD読み込み
    md_docs = load_md_documents(md_folder, logger)
    all_documents.extend(md_docs)
    
    # サマリー表示
    print("\n" + "=" * 60)
    print("📊 読み込みサマリー")
    print("=" * 60)
    print(f"📚 PDFファイル: {len(pdf_docs)} ドキュメント")
    print(f"📝 TXTファイル: {len(txt_docs)} ドキュメント")
    print(f"📋 MDファイル: {len(md_docs)} ドキュメント")
    print(f"📄 総ドキュメント数: {len(all_documents)}")
    print("=" * 60 + "\n")
    
    return all_documents


def safe_remove_directory(directory: Path):
    """
    安全なディレクトリ削除（権限問題対応）
    
    Args:
        directory: 削除するディレクトリ
    """
    try:
        # 全てのファイルに書き込み権限を付与
        for root, dirs, files in os.walk(directory):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                os.chmod(dir_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            for file_name in files:
                file_path = os.path.join(root, file_name)
                os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        
        # ディレクトリを削除
        shutil.rmtree(directory, ignore_errors=True)
        
    except Exception as e:
        # macOSでターミナルコマンドでforce削除
        if platform.system() == 'Darwin':
            try:
                result = subprocess.run(
                    ['rm', '-rf', str(directory)], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode != 0:
                    raise Exception(f"削除エラー: {result.stderr}")
            except Exception as subprocess_error:
                raise Exception(f"安全削除エラー: {str(e)}, subprocess削除エラー: {str(subprocess_error)}")
        else:
            raise Exception(f"安全削除エラー: {str(e)}")


def ensure_folders_exist(pdf_folder: Path, txt_folder: Path, md_folder: Path, db_folder: Path):
    """
    必要なフォルダが存在することを確認し、なければ作成
    
    Args:
        pdf_folder: PDFフォルダ
        txt_folder: TXTフォルダ
        md_folder: MDフォルダ
        db_folder: データベースフォルダ
    """
    pdf_folder.mkdir(parents=True, exist_ok=True)
    txt_folder.mkdir(parents=True, exist_ok=True)
    md_folder.mkdir(parents=True, exist_ok=True)
    db_folder.mkdir(parents=True, exist_ok=True)
