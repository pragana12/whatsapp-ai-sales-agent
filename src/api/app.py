import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException

from src.agent.service import AgentService
from src.api.schemas import EvolutionWebhookPayload, HealthResponse
from src.core.config import FileAgentConfigRepository
from src.core.logging import configure_logging
from src.core.rate_limit import InMemoryRateLimiter
from src.core.settings import Settings, get_settings
from src.integrations.evolution import EvolutionClient
from src.integrations.llm import ChatProvider, EmbeddingsProvider
from src.memory.store import InMemoryConversationStore
from src.rag.service import RetrieverService

logger = logging.getLogger(__name__)


class AppContainer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.config_repository = FileAgentConfigRepository(settings.agent_config_path)
        self.agent_config = self.config_repository.get_config()
        self.memory_store = InMemoryConversationStore()
        self.rate_limiter = InMemoryRateLimiter(limit=settings.webhook_rate_limit)
        self.evolution_client = EvolutionClient(
            api_url=settings.evolution_api_url,
            instance=settings.evolution_api_instance,
            api_key=settings.evolution_api_key,
        )
        self.retriever = RetrieverService(
            persist_dir=settings.chroma_persist_dir,
            embeddings_provider=EmbeddingsProvider(settings),
        )
        knowledge_base_path = Path(self.agent_config["knowledge_base_path"])
        if knowledge_base_path.exists() and not any(settings.chroma_persist_dir.iterdir()):
            self.retriever.ingest_file(knowledge_base_path)
        self.agent_service = AgentService(
            llm=ChatProvider(settings),
            config=self.agent_config,
            retriever=self.retriever,
            store=self.memory_store,
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    container = AppContainer(settings)
    app.state.container = container
    try:
        yield
    finally:
        pass


def create_app() -> FastAPI:
    app = FastAPI(
        title="WhatsApp AI Sales Agent",
        version=get_settings().app_version,
        lifespan=lifespan,
    )

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        settings = app.state.container.settings
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "ok",
        }

    @app.get("/health", response_model=HealthResponse, tags=["meta"])
    async def health() -> HealthResponse:
        container: AppContainer = app.state.container
        return HealthResponse(
            status="ok",
            version=container.settings.app_version,
            chroma_ready=container.retriever.healthcheck(),
            evolution_configured=container.evolution_client.configured,
        )

    @app.post("/webhook", tags=["webhook"])
    async def webhook(payload: EvolutionWebhookPayload) -> dict[str, str]:
        container: AppContainer = app.state.container
        return await process_webhook_payload(container, payload)

    return app


async def process_webhook_payload(
    container: AppContainer,
    payload: EvolutionWebhookPayload,
) -> dict[str, str]:
    if payload.event != "MESSAGES_UPSERT":
        return {"status": "ignored", "reason": "unsupported_event"}
    if payload.data.key.fromMe:
        return {"status": "ignored", "reason": "from_me"}

    text = payload.extract_text()
    if not text:
        raise HTTPException(status_code=400, detail="Unsupported message payload.")

    session_id = payload.data.key.remoteJid
    phone_number = payload.data.key.remoteJid.split("@")[0]
    if not container.rate_limiter.allow(phone_number):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")

    logger.info(
        "Processing inbound message",
        extra={
            "session_id": session_id,
            "phone_number": phone_number,
            "event_type": "webhook_received",
        },
    )
    state = container.agent_service.run(session_id, phone_number, text)
    await container.evolution_client.send_text(
        phone_number=phone_number,
        text=state["last_response"],
    )
    return {"status": "processed", "stage": state["current_stage"]}
