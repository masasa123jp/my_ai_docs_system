@echo off
REM ====================================================
REM run_hubapp.bat
REM hub-app を起動するバッチファイル
REM ====================================================

REM hub-appディレクトリに移動
cd /d .\hub-app

REM 仮想環境をアクティベート
call venv\Scripts\activate

REM 環境変数をロード (.env ファイルがある場合)
if exist .env (
    for /f "delims=" %%i in (.env) do set "%%i"
)

REM hub-appを起動
echo Starting hub-app...
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
