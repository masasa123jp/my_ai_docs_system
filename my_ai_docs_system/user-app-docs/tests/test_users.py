# .\user-app-docs\tests\test_users.py

import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbschemas.users_schema import BaseUsers, User
from database import get_db
from passlib.context import CryptContext

# テスト用データベース設定
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# パスワードハッシュ化の設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# テスト用データベースのセットアップ
@pytest.fixture(scope="module")
def test_db():
    BaseUsers.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    BaseUsers.metadata.drop_all(bind=engine)

# テスト用クライアント
@pytest.fixture(scope="module")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

def test_signup(client, test_db):
    """
    ユーザーのサインアップが正常に行われるかテスト
    """
    response = client.post(
        "/login/signup",
        data={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "ユーザーが正常に作成されました。"

    # データベースにユーザーが追加されているか確認
    user = test_db.query(User).filter(User.username == "testuser").first()
    assert user is not None
    assert user.email == "testuser@example.com"
    assert pwd_context.verify("testpassword", user.password_hash)

def test_login(client, test_db):
    """
    ユーザーのログインが正常に行われるかテスト
    """
    # 事前にユーザーを作成
    user = User(
        username="loginuser",
        email="loginuser@example.com",
        password_hash=pwd_context.hash("loginpassword")
    )
    test_db.add(user)
    test_db.commit()

    response = client.post(
        "/login/login",
        data={
            "username": "loginuser",
            "password": "loginpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_login(client):
    """
    無効なログイン情報でエラーが返されるかテスト
    """
    response = client.post(
        "/login/login",
        data={
            "username": "nonexistent",
            "password": "nopassword"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "ユーザー名またはパスワードが無効です。"