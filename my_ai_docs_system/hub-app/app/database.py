# .\hub-app\app\database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from shared_libs.database import Base  # 共通のBaseをインポート
from app import models  # hub-app内の全てのモデルをインポート
from config import Settings

# ロギングの設定
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# 設定のロード
settings = Settings()

engine = create_engine(
    settings.DOCAPP_DB_URL,
    pool_pre_ping=True,
    connect_args={
        "options": "-c search_path=auth_schema,doc_app,ai_schema,logs_schema,hub_docs,public"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テーブルを作成する前に全てのモデルをインポート
from dbschemas.auth_schema import User, Client
# 他の必要なモデルもここでインポート

# テーブルを作成
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully.")