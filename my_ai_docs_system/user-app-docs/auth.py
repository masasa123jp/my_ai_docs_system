# .\user-app-docs\auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from config import DocsSettings
from typing import Optional
from dbschemas.users_schema import User
from database import get_db
from sqlalchemy.orm import Session

settings = DocsSettings()

oauth = OAuth()
oauth.register(
    name='hubapp',
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    access_token_url=f"{settings.HUBAPP_URL}/oauth/token",
    authorize_url=f"{settings.HUBAPP_URL}/oauth/authorize",
    client_kwargs={'scope': 'openid profile email'},
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{settings.HUBAPP_URL}/oauth/authorize",
    tokenUrl=f"{settings.HUBAPP_URL}/oauth/token",
)

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報の検証に失敗しました。",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user