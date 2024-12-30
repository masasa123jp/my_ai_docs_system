# .\user-app-docs\main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from routers.local_doc_router import router as local_doc_router
from routers.login import router as login_router
from routers.auth_router import router as auth_router
from routers.admin_router import router as admin_router  # 追加: 管理者ルーター
from auth import get_current_user  # auth.pyからインポート
from dbschemas.users_schema import User
from dbschemas.local_doc_schema import LocalDoc
from config import DocsSettings  # 設定のインポート
from pydantic import BaseModel
from authlib.integrations.starlette_client import OAuth
from jose import JWTError, jwt
import logging
import os
import httpx
from typing import Optional

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "static")), name="static")

HUBAPP_URL = os.getenv("HUBAPP_URL")
USRAPP_URL = os.getenv("USRAPP_URL")

# CORS設定
origins = [
    HUBAPP_URL,  # hub-appのURL
    USRAPP_URL,  # user-app-docsのURL
    # 必要に応じて他のオリジンを追加
]

ALLOWED_REDIRECT_URIS = [
    USRAPP_URL + "/callback",  # 開発環境用
    # "https://example.com/callback",
    # "https://another-example.com/redirect"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# セッション管理の設定
settings = DocsSettings()
session_secret_key = settings.SECRET_KEY  # 例: SECRET_KEYをセッションキーとして使用

if not session_secret_key:
    raise ValueError("環境変数にSESSION_SECRET_KEYが設定されていません。")

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret_key
)

# テンプレート設定
templates = Jinja2Templates(directory="templates")

# ルーターのインクルード
app.include_router(login_router)
app.include_router(auth_router)
app.include_router(local_doc_router)
app.include_router(admin_router)  # 追加: 管理者ルーターのインクルード

# OAuthクライアントの設定
oauth = OAuth()
oauth.register(
    name='hub-app',
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    access_token_url=f"{settings.HUBAPP_URL}/token",
    authorize_url=f"{settings.HUBAPP_URL}/authorize",
    client_kwargs={'scope': 'openid profile email'},
)

# JWT設定
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

if not SECRET_KEY or not ALGORITHM:
    raise ValueError("SECRET_KEY and ALGORITHM must be set in environment variables.")

# Pydanticモデル
class UserModel(BaseModel):
    username: str
    email: str
    is_active: bool

class TokenData(BaseModel):
    sub: Optional[str] = None

