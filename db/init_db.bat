@echo off
REM init_db.bat : DB初期化を順に実行する完全版

echo === Creating Database and User ===
psql -U postgres -f .\db\create_db.sql

echo === Creating Tables for hub-app ===
REM スキーマを設定してからテーブル作成スクリプトを実行
psql -U mydbuser -d my_ai_docs_db -c "SET search_path TO auth_schema, public;" -f .\db\create_tables_hub.sql

echo === Creating Tables for user-app-docs ===
REM スキーマを設定してからテーブル作成スクリプトを実行
psql -U mydbuser -d my_ai_docs_db -c "SET search_path TO doc_app, public;" -f .\db\create_tables_user.sql

REM echo === Creating Tables for AI Schema ===
REM スキーマを設定してからAI関連のテーブル作成スクリプトを実行
REM psql -U mydbuser -d my_ai_docs_db -c "SET search_path TO ai_schema, public;" -f .\db\create_tables_ai.sql

REM echo === Creating Tables for Auth Schema ===
REM スキーマを設定してからAuth関連のテーブル作成スクリプトを実行
REM psql -U mydbuser -d my_ai_docs_db -c "SET search_path TO auth_schema, public;" -f .\db\create_tables_auth.sql

REM echo === Creating Tables for Logs Schema ===
REM スキーマを設定してからLogs関連のテーブル作成スクリプトを実行
REM psql -U mydbuser -d my_ai_docs_db -c "SET search_path TO logs_schema, public;" -f .\db\create_tables_logs.sql

REM echo === Creating Tables for Hub Docs Schema ===
REM スキーマを設定してからHub Docs関連のテーブル作成スクリプトを実行
REM psql -U mydbuser -d my_ai_docs_db -c "SET search_path TO hub_docs, public;" -f .\db\create_tables_hub_docs.sql

echo === Inserting Sample Data ===
REM 必要なスキーマを設定してからサンプルデータ挿入スクリプトを実行
psql -U mydbuser -d my_ai_docs_db -c "SET search_path TO auth_schema, doc_app, ai_schema, logs_schema, hub_docs, public;" -f .\db\insert_sample_data.sql

echo All done.