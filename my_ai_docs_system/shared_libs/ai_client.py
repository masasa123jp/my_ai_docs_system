# .\shared-libs\ai_client.py
"""
ai_client.py
AI(LLM)を呼び出すクライアント処理をまとめる例
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

class AIClient:
    @staticmethod
    def call_llm(prompt: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            logger.error("OpenAI APIキーが設定されていません。")
            return "エラー: サービスが利用できません。"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "text-davinci-003",
            "prompt": prompt,
            "max_tokens": 200
        }
        try:
            resp = requests.post("https://api.openai.com/v1/completions", 
                                 headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["text"].strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM呼び出しエラー: {e}")
            return "エラー: AIサービスへの接続に失敗しました。"