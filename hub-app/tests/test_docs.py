# .\hub-app\tests\test_docs.py

import pytest
from fastapi.testclient import TestClient
from hubapp.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dbschemas.docs_schema import BaseDocs, Document
from app.database import DATABASE_URL
from sqlalchemy.pool import StaticPool
from services.doc_service import DocService

# テスト用データベース設定
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テスト用データベースのセットアップ
@pytest.fixture(scope="module")
def test_db():
    BaseDocs.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    BaseDocs.metadata.drop_all(bind=engine)

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

def test_create_document(client, test_db):
    payload = {"title": "TestDoc", "content": "Test Content"}
    resp = client.post("/doc/create", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "doc_id" in data
    assert isinstance(data["doc_id"], int)

def test_list_documents(client, test_db):
    # 最初は一つのドキュメントが存在するはず
    resp = client.get("/doc/list")
    assert resp.status_code == 200
    docs = resp.json()
    assert isinstance(docs, list)
    assert len(docs) == 1
    assert docs[0]["title"] == "TestDoc"