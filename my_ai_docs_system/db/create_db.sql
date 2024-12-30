-- ._bk\db\create_db.sql
-- ローカル環境で PostgreSQL に「my_ai_docs_db」を作成し、
-- DBユーザー mydbuser へ権限付与する例

select current_setting('client_encoding'); -- 現在のクライアントエンコーディングを確認
set client_encoding to 'utf8'; -- 変更
-- データベースとユーザーの作成
CREATE USER mydbuser WITH PASSWORD 'mypassword';

CREATE DATABASE my_ai_docs_db OWNER mydbuser;

-- 必要な拡張機能の有効化
\c my_ai_docs_db mydbuser
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";