def decode_jwt_token(token: str) -> UserModel:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        email: str = payload.get("email")
        is_active: bool = payload.get("is_active", True)
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UserModel(username=username, email=email, is_active=is_active)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user_func(request: Request) -> UserModel:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        scheme, _, param = token.partition(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        return decode_jwt_token(param)
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

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

@app.post("/authenticate")
async def authenticate(
    redirect_uri: str = Form(...),
    scope: str = Form(None),
    response_type: str = Form(...),
    state: str = Form(None),
    nonce: str = Form(None)
):
    """
    クライアントからのPOSTリクエストを受け取り、認証処理を行った後、
    指定されたリダイレクトURIに対してPOSTリクエストでリダイレクトします。
    """
    logger.info("Authenticate endpoint called with redirect_uri: %s", redirect_uri)

    # 必須パラメータの検証
    if not redirect_uri:
        logger.error("redirect_uri is missing.")
        raise HTTPException(status_code=400, detail="redirect_uri is required")
    if not response_type:
        logger.error("response_type is missing.")
        raise HTTPException(status_code=400, detail="response_type is required")

    # リダイレクトURIの検証
    if redirect_uri not in ALLOWED_REDIRECT_URIS:
        logger.error("Invalid redirect_uri: %s", redirect_uri)
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")

    # ここで認証処理を実装
    # 例: ユーザー認証、トークン発行など
    # 認証が成功したと仮定し、トークンを生成
    access_token = "dummy_access_token"

    # リダイレクト先のパラメータを準備
    redirect_params = {
        'access_token': access_token,
        'scope': scope,
        'response_type': response_type,
        'state': state,
        'nonce': nonce,
        # 必要に応じて他のパラメータも追加
    }

    logger.info("Preparing to redirect via POST to: %s with params: %s", redirect_uri, redirect_params)

    # 自動送信フォームを生成
    html_content = generate_auto_post_form(redirect_uri, redirect_params)

    # HTMLフォームを含むレスポンスを返す
    return HTMLResponse(content=html_content, status_code=200)

@app.api_route("/callback", methods=["GET", "POST"])
async def callback(request: Request):
    """
    認証後のリダイレクトエンドポイント。GETおよびPOSTリクエストに対応。
    """
    logger.info("Callback endpoint called.")

    try:
        # POSTデータを取得
        if request.method == "POST":
            form = await request.form()
            # フォームデータから必要なパラメータを取得
            token = form.get('access_token')
            scope = form.get('scope')
            response_type = form.get('response_type')
            state = form.get('state')
            nonce = form.get('nonce')
        else:
            # GETリクエストの場合、クエリパラメータから取得
            params = request.query_params
            token = params.get('access_token')
            scope = params.get('scope')
            response_type = params.get('response_type')
            state = params.get('state')
            nonce = params.get('nonce')

        if not token:
            logger.error("Access token is missing.")
            raise HTTPException(status_code=400, detail="Access token is required")

        # ユーザー情報の取得をシミュレート
        user = {
            'preferred_username': 'johndoe',
            'email': 'johndoe@example.com'
        }

        if not user:
            logger.warning("Authentication failed: No user info received.")
            raise HTTPException(status_code=400, detail="Authentication failed")

        # JWTトークンの生成
        access_token_jwt = jwt.encode(
            {
                "sub": user['preferred_username'],
                "email": user['email'],
                "is_active": True  # 必要に応じてユーザーのアクティブ状態を設定
            },
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        # クッキーにトークンを設定してリダイレクト
        response = RedirectResponse(url="/docs", status_code=status.HTTP_303_SEE_OTHER)  # ステータスコードを303に変更
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token_jwt}",
            httponly=True,
            secure=False,  # 開発環境ではFalse、本番環境ではTrueに設定
            samesite='lax'
        )

        logger.info("Authentication successful. Redirecting to /docs with access_token set.")

        return response

    except Exception as e:
        logger.error(f"Error during token authorization: {e}")
        raise HTTPException(status_code=400, detail="Authentication failed")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    認証フォームを提供するルートエンドポイント。
    クライアント側でフォームからPOSTリクエストを送信します。
    """
    html_content = """
    <html>
        <head>
            <title>Authenticate</title>
            <link id="favicon" rel="icon" type="image/x-icon" href="static/favicon.ico">
        </head>
        <body>
            <h2>Authenticate</h2>
            <form action="/authenticate" method="post">
                <label for="redirect_uri">Redirect URI:</label><br>
                <input type="text" id="redirect_uri" name="redirect_uri" value="http://localhost:8100/callback"><br><br>

                <label for="scope">Scope:</label><br>
                <input type="text" id="scope" name="scope" value="read"><br><br>

                <label for="response_type">Response Type:</label><br>
                <input type="text" id="response_type" name="response_type" value="token"><br><br>

                <label for="state">State:</label><br>
                <input type="text" id="state" name="state" value="xyz"><br><br>

                <label for="nonce">Nonce:</label><br>
                <input type="text" id="nonce" name="nonce" value="abc"><br><br>

                <input type="submit" value="Authenticate">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# ドキュメント一覧表示エンドポイント
@app.get("/docs", response_class=HTMLResponse)
async def list_docs(request: Request, current_user: UserModel = Depends(get_current_user_func)):
    # ここでは仮のデータを使用しています。実際にはデータベースから取得します。
    documents = [
        {"id": 1, "title": "ドキュメント1", "content": "内容1"},
        {"id": 2, "title": "ドキュメント2", "content": "内容2"},
    ]
    return templates.TemplateResponse("docs.html", {"request": request, "documents": documents, "user": current_user})

