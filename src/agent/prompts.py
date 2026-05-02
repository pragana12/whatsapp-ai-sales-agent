from src.core.models import AgentConfig, ConversationState


def build_node_prompt(
    node_name: str,
    config: AgentConfig,
    state: ConversationState,
    retrieved_context: str = "",
) -> str:
    conversation = "\n".join(
        f"{message['role']}: {message['content']}" for message in state["messages"]
    )
    context_section = f"\nContexto RAG:\n{retrieved_context}\n" if retrieved_context else "\n"
    return (
        f"Você é {config['agent_name']}, um vendedor consultivo via WhatsApp.\n"
        f"Personalidade: {config['personality']}\n"
        f"Objetivo comercial: {config['sales_objective']}\n"
        f"Meta inicial: {config['welcome_goal']}\n"
        f"Etapa atual: {node_name}\n"
        f"Perfil parcial do lead: {state['lead_profile']}\n"
        f"Histórico:\n{conversation}\n"
        f"{context_section}"
        f"Mensagem mais recente do lead: {state['latest_user_message']}\n"
        "Responda em portugues do Brasil, com mensagem curta, natural e orientada para "
        "avancar a venda.\n"
        "Sempre produza uma única resposta ao cliente.\n"
    )
