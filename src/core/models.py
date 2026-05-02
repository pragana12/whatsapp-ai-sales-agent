from typing import Literal, NotRequired, TypedDict


class AgentConfig(TypedDict):
    agent_name: str
    personality: str
    sales_objective: str
    welcome_goal: str
    knowledge_base_path: str
    max_objection_loops: int


Stage = Literal["qualify", "understand", "present", "objection", "close"]


class ConversationMessage(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str


class LeadProfile(TypedDict, total=False):
    name: str
    experience_level: str
    objective: str
    pain_point: str


class ConversationState(TypedDict):
    session_id: str
    phone_number: str
    latest_user_message: str
    messages: list[ConversationMessage]
    lead_profile: LeadProfile
    current_stage: Stage
    objections_handled: int
    ready_to_close: bool
    retrieved_chunks: list[str]
    last_response: str
    should_handle_objection: bool
    missing_fields: list[str]
    max_objection_loops: int
    node_trace: NotRequired[list[str]]

