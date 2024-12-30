# .\hub-app\tests\test_ai.py

from fastapi.testclient import TestClient
from hubapp.main import app
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbschemas.ai_schema import Base, AICallLogs
from app.database import DATABASE_URL
from sqlalchemy.pool import StaticPool
from services.ai_service import AIService

# テスト用のデータベース設定
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テスト用データベースのセットアップ
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

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

def test_generate_text(client, test_db, monkeypatch):
    def mock_call_llm(prompt):
        assert prompt == "Hello"
        return "Mocked LLM response"

    monkeypatch.setattr(AIService, "generate_text", lambda p, db: mock_call_llm(p))

    resp = client.post("/ai/generate", json={"prompt": "Hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["generated_text"] == "Mocked LLM response"

def test_rag_search(client, test_db, monkeypatch):
    def mock_rag_search_and_answer(query, db):
        assert query == "What is AI?"
        return "AI stands for Artificial Intelligence."

    monkeypatch.setattr(AIService, "rag_search_and_answer", mock_rag_search_and_answer)

    resp = client.get("/ai/rag_search", params={"query": "What is AI?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "AI stands for Artificial Intelligence."