from src.agent.service import AgentService
from src.memory.store import InMemoryConversationStore


class StubChatProvider:
    def invoke(self, prompt: str) -> str:
        if "Etapa atual: close" in prompt:
            return "Se fizer sentido, posso te passar o proximo passo para fechar."
        if "Etapa atual: objection" in prompt:
            return "Faz sentido essa objecao. Posso te mostrar por que o investimento retorna?"
        if "Etapa atual: present" in prompt:
            return "Com base no que voce me disse, essa solucao resolve isso de forma pratica."
        if "Etapa atual: understand" in prompt:
            return "Entendi. Qual resultado voce quer atingir mais rapido?"
        return "Antes de te indicar algo, me conta melhor seu momento."


class StubRetriever:
    def retrieve(self, query: str, limit: int = 3) -> list[str]:
        return [f"contexto para {query}"]


def test_agent_service_runs_full_flow_and_persists_state() -> None:
    config = {
        "agent_name": "Paulo",
        "personality": "Consultivo",
        "sales_objective": "Fechar a venda",
        "welcome_goal": "Criar rapport",
        "knowledge_base_path": "data/knowledge_base.txt",
        "max_objection_loops": 2,
    }
    store = InMemoryConversationStore()
    service = AgentService(
        llm=StubChatProvider(),
        config=config,
        retriever=StubRetriever(),
        store=store,
    )

    first = service.run("session-1", "5511999999999", "Oi, meu nome e Ana")
    assert first["messages"][-1]["role"] == "assistant"
    assert "qualify" in first["node_trace"]

    second = service.run(
        "session-1",
        "5511999999999",
        "Quero vender melhor no WhatsApp, mas achei caro.",
    )
    assert second["current_stage"] == "close"
    assert second["objections_handled"] >= 1
    assert second["retrieved_chunks"]
    assert len(second["messages"]) >= 4

