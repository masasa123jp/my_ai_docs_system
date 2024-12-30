@echo off
REM ====================================================
REM run_userapp_docs.bat
REM user-app-docs を起動するバッチファイル
REM ====================================================

REM user-app-docsディレクトリに移動
cd /d .\user-app-docs

REM 仮想環境をアクティベート
call venv\Scripts\activate

REM 環境変数をロード (.env ファイルがある場合)
if exist .env (
    for /f "delims=" %%i in (.env) do set "%%i"
)

REM user-app-docsを起動
echo Starting user-app-docs...
uvicorn main:app --host 0.0.0.0 --port 8100 --reload
