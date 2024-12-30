# .\hub-app\alembic\env.py

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# アプリケーションのデータベースとモデルをインポート
from app.database import Base, DATABASE_URL  # 必要に応じてインポートパスを調整
from app import models  # 全てのモデルがBaseに登録されていることを確認

# Alembic Configオブジェクトを取得
config = context.config

# ロギング設定を読み込む
fileConfig(config.config_file_name)

# モデルのメタデータを設定
target_metadata = Base.metadata

def get_url():
    # 環境変数からDATABASE_URLを取得
    return os.getenv("DATABASE_URL", DATABASE_URL)  # fallbackとして設定ファイルから

def run_migrations_offline():
    """'offline'モードでマイグレーションを実行"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # オプション: カラム型の変更を検出
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """'online'モードでマイグレーションを実行"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # オプション: カラム型の変更を検出
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()