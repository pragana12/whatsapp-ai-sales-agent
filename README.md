# Documentação do Projeto de Chatbot com FastAPI e LangChain

## Introdução
Este é um projeto de chatbot desenvolvido utilizando FastAPI, LangChain e OpenAI para responder de forma personalizada às perguntas de usuários. O chatbot foi configurado para simular o estilo de linguagem de Expert, utilizando técnicas de persuasão e uma abordagem informal.

## Funcionalidades Principais
1. **Resposta a perguntas**: Gera respostas baseadas em um contexto pré-definido e dinâmico, utilizando modelos de linguagem avançados.
2. **Estilo personalizado**: Responde no estilo de linguagem do Expert.
3. **Persistência de contexto**: Salva as interações no arquivo `context.txt` para uso futuro.
4. **Configuração dinâmica**: Permite adicionar mais contexto dinamicamente a partir do arquivo `context.txt`.

## Estrutura do Código
O projeto é dividido em diversas partes:

### 1. Dependências
As bibliotecas utilizadas incluem:
- **FastAPI**: Para criar a API.
- **LangChain**: Para gerenciar a interação com os modelos de linguagem.
- **OpenAI**: Para acessar os modelos da OpenAI.
- **pydantic**: Para validação de dados.
- **dotenv**: Para carregar variáveis de ambiente.
- **uvicorn**: Para executar o servidor.

Instale todas as dependências com o seguinte comando:
```bash
pip install fastapi uvicorn pydantic python-dotenv langchain langchain-openai langchain-core
```

### 2. Variáveis de Ambiente
As chaves de API para OpenAI e GROQ devem ser armazenadas em um arquivo `.env`. Exemplo do arquivo:
```
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
```

Certifique-se de que o arquivo `.env` está localizado no mesmo diretório do seu projeto.

### 3. Configuração do Modelo LLM
O código utiliza o modelo `gpt-3.5-turbo` da OpenAI:
```python
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=openai_api_key,
    temperature=0.7,
)
```
O `StrOutputParser` é usado para tratar a saída textual do modelo.

### 4. Template de Prompt
O prompt é configurado para:
- Personalizar as respostas no estilo informal do Expert.
- Destacar benefícios de um curso digital, incentivando a compra.

Exemplo:
```python
initial_template = PromptTemplate(
    input_variables=["pergunta", "contexto"],
    template="""
    Você é um assistente especializado em marketing digital e afiliados. ...
    """
)
```

### 5. Persistência de Contexto
As interações são salvas no arquivo `context.txt` para reutilização futura:
```python
def carregar_contexto():
    try:
        with open("context.txt", "r") as file:
            lines = file.readlines()
            return "".join(lines[-4:])
    except FileNotFoundError:
        return ""
```

### 6. Configuração do FastAPI
O servidor é inicializado utilizando o FastAPI e configurado para aceitar CORS:
```python
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

O endpoint principal recebe perguntas e retorna respostas:
```python
@app.post("/chat")
async def chat(pergunta: Pergunta):
    ...
```

### 7. Execução do Servidor
Para iniciar o servidor, utilize o comando:
```bash
uvicorn chatbot:app --reload
```
- Substitua `chatbot` pelo nome do arquivo principal, caso diferente.
- O servidor ficará acessível em: [http://localhost:8000](http://localhost:8000).

## Arquivo `context.txt`
Esse arquivo registra as interações do chatbot:
- Perguntas enviadas pelos usuários.
- Respostas geradas pelo modelo.

Exemplo:
```
Pergunta: Qual o benefício do curso?
Resposta: Aeee meu fi! Esse curso vai te colocar no jogo, com 100% de comissão em cada venda...
```

## Exemplos de Uso
### Requisição via cURL
Envie uma pergunta para o chatbot usando cURL:
```bash
curl -X POST "http://localhost:8000/chat" \
-H "Content-Type: application/json" \
-d '{"pergunta": "O que o curso oferece?"}'
```
### Resposta Esperada
```json
{
  "resposta": "Aeee meu fi! Esse curso vai te transformar..."
}
```

## Conclusão
Este projeto é uma implementação robusta para criar um chatbot especializado e dinâmico. Siga os passos descritos para configurar e iniciar o servidor, e adapte o contexto ou prompt conforme suas necessidades.


## Como Funciona o Script
Este script combina diversas ferramentas para criar um chatbot que responde perguntas de forma personalizada. Abaixo está uma explicação didática para que mesmo quem não tenha experiência em programação possa entender:

1. **Recebendo a Pergunta:**
   - O usuário faz uma pergunta ao chatbot, que é enviada ao servidor por meio de um endpoint chamado `/chat`.

2. **Carregando o Contexto:**
   - O script busca informações adicionais no arquivo `context.txt` para criar uma resposta mais rica e relevante. Se o arquivo não existir, o chatbot usa apenas o contexto predefinido.

3. **Gerando a Resposta:**
   - A pergunta e o contexto são enviados ao modelo de inteligência artificial configurado no script. Esse modelo, treinado para entender e gerar texto, cria uma resposta no estilo do Expert.

4. **Salvando a Interação:**
   - Tanto a pergunta quanto a resposta são gravadas no arquivo `context.txt` para que o chatbot possa "lembrar" dessa conversa no futuro.

5. **Enviando a Resposta:**
   - O chatbot devolve a resposta gerada ao usuário de forma amigável e motivacional.

6. **Fácil Acesso:**
   - O servidor FastAPI permite que o chatbot seja acessado por meio de aplicativos ou diretamente pelo navegador, bastando enviar as perguntas para o endpoint correto.

Assim, o script funciona como um "cérebro digital" que entende perguntas, busca informações relevantes e gera respostas de maneira personalizada e persuasiva.

