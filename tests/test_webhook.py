from pathlib import Path

from src.api.app import AppContainer, process_webhook_payload
from src.api.schemas import EvolutionWebhookPayload
from src.core.settings import get_settings
from src.rag.service import RetrieverService


async def test_webhook_processes_supported_payload(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "agent_config.json"
    config_path.write_text(
        """
        {
          "agent_name": "Paulo",
          "personality": "Consultivo",
          "sales_objective": "Fechar venda",
          "welcome_goal": "Criar rapport",
          "knowledge_base_path": "data/knowledge_base.txt",
          "max_objection_loops": 2
        }
        """,
        encoding="utf-8",
    )
    monkeypatch.setenv("AGENT_CONFIG_PATH", str(config_path))
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setattr(RetrieverService, "ingest_file", lambda self, path: 0)
    monkeypatch.setattr(RetrieverService, "retrieve", lambda self, query, limit=3: ["stub context"])
    get_settings.cache_clear()

    container = AppContainer(get_settings())
    payload = EvolutionWebhookPayload.model_validate(
        {
            "event": "MESSAGES_UPSERT",
            "data": {
                "key": {"remoteJid": "5511999999999@s.whatsapp.net", "fromMe": False},
                "message": {"conversation": "Oi, meu nome e Carla"},
            },
        }
    )

    response = await process_webhook_payload(container, payload)

    assert response["status"] == "processed"
    assert container.memory_store.get("5511999999999@s.whatsapp.net") is not None


async def test_webhook_ignores_from_me(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "agent_config.json"
    config_path.write_text(
        """
        {
          "agent_name": "Paulo",
          "personality": "Consultivo",
          "sales_objective": "Fechar venda",
          "welcome_goal": "Criar rapport",
          "knowledge_base_path": "data/knowledge_base.txt",
          "max_objection_loops": 2
        }
        """,
        encoding="utf-8",
    )
    monkeypatch.setenv("AGENT_CONFIG_PATH", str(config_path))
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setattr(RetrieverService, "ingest_file", lambda self, path: 0)
    monkeypatch.setattr(RetrieverService, "retrieve", lambda self, query, limit=3: ["stub context"])
    get_settings.cache_clear()

    container = AppContainer(get_settings())
    payload = EvolutionWebhookPayload.model_validate(
        {
            "event": "MESSAGES_UPSERT",
            "data": {
                "key": {"remoteJid": "5511999999999@s.whatsapp.net", "fromMe": True},
                "message": {"conversation": "teste"},
            },
        }
    )

    response = await process_webhook_payload(container, payload)

    assert response["status"] == "ignored"
