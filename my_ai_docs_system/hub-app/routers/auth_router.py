# .\hub-app\routers\auth_router.py
from fastapi import APIRouter, HTTPException, status, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from services.auth_service import AuthService
from app.database import SessionLocal
from sqlalchemy.orm import Session
import logging

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.get("/login", response_class=HTMLResponse)
def login_form():
    return """
    <html>
     <head><title>HubApp - Login</title></head>
     <body>
       <h2>Login</h2>
       <form action="/auth/login" method="post">
         <label>Username: <input type="text" name="username"></label><br/>
         <label>Password: <input type="password" name="password"></label><br/>
         <button type="submit">Sign In</button>
       </form>
     </body>
    </html>
    """

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(SessionLocal)):
    try:
        user = AuthService.authenticate_user(db, username, password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        session_id = AuthService.create_session(db, user.id)
        response = RedirectResponse(url="http://localhost:8100", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="session_id", value=session_id, httponly=True, secure=True, samesite='lax')
        return response
    except Exception as e:
        logging.error(f"Login failed for user {username}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

@router.get("/logout")
def logout(db: Session = Depends(SessionLocal)):
    sid = request.cookies.get("session_id")
    if sid:
        try:
            AuthService.logout_session(db, sid)
        except Exception as e:
            logging.error(f"Error during logout: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed.")
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