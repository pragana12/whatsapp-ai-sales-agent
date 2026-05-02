from typing import Protocol

from langchain_core.embeddings import FakeEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import SecretStr

from src.core.settings import Settings


class ChatModel(Protocol):
    def invoke(self, input: str) -> object:
        """Generate a response from the underlying model."""


class ChatProvider:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model: ChatOpenAI | None = None
        if settings.openrouter_api_key:
            self._model = ChatOpenAI(
                model=settings.openrouter_model,
                api_key=SecretStr(settings.openrouter_api_key),
                base_url=settings.openrouter_base_url,
                temperature=0.5,
            )

    def invoke(self, prompt: str) -> str:
        if self._model is None:
            return (
                "Perfeito. Me conta um pouco mais do seu contexto para eu te indicar a melhor "
                "forma de avancar."
            )
        response = self._model.invoke(prompt)
        content = getattr(response, "content", "")
        return content if isinstance(content, str) else str(content)


class EmbeddingsProvider:
    def __init__(self, settings: Settings) -> None:
        self._embeddings: OpenAIEmbeddings | FakeEmbeddings
        if settings.openai_api_key:
            self._embeddings = OpenAIEmbeddings(
                model=settings.openai_embedding_model,
                api_key=SecretStr(settings.openai_api_key),
            )
        else:
            self._embeddings = FakeEmbeddings(size=32)

    @property
    def client(self) -> OpenAIEmbeddings | FakeEmbeddings:
        return self._embeddings
