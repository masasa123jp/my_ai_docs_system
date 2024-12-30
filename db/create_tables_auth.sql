-- auth_schema.users テーブルの作成
CREATE TABLE IF NOT EXISTS auth_schema.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- auth_schema.sessions テーブルの作成
CREATE TABLE IF NOT EXISTS auth_schema.sessions (
    session_id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_schema.users(id),
    expires_at TIMESTAMP NOT NULL
);

-- その他のテーブル作成SQL
