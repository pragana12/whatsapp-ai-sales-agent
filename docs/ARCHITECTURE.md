# Architecture

## Current scope

This refactor intentionally runs in single-tenant mode, with local config and in-memory conversation state. The goal is to make the orchestration and data flow easy to study before adding Supabase, Redis, or multi-tenant routing.

## Runtime flow

1. Evolution API sends `POST /webhook`.
2. FastAPI validates the payload with Pydantic.
3. The app loads the current conversation state from `InMemoryConversationStore`.
4. `AgentService` runs a LangGraph flow with these nodes:
   `qualify -> understand -> present -> objection -> close`.
5. `present` queries ChromaDB through `RetrieverService`.
6. The final response is sent back through `EvolutionClient`.

## Boundary design

- `AgentConfigRepository` is file-backed today and can later become a Supabase repository.
- `InMemoryConversationStore` can later become a Redis-backed implementation without changing the graph nodes.
- `ChatProvider` and `EmbeddingsProvider` isolate provider-specific configuration from the agent core.
- `RetrieverService` hides the vector store details from the graph.

## State model

Each conversation keeps:

- `session_id`
- `phone_number`
- `messages`
- `lead_profile`
- `current_stage`
- `objections_handled`
- `ready_to_close`
- `retrieved_chunks`
- `last_response`

## Known limitations

- State is lost when the process restarts.
- Only one local agent config is supported.
- Knowledge-base bootstrapping is local and file-based.
- Health checks are lightweight and focused on local study/development.

