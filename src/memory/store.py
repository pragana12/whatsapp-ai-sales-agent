from copy import deepcopy

from src.core.models import ConversationState


class InMemoryConversationStore:
    def __init__(self) -> None:
        self._store: dict[str, ConversationState] = {}

    def get(self, session_id: str) -> ConversationState | None:
        state = self._store.get(session_id)
        return deepcopy(state) if state is not None else None

    def save(self, state: ConversationState) -> None:
        self._store[state["session_id"]] = deepcopy(state)

    def clear(self) -> None:
        self._store.clear()

