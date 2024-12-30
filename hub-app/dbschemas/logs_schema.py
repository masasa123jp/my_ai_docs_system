# .\hub-app\dbschemas\logs_schema.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

LogsBase = declarative_base()

# ログテーブルの例
class APILog(LogsBase):
    __tablename__ = "api_logs"
    __table_args__ = {"schema": "logs_schema"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False)
    request_body = Column(Text, nullable=True)
    response_status = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)