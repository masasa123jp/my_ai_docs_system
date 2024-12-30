-- ai_schema.ai_call_logs テーブルの作成
CREATE TABLE IF NOT EXISTS ai_schema.ai_call_logs (
    call_id SERIAL PRIMARY KEY,
    app_name VARCHAR(100) NOT NULL,
    user_id INTEGER,
    prompt TEXT NOT NULL,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ai_schema.doc_embeddings テーブルの作成
CREATE TABLE IF NOT EXISTS ai_schema.doc_embeddings (
    embedding_id SERIAL PRIMARY KEY,
    doc_ref VARCHAR(100) NOT NULL,
    embedding_vector TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- その他のテーブル作成SQL
