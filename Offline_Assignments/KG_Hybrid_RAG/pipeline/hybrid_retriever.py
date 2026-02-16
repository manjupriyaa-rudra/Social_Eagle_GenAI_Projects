from rank_bm25 import BM25Okapi
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from config.settings import settings


class HybridRetriever:
    def __init__(self, documents):
        self.docs = documents

        tokenized = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.vector = FAISS.from_texts(documents, embeddings)

    def retrieve(self, query, k=3):
        tokenized_query = query.split()

        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_bm25 = sorted(
            zip(self.docs, bm25_scores),
            key=lambda x: x[1],
            reverse=True
        )[:k]

        vector_results = self.vector.similarity_search(query, k=k)
        vector_texts = [doc.page_content for doc in vector_results]

        merged = list(set([doc for doc, _ in top_bm25] + vector_texts))
        return merged
