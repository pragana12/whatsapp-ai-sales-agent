from typing import Any, cast

from src.agent.graph import build_graph
from src.core.models import AgentConfig, ConversationState
from src.integrations.llm import ChatProvider
from src.memory.store import InMemoryConversationStore
from src.rag.service import RetrieverService


class AgentService:
    def __init__(
        self,
        llm: ChatProvider,
        config: AgentConfig,
        retriever: RetrieverService,
        store: InMemoryConversationStore,
    ) -> None:
        self._graph: Any = build_graph(llm, config, retriever)
        self._config = config
        self._store = store

    def run(self, session_id: str, phone_number: str, user_message: str) -> ConversationState:
        existing_state = self._store.get(session_id)
        state = existing_state or self._build_initial_state(session_id, phone_number)
        state["latest_user_message"] = user_message
        state["messages"].append({"role": "user", "content": user_message})
        final_state = self._graph.invoke(state)
        final_state["messages"].append(
            {"role": "assistant", "content": final_state["last_response"]}
        )
        self._store.save(final_state)
        return cast(ConversationState, final_state)

    def _build_initial_state(self, session_id: str, phone_number: str) -> ConversationState:
        return {
            "session_id": session_id,
            "phone_number": phone_number,
            "latest_user_message": "",
            "messages": [],
            "lead_profile": {},
            "current_stage": "qualify",
            "objections_handled": 0,
            "ready_to_close": False,
            "retrieved_chunks": [],
            "last_response": "",
            "should_handle_objection": False,
            "missing_fields": ["name", "objective", "pain_point"],
            "max_objection_loops": self._config["max_objection_loops"],
            "node_trace": [],
        }
