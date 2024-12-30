# .\hub-app\dbschemas\core_schema.py

from sqlalchemy.ext.declarative import declarative_base

CoreBase = declarative_base()

# 必要に応じて coreテーブルを定義
# 例:
# class SomeCoreTable(CoreBase):
#     __tablename__ = "some_core_table"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)