-- ._bk\db\create_tables_hub.sql
-- Hub-app 用のスキーマとテーブル定義(認証, AI関連, 共通文書など)
select current_setting('client_encoding'); -- 現在のクライアントエンコーディングを確認
set client_encoding to 'utf8'; -- 変更

-- 1) auth_schema: ユーザー認証情報 & セッション管理
CREATE SCHEMA IF NOT EXISTS auth_schema;

-- テーブル作成: users
CREATE TABLE IF NOT EXISTS auth_schema.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- テーブル作成: clients
CREATE TABLE IF NOT EXISTS auth_schema.clients (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(100) UNIQUE NOT NULL,
    client_secret VARCHAR(200) NOT NULL,
    redirect_uri VARCHAR(300) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS auth_schema.sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    user_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_schema.users(id) ON DELETE CASCADE
);

-- テーブル作成: auth_schema.authorization_codes
CREATE TABLE IF NOT EXISTS auth_schema.authorization_codes (
    code VARCHAR(64) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_schema.users(id) ON DELETE CASCADE,
    client_id VARCHAR(100) NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    scope VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL
);

-- テーブル作成: auth_schema.token_blacklist
CREATE TABLE IF NOT EXISTS auth_schema.token_blacklist (
    id SERIAL PRIMARY KEY,
    token VARCHAR(500) UNIQUE NOT NULL,
    revoked_at TIMESTAMP NOT NULL
);

COMMENT ON TABLE auth_schema.users IS 'ローカル認証ユーザ管理';
COMMENT ON TABLE auth_schema.sessions IS 'DBでセッションを管理し、マルチインスタンス対応';
COMMENT ON TABLE auth_schema.clients IS 'ユーザーアプリ管理';
COMMENT ON TABLE auth_schema.authorization_codes IS '認証管理関連';
COMMENT ON TABLE auth_schema.token_blacklist IS '認証管理関連';

-- 2) hub_docs: 全社文書などを管理する場合の例
CREATE SCHEMA IF NOT EXISTS hub_docs;

CREATE TABLE IF NOT EXISTS hub_docs.documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE hub_docs.documents IS 'HubApp全社文書の格納テーブル';

-- 3) ai_schema: AI/RAG関連
CREATE SCHEMA IF NOT EXISTS ai_schema;

CREATE TABLE IF NOT EXISTS ai_schema.ai_call_logs (
    call_id SERIAL PRIMARY KEY,
    app_name VARCHAR(100) NOT NULL,
    user_id INT,
    prompt TEXT NOT NULL,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_schema.doc_embeddings (
    embedding_id SERIAL PRIMARY KEY,
    doc_ref VARCHAR(100) NOT NULL,
    embedding_vector TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE ai_schema.ai_call_logs IS 'AI呼び出し履歴を保存(全アプリ共通)';
COMMENT ON TABLE ai_schema.doc_embeddings IS 'RAG用途の文書Embeddingを保管';
