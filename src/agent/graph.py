from typing import Any

from langgraph.graph import END, StateGraph

from src.agent.nodes import (
    close_node,
    handle_objection_node,
    present_solution_node,
    qualify_lead_node,
    understand_need_node,
)
from src.core.models import AgentConfig, ConversationState
from src.integrations.llm import ChatProvider
from src.rag.service import RetrieverService


def build_graph(
    llm: ChatProvider,
    config: AgentConfig,
    retriever: RetrieverService,
) -> Any:
    graph = StateGraph(ConversationState)
    graph.add_node("qualify", lambda state: qualify_lead_node(state, llm, config))
    graph.add_node("understand", lambda state: understand_need_node(state, llm, config))
    graph.add_node("present", lambda state: present_solution_node(state, llm, config, retriever))
    graph.add_node("objection", lambda state: handle_objection_node(state, llm, config))
    graph.add_node("close", lambda state: close_node(state, llm, config))

    graph.set_entry_point("qualify")
    graph.add_conditional_edges(
        "qualify",
        lambda state: "understand" if state["missing_fields"] else "present",
        {"understand": "understand", "present": "present"},
    )
    graph.add_edge("understand", "present")
    graph.add_conditional_edges(
        "present",
        lambda state: "objection" if state["should_handle_objection"] else "close",
        {"objection": "objection", "close": "close"},
    )
    graph.add_conditional_edges(
        "objection",
        lambda state: "present" if state["should_handle_objection"] else "close",
        {"present": "present", "close": "close"},
    )
    graph.add_edge("close", END)
    return graph.compile()
