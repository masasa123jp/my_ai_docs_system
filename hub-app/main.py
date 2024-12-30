# .\hub-app\main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request, Query, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app import models, schemas, auth, oauth2
from config import Settings 
from app.database import SessionLocal, engine, Base
from jose import JWTError
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth as AuthlibOAuth
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
from datetime import timedelta
from routers.auth_router import router as auth_router
from routers.authorize import router as authorize_router
from routers.ai_router import router as ai_router
from routers.doc_router import router as doc_router
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()

# データベースのマイグレーション（必要に応じてコメントアウト）
# Base.metadata.create_all(bind=engine)  # 既に database.py で実行済み

app = FastAPI()

# ルーターのインクルード
app.include_router(auth_router)
app.include_router(authorize_router)
app.include_router(ai_router)
app.include_router(doc_router)

# CORS 設定
cors_allowed_origins = [origin.strip() for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if origin.strip()]
logger.info(f"CORS allowed origins: {cors_allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origins if cors_allowed_origins else ["*"],  # デフォルトで全許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SessionMiddleware の追加
session_secret_key = os.getenv("SESSION_SECRET_KEY")
if not session_secret_key:
    raise ValueError("SESSION_SECRET_KEY is not set in the environment variables.")

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret_key,
)
logger.info("SessionMiddleware added successfully.")

# OAuth2PasswordBearer を使用してトークンの取得を管理
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Authlib OAuth クライアントの設定
oauth = AuthlibOAuth()
settings = auth.Settings()  # Settingsクラスのインスタンス化を確認
oauth.register(
    name='hubapp',
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    access_token_url=f"{settings.HUBAPP_URL}/token",
    authorize_url=f"{settings.HUBAPP_URL}/authorize",
    client_kwargs={'scope': 'openid profile email'},
)
logger.info("Authlib OAuth client registered successfully.")

# デペンデンシー
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ユーザーの取得
def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# クライアントの取得
def get_client_by_id(db: Session, client_id: str):
    return oauth2.get_client(db, client_id)

# 認証の実装
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not auth.verify_password(password, user.hashed_password):
        return False
    return user

# トークンから現在のユーザーを取得
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = auth.decode_access_token(token)
    if token_data is None or token_data.get("username") is None:
        raise credentials_exception
    user = get_user(db, token_data.get("username"))
    if user is None:
        raise credentials_exception
    return user

# 現在のアクティブなユーザーを取得
async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ユーザー登録エンドポイント
@app.post("/register", response_model=schemas.UserRead)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# トークン発行エンドポイント
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 保護されたエンドポイントの例
@app.get("/users/me", response_model=schemas.UserRead)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

def generate_auto_post_form(url: str, params: dict) -> str:
    """
    指定されたURLにPOSTリクエストを自動的に送信するHTMLフォームを生成します。
    """
    form_fields = ''.join(
        f'<input type="hidden" name="{key}" value="{value}"/>' for key, value in params.items()
    )
    html_content = f"""
    <html>
        <head>
            <title>Redirecting...</title>
        </head>
        <body onload="document.forms[0].submit();">
            <form method="post" action="{url}">
                {form_fields}
                <noscript>
                    <p>JavaScript が無効になっている場合は、以下のボタンをクリックしてください。</p>
                    <button type="submit">Continue</button>
                </noscript>
            </form>
        </body>
    </html>
    """
    return html_content

