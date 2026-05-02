from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.integrations.llm import EmbeddingsProvider


class RetrieverService:
    def __init__(self, persist_dir: Path, embeddings_provider: EmbeddingsProvider) -> None:
        self._persist_dir = persist_dir
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        self._embeddings_provider = embeddings_provider
        self._collection_name = "sales_agent_knowledge"

    def ingest_file(self, file_path: Path) -> int:
        content = file_path.read_text(encoding="utf-8")
        chunks = [chunk.strip() for chunk in content.splitlines() if chunk.strip()]
        documents = [Document(page_content=chunk) for chunk in chunks]
        if not documents:
            return 0
        Chroma.from_documents(
            documents=documents,
            embedding=self._embeddings_provider.client,
            persist_directory=str(self._persist_dir),
            collection_name=self._collection_name,
        )
        return len(documents)

    def retrieve(self, query: str, limit: int = 3) -> list[str]:
        try:
            store = Chroma(
                persist_directory=str(self._persist_dir),
                embedding_function=self._embeddings_provider.client,
                collection_name=self._collection_name,
            )
            documents = store.similarity_search(query=query, k=limit)
            return [document.page_content for document in documents]
        except Exception:
            return []

    def healthcheck(self) -> bool:
        return self._persist_dir.exists()
