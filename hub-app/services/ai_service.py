# .\hub-app\services\ai_service.py

from shared_libs.ai_client import AIClient
from shared_libs.rag_utils import RAGSearcher
from sqlalchemy.orm import Session
from dbschemas.ai_schema import AICallLogs
from dbschemas.docs_schema import Document
from datetime import datetime
import logging

class AIService:
    @staticmethod
    def generate_text(prompt: str, db: Session) -> str:
        try:
            generated_text = AIClient.call_llm(prompt)
            # ログを保存
            log = AICallLogs(
                app_name="AIService",
                user_id=None,  # 必要に応じてユーザーIDを設定
                prompt=prompt,
                response=generated_text,
                created_at=datetime.utcnow()
            )
            db.add(log)
            db.commit()
            return generated_text
        except Exception as e:
            logging.error(f"Error in generate_text: {e}")
            raise e

    @staticmethod
    def rag_search_and_answer(query: str, db: Session) -> str:
        try:
            docs = RAGSearcher.search_docs(query)
            if not docs:
                return "No relevant docs found"
            combined = "\n".join(docs)
            prompt = f"以下の文書を参考に質問に回答:\n{combined}\n質問:{query}"
            generated_answer = AIClient.call_llm(prompt)
            # ログを保存
            log = AICallLogs(
                app_name="AIService",
                user_id=None,  # 必要に応じてユーザーIDを設定
                prompt=prompt,
                response=generated_answer,
                created_at=datetime.utcnow()
            )
            db.add(log)
            db.commit()
            return generated_answer
        except Exception as e:
            logging.error(f"Error in rag_search_and_answer: {e}")
            raise e