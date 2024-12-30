# .\hub-app\app\oauth2.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import User, Client
from app.schemas import OAuth2Client
import uuid
import secrets
from passlib.context import CryptContext
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_oauth2_client(db: Session, redirect_uri: str) -> OAuth2Client:
    client_id = str(uuid.uuid4())
    client_secret = secrets.token_urlsafe(32)
    logger.info(f"Creating OAuth2 client with client_id: {client_id}")
    
    # クライアント情報をデータベースに保存
    new_client = Client(
        client_id=client_id,
        client_secret=pwd_context.hash(client_secret),
        redirect_uri=redirect_uri
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    logger.info(f"OAuth2 client created with client_id: {new_client.client_id}")
    
    return OAuth2Client(
        client_id=new_client.client_id,
        client_secret=client_secret,  # プレーンなシークレットを返す（セキュリティに注意）
        redirect_uri=new_client.redirect_uri
    )

def get_client(db: Session, client_id: str) -> Client:
    try:
        # 現在のsearch_pathを取得
        result = db.execute(text("SHOW search_path;"))
        search_path = result.scalar()
        logger.info(f"Current search_path: {search_path}")

        # クライアントを取得
        client = db.query(Client).filter(Client.client_id == client_id, Client.is_active == True).first()
        if not client:
            logger.warning(f"Client with client_id '{client_id}' not found or inactive.")
        else:
            logger.info(f"Client retrieved: {client.client_id}")
        return client
    except Exception as e:
        logger.error(f"Error in get_client: {e}")
        raise
