from pathlib import Path

from src.core.settings import get_settings
from src.integrations.llm import EmbeddingsProvider
from src.rag.service import RetrieverService


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Ingest a knowledge base file into ChromaDB.")
    parser.add_argument("--file", required=True, help="Path to the knowledge base text file.")
    args = parser.parse_args()

    settings = get_settings()
    retriever = RetrieverService(
        persist_dir=settings.chroma_persist_dir,
        embeddings_provider=EmbeddingsProvider(settings),
    )
    count = retriever.ingest_file(Path(args.file))
    print(f"Ingested {count} chunks.")


if __name__ == "__main__":
    main()

