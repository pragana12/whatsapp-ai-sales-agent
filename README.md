# WhatsApp AI Sales Agent

Refatoração do projeto original de 2023 para uma arquitetura mais clara, modular e estudável. Nesta fase, o foco está em entender bem o fluxo do agente com `FastAPI + LangGraph + ChromaDB`, sem adicionar Supabase, Redis ou multi-tenant.

## Estado atual

- `POST /webhook` recebe mensagens no formato da Evolution API
- LangGraph orquestra o fluxo `qualify -> understand -> present -> objection -> close`
- Estado conversacional fica em memória
- Configuração do agente vem de arquivo local
- RAG usa ChromaDB local com embeddings OpenAI
- A v1 foi preservada em `legacy/`

## Estrutura

```text
src/
  api/            # rotas, schemas e composição da app
  agent/          # nós do grafo, prompts e serviço principal
  core/           # settings, logging, config e utilitários
  integrations/   # Evolution API, chat provider, embeddings
  memory/         # store de conversa em memória
  rag/            # retriever e ingestão local
legacy/           # versão antiga preservada
tests/            # testes de fluxo central
docs/             # documentação técnica
data/             # config e base local de conhecimento
```

## Como rodar

1. Copie `.env.example` para `.env`
2. Preencha as chaves que quiser usar
3. Instale dependências:

```bash
pip install -e ".[dev]"
```

4. Rode a aplicação:

```bash
uvicorn src.main:app --reload
```

5. Teste:

```bash
pytest
```

## Ingestão da base

```bash
python -m src.rag.ingestion --file data/knowledge_base.txt
```

## Próximos passos naturais

- trocar `FileAgentConfigRepository` por uma implementação em Supabase
- trocar `InMemoryConversationStore` por Redis
- adicionar roteamento multi-tenant
- endurecer health checks, observabilidade e deploy

## Documentação

- Arquitetura: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Workflow de publicação gradual: [docs/RELEASE_WORKFLOW.md](docs/RELEASE_WORKFLOW.md)
- PRD usado como referência: [prd.md](prd.md)
