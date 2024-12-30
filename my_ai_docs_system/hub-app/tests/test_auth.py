# .\hub-app\tests\test_auth.py

import pytest
from fastapi.testclient import TestClient
from hubapp.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dbschemas.auth_schema import AuthBase, User
from app.database import DATABASE_URL
from sqlalchemy.pool import StaticPool
from services.auth_service import AuthService

# テスト用データベース設定
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テスト用データベースのセットアップ
@pytest.fixture(scope="module")
def test_db():
    AuthBase.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # テストユーザーの作成
    test_user = User(username="admin", email="admin@example.com", password_hash=AuthService.hash_password("adminpass"))
    db.add(test_user)
    db.commit()
    yield db
    db.close()
    AuthBase.metadata.drop_all(bind=engine)

# テスト用クライアント
@pytest.fixture(scope="module")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    app.dependency_overrides[SessionLocal] = override_get_db
    return TestClient(app)

def test_login_fail(client):
    resp = client.post("/auth/login", data={"username":"unknown", "password":"wrong"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"

def test_login_success(client, test_db, monkeypatch):
    def mock_auth_user(db: Session, u: str, p: str):
        return test_db.query(User).filter(User.username == u).first() if u == "admin" and AuthService.verify_password(p, test_db.query(User).filter(User.username == u).first().password_hash) else None

    monkeypatch.setattr(AuthService, "authenticate_user", mock_auth_user)

    resp = client.post("/auth/login", data={"username":"admin", "password":"adminpass"})
    assert resp.status_code == 302
    assert resp.headers["location"] == "http://localhost:8100"
    assert "Set-Cookie" in resp.headers
    assert "session_id" in resp.headers["Set-Cookie"]