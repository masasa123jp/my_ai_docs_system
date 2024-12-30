# ._bk\user-app-docs\routers\local_doc_router.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from services.local_doc_service import LocalDocService
from dbschemas.docs_schema import Document
from database import get_db  # get_db依存関係があると仮定

router = APIRouter(prefix="/local_docs", tags=["ローカルドキュメント"])

@router.post("/upload", response_model=dict)
def local_upload(file: UploadFile = File(...), title: str = "", db: Session = Depends(get_db)):
    """
    ローカルドキュメントのアップロード。
    提供されたタイトルでファイルの内容をローカルデータベースに保存します。
    """
    try:
        if not title:
            title = file.filename
        doc_id = LocalDocService.save_local_record(file, title, db)
        if not doc_id:
            raise HTTPException(status_code=500, detail="ドキュメントの保存に失敗しました。")
        return {"local_doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hub_search", response_model=dict)
def search_on_hub(query: str, db: Session = Depends(get_db)):
    """
    RAGを使用してHubApp上のドキュメントを検索します。
    """
    try:
        results = LocalDocService.search_hub_docs(query, db)
        if results is None:
            raise HTTPException(status_code=500, detail="HubAppの検索に失敗しました。")
        return {"hub_search_results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{doc_id}/add_tag", response_model=dict)
def add_tag(doc_id: int, tag_name: str, db: Session = Depends(get_db)):
    """
    ローカルドキュメントにタグを追加します。
    """
    try:
        success = LocalDocService.add_tag_to_doc(doc_id, tag_name, db)
        if not success:
            raise HTTPException(status_code=400, detail="タグの追加に失敗しました。")
        return {"message": "タグが正常に追加されました。"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{doc_id}/save_version", response_model=dict)
def save_version(doc_id: int, content: str, db: Session = Depends(get_db)):
    """
    ドキュメントのバージョンを保存するエンドポイント。
    """
    try:
        version_id = LocalDocService.save_doc_version(doc_id, content, db)
        if not version_id:
            raise HTTPException(status_code=500, detail="ドキュメントのバージョン保存に失敗しました。")
        return {"version_id": version_id}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": "内部サーバーエラーが発生しました。"})