# OAuth2 認可エンドポイント
@app.get("/authorize")
async def authorize(
    request: Request,
    response_type: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(...),
    state: str = Query(...),
    nonce: str = Query(...),
    db: Session = Depends(get_db)  # 追加
):
    logger.info("Authorize endpoint called.")
    # 必要なバリデーション
    if not all([client_id, redirect_uri, state, nonce]):
        logger.warning("Missing required parameters in authorize request.")
        raise HTTPException(status_code=400, detail="Missing required parameters")

    logger.info(f"Received authorize request for client_id: {client_id}")
    client = get_client_by_id(db, client_id)
    if not client:
        logger.warning(f"Invalid client_id: {client_id}")
        raise HTTPException(status_code=400, detail="Invalid client_id")
    if redirect_uri != client.redirect_uri:
        logger.warning(f"Invalid redirect_uri: {redirect_uri}")
        logger.warning(f"Invalid redirect_uri: {client.redirect_uri}")
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")

    # セッションにclient_idを保存
    request.session['client_id'] = client_id
    logger.info(f"Client_id {client_id} saved in session.")
    logger.info(f"redirect_uri: {redirect_uri} ")

    # リダイレクト先のパラメータを準備
    redirect_params = {
        "request": request,
        "redirect_uri" : redirect_uri,
        "scope" : scope,
        "response_type" : response_type,
        "state" : state,
        "nonce" : nonce
        # 必要に応じて他のパラメータも追加
    }

    logger.info("Preparing to redirect via POST to: %s with params: %s", redirect_uri, redirect_params)

    # 自動送信フォームを生成
    html_content = generate_auto_post_form(redirect_uri, redirect_params)

    # HTMLフォームを含むレスポンスを返す
    return HTMLResponse(content=html_content, status_code=200)

"""
    # クライアントのリダイレクトURIにリダイレクト
    return await oauth.hubapp.authorize_redirect(
        request,
        redirect_uri,
        scope=scope,
        response_type=response_type,
        state=state,
        nonce=nonce
    )
"""

# 認証後のリダイレクトエンドポイント（コールバック）
@app.get("/callback")
async def auth_redirect(request: Request, db: Session = Depends(get_db)):
    logger.info("Callback endpoint called.")
    client_id = request.session.get('client_id')
    if not client_id:
        logger.warning("client_id not found in session.")
        raise HTTPException(status_code=400, detail="client_id not found in session")

    client = get_client_by_id(db, client_id)
    if not client:
        logger.warning(f"Invalid client with client_id: {client_id}")
        raise HTTPException(status_code=400, detail="Invalid client")

    token = await oauth.hubapp.authorize_access_token(request)
    user_info = await oauth.hubapp.parse_id_token(request, token)
    if not user_info:
        logger.warning("Authentication failed: No user info received.")
        raise HTTPException(status_code=400, detail="Authentication failed")

    # ユーザーが存在しない場合は作成
    user = db.query(models.User).filter(models.User.email == user_info.get('email')).first()
    if not user:
        logger.info(f"User with email {user_info.get('email')} not found. Creating new user.")
        # ランダムなパスワードを生成（実際にはユーザーにパスワード設定を依頼するなどの対応が必要）
        random_password = os.urandom(16).hex()
        hashed_password = auth.get_password_hash(random_password)
        user = models.User(
            username=user_info.get('preferred_username', user_info.get('email').split("@")[0]),
            email=user_info.get('email'),
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user created: {user.username}")

    # JWTトークンの生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"Access token created for user: {user.username}")

    # クッキーにトークンを設定してクライアントアプリケーションにリダイレクト
    response = RedirectResponse(url=client.redirect_uri)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, secure=True, samesite='lax')
    logger.info(f"Redirecting to client redirect_uri: {client.redirect_uri}")
    return response

# クライアント登録エンドポイント
@app.post("/clients/register", response_model=schemas.OAuth2Client)
def register_client(
    redirect_uri: str = Form(...),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Registering new client with redirect_uri: {redirect_uri}")
    client = oauth2.create_oauth2_client(db, redirect_uri)
    logger.info(f"Client registered with client_id: {client.client_id}")
    return client

# ルートエンドポイント
@app.get("/")
def read_root():
    logger.info("Root endpoint called.")
    return {"message": "Welcome to hub-app OAuth2 server"}

# 404 エラーハンドリング
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.warning(f"404 Not Found: {request.url}")
    return JSONResponse(status_code=404, content={"detail": "Not Found"})
