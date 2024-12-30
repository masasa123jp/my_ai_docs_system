-- ._bk\db\create_tables_user.sql
-- ユーザーアプリ(文書管理)用スキーマ: doc_app
select current_setting('client_encoding'); -- 現在のクライアントエンコーディングを確認
set client_encoding to 'utf8'; -- 変更
CREATE SCHEMA IF NOT EXISTS doc_app;

-- メイン文書テーブル(部門ローカルで使う)
CREATE TABLE IF NOT EXISTS doc_app.local_docs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

COMMENT ON TABLE doc_app.local_docs IS 'ユーザーアプリ(文書管理)のローカル文書';

-- タグ管理 (多対多)
CREATE TABLE IF NOT EXISTS doc_app.doc_tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS doc_app.doc_tag_links (
    doc_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (doc_id, tag_id)
);

ALTER TABLE doc_app.doc_tag_links
    ADD CONSTRAINT fk_doc_taglinks_docs
    FOREIGN KEY (doc_id)
    REFERENCES doc_app.local_docs (id)
    ON DELETE CASCADE;

ALTER TABLE doc_app.doc_tag_links
    ADD CONSTRAINT fk_doc_taglinks_tags
    FOREIGN KEY (tag_id)
    REFERENCES doc_app.doc_tags (tag_id)
    ON DELETE CASCADE;

-- バージョン管理テーブル
CREATE TABLE IF NOT EXISTS doc_app.local_doc_versions (
    version_id SERIAL PRIMARY KEY,
    doc_id INT NOT NULL,
    version_num INT NOT NULL,
    content TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE doc_app.local_doc_versions
    ADD CONSTRAINT fk_doc_ver_docs
    FOREIGN KEY (doc_id)
    REFERENCES doc_app.local_docs (id)
    ON DELETE CASCADE;

-- バージョン更新用のPL/pgSQLファンクション例
CREATE OR REPLACE FUNCTION doc_app.fn_increment_version(
    p_doc_id INT,
    p_content TEXT
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_latest_ver INT;
    v_next_ver INT;
    v_vid INT;
BEGIN
    SELECT COALESCE(MAX(version_num), 0)
      INTO v_latest_ver
      FROM doc_app.local_doc_versions
     WHERE doc_id = p_doc_id;

    v_next_ver := v_latest_ver + 1;

    INSERT INTO doc_app.local_doc_versions(doc_id, version_num, content)
    VALUES (p_doc_id, v_next_ver, p_content)
    RETURNING version_id INTO v_vid;

    RETURN v_vid;
END;
$$;
