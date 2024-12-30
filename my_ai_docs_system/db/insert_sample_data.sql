-- insert_sample_data.sql
-- 例: HubApp(auth_schema, hub_docs, ai_schema) と
--     user-app-docs(doc_app) にサンプルを投入
select current_setting('client_encoding'); -- 現在のクライアントエンコーディングを確認
set client_encoding to 'utf8'; -- 変更
-- ===================================================================
-- HubApp: auth_schema
-- ===================================================================
-- サンプルユーザーの挿入
INSERT INTO auth_schema.users (id, username, hashed_password, is_active, email)
VALUES 
  (1,'admin', 'sha256hash_admin', TRUE, 'admin@sample.com'),
  (2,'doc_user', '$2b$12$UsKncTaSSKVC8zCnJ6yKJ.uhHY682G9Ko44dbrQ92cmVj8ikOgBiG', TRUE, 'doc_user@sample.com');

-- サンプルクライアントの挿入
INSERT INTO auth_schema.clients (id, client_id, client_secret, redirect_uri, is_active)
VALUES 
(1, 'your-client-id-from-hub-app', 'your-client-secret-from-hub-app', 'http://localhost:8100/callback', TRUE),
(2, 'client456', 'secret456', 'http://localhost:8100/callback', TRUE);

-- NOTE: sessionsはログイン時にINSERTされる想定なのでここでは割愛

-- ===================================================================
-- HubApp: hub_docs
-- ===================================================================
INSERT INTO hub_docs.documents (title, content)
VALUES
  ('Company-Wide Policy', 'All employees must follow...'),
  ('IT Security Guidelines', 'Please keep your password safe...');

-- ===================================================================
-- HubApp: ai_schema
-- ===================================================================
INSERT INTO ai_schema.ai_call_logs (app_name, user_id, prompt, response)
VALUES
  ('user-app-docs', 2, 'Summarize IT Security doc', 'Security doc summary: ...');

INSERT INTO ai_schema.doc_embeddings (doc_ref, embedding_vector)
VALUES
  ('hub_docs.documents:1', '[0.11, 0.22, 0.33]'),
  ('hub_docs.documents:2', '[0.44, 0.55, 0.66]');

-- ===================================================================
-- User-app-docs: doc_app
-- ===================================================================
INSERT INTO doc_app.local_docs (title, content)
VALUES
  ('Local Policy A', 'Local doc content A...'),
  ('Memo about HR changes', 'Memo: New HR policies this quarter...');

INSERT INTO doc_app.doc_tags (tag_name, description)
VALUES
  ('urgent', 'Time-sensitive'), 
  ('draft', 'Draft status');

INSERT INTO doc_app.doc_tag_links (doc_id, tag_id)
VALUES
  (1, 1),  -- doc_id=1 => 'urgent'
  (2, 2);  -- doc_id=2 => 'draft'

-- Version example
INSERT INTO doc_app.local_doc_versions (doc_id, version_num, content)
VALUES (1, 1, 'Version 1 of local policy A');
INSERT INTO doc_app.local_doc_versions (doc_id, version_num, content)
VALUES (1, 2, 'Version 2 with changes');
