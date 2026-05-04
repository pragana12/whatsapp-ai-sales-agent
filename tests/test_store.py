from src.memory.store import InMemoryConversationStore


def test_store_round_trip_isolated_copy() -> None:
    store = InMemoryConversationStore()
    state = {
        "session_id": "abc",
        "phone_number": "123",
        "latest_user_message": "oi",
        "messages": [],
        "lead_profile": {},
        "current_stage": "qualify",
        "objections_handled": 0,
        "ready_to_close": False,
        "retrieved_chunks": [],
        "last_response": "",
        "should_handle_objection": False,
        "missing_fields": [],
        "max_objection_loops": 2,
        "node_trace": [],
    }
    store.save(state)
    loaded = store.get("abc")
    assert loaded is not None
    loaded["messages"].append({"role": "user", "content": "mutacao"})
    reloaded = store.get("abc")
    assert reloaded is not None
    assert reloaded["messages"] == []

