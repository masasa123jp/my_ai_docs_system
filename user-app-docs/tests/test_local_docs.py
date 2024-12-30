# ._bk\user-app-docs\tests\test_local_docs.py

import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dbschemas.docs_schema import BaseDocLocal, LocalDoc
from dbschemas.doc_tags_schema import BaseTags, DocTag, DocTagLink
from dbschemas.local_doc_versions_schema import BaseVersions, LocalDocVersion
from fastapi import UploadFile, File
import io

# テスト用データベース設定
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テスト用データベースのセットアップ
@pytest.fixture(scope="module")
def test_db():
    # 各スキーマのメタデータを作成
    BaseDocLocal.metadata.create_all(bind=engine)
    BaseTags.metadata.create_all(bind=engine)
    BaseVersions.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    # 各スキーマのテーブルをドロップ
    BaseDocLocal.metadata.drop_all(bind=engine)
    BaseTags.metadata.drop_all(bind=engine)
    BaseVersions.metadata.drop_all(bind=engine)

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

def test_upload_document(client, test_db):
    """
    ドキュメントのアップロードが正常に行われるかテスト
    """
    file_content = b"Test document content"
    file = io.BytesIO(file_content)
    upload_file = UploadFile(filename="test_doc.txt", file=file)
    response = client.post(
        "/upload",
        files={"file": ("test_doc.txt", file_content, "text/plain")},
        data={"title": "Test Document"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "local_doc_id" in data
    doc_id = data["local_doc_id"]

    # データベースにドキュメントが保存されているか確認
    doc = test_db.query(LocalDoc).filter(LocalDoc.id == doc_id).first()
    assert doc is not None
    assert doc.title == "Test Document"
    assert doc.content == "Test document content"

def test_search_hub_docs(client, test_db, monkeypatch):
    """
    HubAppへのRAG検索が正常に行われるかテスト
    """
    def mock_search_hub_docs(query: str):
        assert query == "Test Query"
        return ["Result 1", "Result 2"]

    monkeypatch.setattr("user_app_docs.services.local_doc_service.LocalDocService.search_hub_docs", mock_search_hub_docs)

    response = client.get("/hub_search", params={"query": "Test Query"})
    assert response.status_code == 200
    data = response.json()
    assert "hub_search_results" in data
    assert data["hub_search_results"] == ["Result 1", "Result 2"]

def test_add_tag_to_doc(test_db):
    """
    ドキュメントにタグを追加できるかテスト
    """
    # まず、ドキュメントを作成
    new_doc = LocalDoc(title="Tagged Document", content="Content with tags")
    test_db.add(new_doc)
    test_db.commit()
    test_db.refresh(new_doc)

    # タグを追加
    service = LocalDocService()
    result = service.add_tag_to_doc(doc_id=new_doc.id, tag_name="important")
    assert result is True

    # タグが作成され、リンクが生成されているか確認
    tag = test_db.query(DocTag).filter(DocTag.tag_name == "important").first()
    assert tag is not None

    link = test_db.query(DocTagLink).filter(
        DocTagLink.doc_id == new_doc.id,
        DocTagLink.tag_id == tag.tag_id
    ).first()
    assert link is not None

def test_save_doc_version(test_db):
    """
    ドキュメントのバージョンが保存できるかテスト
    """
    # まず、ドキュメントを作成
    new_doc = LocalDoc(title="Versioned Document", content="Initial Content")
    test_db.add(new_doc)
    test_db.commit()
    test_db.refresh(new_doc)

    # バージョンを保存
    service = LocalDocService()
    version_id = service.save_doc_version(doc_id=new_doc.id, content="Updated Content")
    assert version_id is not None

    # データベースにバージョンが保存されているか確認
    version = test_db.query(LocalDocVersion).filter(LocalDocVersion.version_id == version_id).first()
    assert version is not None
    assert version.version_num == 1
    assert version.content == "Updated Content"