# .\hub-app\routers\auth.py

from fastapi import APIRouter, Query, HTTPException, status, Form, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from services.auth_service import AuthService
from app.database import SessionLocal

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(SessionLocal)):
    user = AuthService.authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    session_id = AuthService.create_session(user.id)
    response = RedirectResponse(url="http://localhost:8100", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True, samesite='lax')
    return response

@router.get("/logout")
def logout(request: Request, db: Session = Depends(SessionLocal)):
    sid = request.cookies.get("session_id")
    if sid:
        AuthService.logout_session(db, sid)
    resp = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    resp.delete_cookie("session_id")
    return resp

@router.get("/validate_session")
def validate_session(sid: str, db: Session = Depends(SessionLocal)):
    """
    user-appがセッション確認用に呼び出す
    """
    user_id = AuthService.validate_session(db, sid)
    if user_id:
        return {"user_id": user_id}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session invalid or expired")