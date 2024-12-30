# .\user-app-docs\services\local_doc_service.py

import requests
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import DocsSettings
from dbschemas.docs_schema import Document
from dbschemas.doc_tags_schema import DocTag, DocTagLink
from dbschemas.local_doc_versions_schema import LocalDocVersion
from typing import Optional, List
import logging
from fastapi import UploadFile

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設定のロード
settings = DocsSettings()

class LocalDocService:
    @staticmethod
    def save_local_record(file: UploadFile, title: str, db: Session) -> Optional[int]:
        """
        アップロードされたファイルを読み込み、タイトルと内容をデータベースに保存します。
        """
        try:
            content = file.file.read().decode("utf-8")
            new_doc = Document(title=title, content=content)
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            logger.info(f"ドキュメント '{title}' がID {new_doc.id} で保存されました。")
            return new_doc.id
        except Exception as e:
            logger.error(f"ローカルレコードの保存中にエラーが発生しました: {e}")
            db.rollback()
            return None
        finally:
            file.file.close()

    @staticmethod
    def search_hub_docs(query: str, db: Session) -> Optional[List[str]]:
        """
        HubAppの /doc/search エンドポイントを呼び出して、RAG検索を実行します。
        """
        try:
            hub_url = settings.HUBAPP_URL
            endpoint = f"{hub_url}/doc/search"
            resp = requests.get(endpoint, params={"query": query})
            resp.raise_for_status()
            results = resp.json().get("results", [])
            logger.info(f"クエリ '{query}' のRAG検索が成功しました。結果: {results}")
            return results
        except requests.exceptions.RequestException as e:
            logger.error(f"HubAppの呼び出し中にエラーが発生しました: {e}")
            return None

    @staticmethod
    def add_tag_to_doc(doc_id: int, tag_name: str, db: Session) -> bool:
        """
        ドキュメントにタグを追加します。タグが存在しない場合は作成します。
        """
        try:
            tag = db.query(DocTag).filter_by(tag_name=tag_name).first()
            if not tag:
                tag = DocTag(tag_name=tag_name, description="")
                db.add(tag)
                db.commit()
                db.refresh(tag)
                logger.info(f"新しいタグ '{tag_name}' を作成しました。")

            link = db.query(DocTagLink).filter_by(doc_id=doc_id, tag_id=tag.tag_id).first()
            if link:
                logger.warning(f"タグ '{tag_name}' は既にドキュメントID {doc_id} にリンクされています。")
                return False

            link = DocTagLink(doc_id=doc_id, tag_id=tag.tag_id)
            db.add(link)
            db.commit()
            logger.info(f"タグ '{tag_name}' がドキュメントID {doc_id} に追加されました。")
            return True
        except Exception as e:
            logger.error(f"ドキュメントにタグを追加中にエラーが発生しました: {e}")
            db.rollback()
            return False

    @staticmethod
    def save_doc_version(doc_id: int, content: str, db: Session) -> Optional[int]:
        """
        更新された内容でドキュメントの新しいバージョンを保存します。
        """
        try:
            latest_version = db.query(LocalDocVersion).filter_by(doc_id=doc_id).order_by(LocalDocVersion.version_num.desc()).first()
            next_version = latest_version.version_num + 1 if latest_version else 1

            new_version = LocalDocVersion(doc_id=doc_id, version_num=next_version, content=content)
            db.add(new_version)
            db.commit()
            db.refresh(new_version)
            logger.info(f"ドキュメントID {doc_id} がバージョン {new_version.version_num} として保存されました。")
            return new_version.version_id
        except Exception as e:
            logger.error(f"ドキュメントのバージョン保存中にエラーが発生しました: {e}")
            db.rollback()
            return None