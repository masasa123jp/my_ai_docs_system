# .\hub-app\services\oauth2_service.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import uuid
import secrets

from app.schemas import OAuth2Client
from app.models import Client
from app.auth import pwd_context
from config import Settings

settings = Settings()

class OAuth2Service:
    @staticmethod
    def create_client(db: Session, redirect_uri: str) -> OAuth2Client:
        """
        新しいOAuth2クライアントを作成し、データベースに保存します。
        """
        client_id = str(uuid.uuid4())
        client_secret = secrets.token_urlsafe(32)
        hashed_secret = pwd_context.hash(client_secret)

        new_client = Client(
            client_id=client_id,
            client_secret=hashed_secret,
            redirect_uri=redirect_uri,
            is_active=True
        )

        db.add(new_client)
        db.commit()
        db.refresh(new_client)

        return OAuth2Client(
            client_id=new_client.client_id,
            client_secret=client_secret,  # クライアントシークレットはプレーンテキストで返す
            redirect_uri=new_client.redirect_uri
        )

    @staticmethod
    def get_client(db: Session, client_id: str) -> Client:
        """
        クライアントIDを用いてクライアントを取得します。
        """
        return db.query(Client).filter(Client.client_id == client_id, Client.is_active == True).first()

    @staticmethod
    def validate_client_secret(db: Session, client_id: str, client_secret: str) -> bool:
        """
        クライアントシークレットの検証を行います。
        """
        client = OAuth2Service.get_client(db, client_id)
        if not client:
            return False
        return pwd_context.verify(client_secret, client.client_secret)

    @staticmethod
    def generate_authorization_code(db: Session, user_id: int, client_id: str, scope: str) -> str:
        """
        認可コードを生成し、データベースに保存します。
        """
        code = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)  # 認可コードの有効期限は10分

        db.execute(
            text(
                "INSERT INTO auth_schema.authorization_codes (code, user_id, client_id, scope, expires_at) "
                "VALUES (:code, :user_id, :client_id, :scope, :expires_at)"
            ),
            {"code": code, "user_id": user_id, "client_id": client_id, "scope": scope, "expires_at": expires_at}
        )
        db.commit()

        return code

    @staticmethod
    def validate_authorization_code(db: Session, code: str, client_id: str) -> int:
        """
        認可コードの検証を行い、関連するユーザーIDを返します。
        """
        result = db.execute(
            text(
                "SELECT user_id, expires_at FROM auth_schema.authorization_codes "
                "WHERE code = :code AND client_id = :client_id"
            ),
            {"code": code, "client_id": client_id}
        ).fetchone()

        if not result:
            return None

        user_id, expires_at = result
        if datetime.utcnow() > expires_at:
            # 認可コードの期限切れ
            db.execute(
                text("DELETE FROM auth_schema.authorization_codes WHERE code = :code"),
                {"code": code}
            )
            db.commit()
            return None

        # 認可コードの一回限りの使用を確保するため削除
        db.execute(
            text("DELETE FROM auth_schema.authorization_codes WHERE code = :code"),
            {"code": code}
        )
        db.commit()

        return user_id

    @staticmethod
    def generate_access_token(db: Session, user_id: int, client_id: str, scope: str) -> str:
        """
        アクセストークン（JWT）を生成します。
        """
        from app.auth import create_access_token  # 循環依存防止のため内部インポート

        data = {
            "sub": user_id,
            "scope": scope,
            "client_id": client_id
        }
        access_token_expires = timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        token = create_access_token(data=data, expires_delta=access_token_expires)
        return token

    @staticmethod
    def revoke_token(db: Session, token: str):
        """
        トークンを無効化します。必要に応じてトークンブラックリストに追加します。
        """
        # 実装例：ブラックリストテーブルにトークンを保存
        db.execute(
            text(
                "INSERT INTO auth_schema.token_blacklist (token, revoked_at) "
                "VALUES (:token, :revoked_at)"
            ),
            {"token": token, "revoked_at": datetime.utcnow()}
        )
        db.commit()

    @staticmethod
    def is_token_revoked(db: Session, token: str) -> bool:
        """
        トークンがブラックリストに存在するかをチェックします。
        """
        result = db.execute(
            text(
                "SELECT 1 FROM auth_schema.token_blacklist WHERE token = :token"
            ),
            {"token": token}
        ).fetchone()
        return result is not None