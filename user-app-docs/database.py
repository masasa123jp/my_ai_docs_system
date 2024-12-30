# .\user-app-docs\database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared_libs.database import Base  # 共通のBaseをインポート
from dbschemas import *  # 全てのdbschemasモデルをインポート

# ロギングの設定
import logging
import os
from config import DocsSettings
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declarative_base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設定のロード
settings = DocsSettings()

engine = create_engine(
    settings.DOCAPP_DB_URL,
    echo=False,
    pool_size=20,
    max_overflow=0,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 全てのモデルをインポートしてBaseに登録
from dbschemas import users_schema, local_doc_schema, doc_tags_schema, doc_links_schema, doc_tags_schema, local_doc_versions_schema, docs_schema, ai_schema

# テーブルを作成
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully.")

def get_db():
    """
    データベースセッションを取得する依存関係
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()