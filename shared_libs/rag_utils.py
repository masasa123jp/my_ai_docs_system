# .\shared-libs\rag_utils.py
"""
rag_utils.py
RAG検索(Embedding)関連の共通処理サンプル
"""

from typing import List

class RAGSearcher:
    @staticmethod
    def search_docs(query: str) -> List[str]:
        """
        ダミー実装: 本来はベクトルDBやpgvectorを用いて
        queryのEmbeddingと既存Embeddingを比較し、類似文書を取得
        """
        # 仮に2つの文書を返す例
        doc_snippets = [
            "Doc snippet 1 about the query",
            "Doc snippet 2 about the query"
        ]
        return doc_snippets

    @staticmethod
    def index_document(doc_id, content: str) -> None:
        """
        ダミー実装: 新しい文書をEmbedding化してベクトルDBに登録
        """
        # 何もしない
        pass