# ドキュメント作成フォーム表示エンドポイント
@app.get("/docs/create", response_class=HTMLResponse)
async def create_doc_form(request: Request, current_user: UserModel = Depends(get_current_user_func)):
    return templates.TemplateResponse("create_doc.html", {"request": request, "user": current_user})

# ドキュメント作成処理エンドポイント
@app.post("/docs/create")
async def create_doc(request: Request, title: str = Form(...), content: str = Form(...), current_user: UserModel = Depends(get_current_user_func)):
    # ここでデータベースにドキュメントを保存します。現在は仮の処理です。
    # 実際にはデータベース操作を追加してください。
    logger.info(f"Creating document: {title}")
    # 例: db.add(new_doc); db.commit()
    return RedirectResponse(url="/docs", status_code=status.HTTP_303_SEE_OTHER)

# ドキュメント詳細表示エンドポイント
@app.get("/docs/{doc_id}", response_class=HTMLResponse)
async def get_doc(request: Request, doc_id: int, current_user: UserModel = Depends(get_current_user_func)):
    # データベースからドキュメントを取得します。ここでは仮のデータを使用します。
    document = {"id": doc_id, "title": f"ドキュメント{doc_id}", "content": f"内容{doc_id}"}
    return templates.TemplateResponse("doc_detail.html", {"request": request, "document": document, "user": current_user})

# ドキュメント編集フォーム表示エンドポイント
@app.get("/docs/{doc_id}/edit", response_class=HTMLResponse)
async def edit_doc_form(request: Request, doc_id: int, current_user: UserModel = Depends(get_current_user_func)):
    # 実際にはデータベースからドキュメントを取得します。
    document = {"id": doc_id, "title": f"ドキュメント{doc_id}", "content": f"内容{doc_id}"}
    return templates.TemplateResponse("edit_doc.html", {"request": request, "document": document, "user": current_user})

# ドキュメント更新処理エンドポイント
@app.post("/docs/{doc_id}/edit")
async def edit_doc(request: Request, doc_id: int, title: str = Form(...), content: str = Form(...), current_user: UserModel = Depends(get_current_user_func)):
    # ここでデータベースのドキュメントを更新します。現在は仮の処理です。
    # 実際にはデータベース操作を追加してください。
    logger.info(f"Updating document {doc_id} to title: {title}")
    # 例: doc = db.query(Doc).get(doc_id); doc.title = title; doc.content = content; db.commit()
    return RedirectResponse(url=f"/docs/{doc_id}", status_code=status.HTTP_303_SEE_OTHER)

# ドキュメント削除エンドポイント
@app.post("/docs/{doc_id}/delete")
async def delete_doc(doc_id: int, current_user: UserModel = Depends(get_current_user_func)):
    # ここでデータベースからドキュメントを削除します。現在は仮の処理です。
    # 実際にはデータベース操作を追加してください。
    logger.info(f"Deleting document {doc_id}")
    # 例: doc = db.query(Doc).get(doc_id); db.delete(doc); db.commit()
    return RedirectResponse(url="/docs", status_code=status.HTTP_303_SEE_OTHER)

# ログインエンドポイント
@app.get("/login")
async def login(request: Request):
    logger.info("Login endpoint called.")
    redirect_uri = "http://localhost:8100/callback"  # リダイレクトURIを/callbackに変更
    state = os.urandom(16).hex()  # 状態をランダムに生成
    nonce = os.urandom(16).hex()  # ノンスをランダムに生成

    return await oauth.hub-app.authorize_redirect(
        request,
        redirect_uri,
        scope='openid profile email',
        response_type='code',
        state=state,
        nonce=nonce
    )

# ログアウトエンドポイント
@app.get("/logout")
async def logout():
    logger.info("Logout endpoint called.")
    response = RedirectResponse(url="/")
    response.delete_cookie(key="access_token")
    logger.info("Access token cookie deleted. Redirecting to home.")
    return response