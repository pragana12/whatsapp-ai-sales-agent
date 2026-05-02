import re
from copy import deepcopy

from src.agent.prompts import build_node_prompt
from src.core.models import AgentConfig, ConversationState
from src.integrations.llm import ChatProvider
from src.rag.service import RetrieverService


def _append_trace(state: ConversationState, node_name: str) -> None:
    trace = list(state.get("node_trace", []))
    trace.append(node_name)
    state["node_trace"] = trace


def _find_missing_fields(state: ConversationState) -> list[str]:
    missing: list[str] = []
    profile = state["lead_profile"]
    for field in ("name", "objective", "pain_point"):
        if not profile.get(field):
            missing.append(field)
    return missing


def qualify_lead_node(
    state: ConversationState,
    llm: ChatProvider,
    config: AgentConfig,
) -> ConversationState:
    next_state = deepcopy(state)
    message = next_state["latest_user_message"]
    profile = next_state["lead_profile"]
    if not profile.get("name"):
        match = re.search(r"meu nome e ([a-zA-ZÀ-ÿ]+)", message, re.IGNORECASE)
        if match:
            profile["name"] = match.group(1)
    next_state["missing_fields"] = _find_missing_fields(next_state)
    next_state["current_stage"] = "qualify"
    next_state["should_handle_objection"] = False
    next_state["last_response"] = llm.invoke(build_node_prompt("qualify", config, next_state))
    _append_trace(next_state, "qualify")
    return next_state


def understand_need_node(
    state: ConversationState,
    llm: ChatProvider,
    config: AgentConfig,
) -> ConversationState:
    next_state = deepcopy(state)
    lowered = next_state["latest_user_message"].lower()
    if not next_state["lead_profile"].get("objective"):
        next_state["lead_profile"]["objective"] = lowered
    if not next_state["lead_profile"].get("pain_point"):
        next_state["lead_profile"]["pain_point"] = lowered
    next_state["missing_fields"] = _find_missing_fields(next_state)
    next_state["current_stage"] = "understand"
    next_state["should_handle_objection"] = False
    next_state["last_response"] = llm.invoke(build_node_prompt("understand", config, next_state))
    _append_trace(next_state, "understand")
    return next_state


def present_solution_node(
    state: ConversationState,
    llm: ChatProvider,
    config: AgentConfig,
    retriever: RetrieverService,
) -> ConversationState:
    next_state = deepcopy(state)
    retrieved_chunks = retriever.retrieve(next_state["latest_user_message"])
    next_state["retrieved_chunks"] = retrieved_chunks
    next_state["current_stage"] = "present"
    lowered = next_state["latest_user_message"].lower()
    next_state["should_handle_objection"] = any(
        token in lowered for token in ("caro", "difícil", "duvida", "não sei", "nao sei")
    )
    next_state["ready_to_close"] = not next_state["should_handle_objection"]
    next_state["last_response"] = llm.invoke(
        build_node_prompt("present", config, next_state, "\n".join(retrieved_chunks))
    )
    _append_trace(next_state, "present")
    return next_state


def handle_objection_node(
    state: ConversationState,
    llm: ChatProvider,
    config: AgentConfig,
) -> ConversationState:
    next_state = deepcopy(state)
    next_state["current_stage"] = "objection"
    next_state["objections_handled"] += 1
    next_state["should_handle_objection"] = (
        next_state["objections_handled"] < next_state["max_objection_loops"]
    )
    next_state["ready_to_close"] = not next_state["should_handle_objection"]
    next_state["last_response"] = llm.invoke(build_node_prompt("objection", config, next_state))
    _append_trace(next_state, "objection")
    return next_state


def close_node(
    state: ConversationState,
    llm: ChatProvider,
    config: AgentConfig,
) -> ConversationState:
    next_state = deepcopy(state)
    next_state["current_stage"] = "close"
    next_state["ready_to_close"] = True
    next_state["should_handle_objection"] = False
    next_state["last_response"] = llm.invoke(build_node_prompt("close", config, next_state))
    _append_trace(next_state, "close")
    return next_state
