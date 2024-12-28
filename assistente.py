import os
from openai import OpenAI
from dotenv import load_dotenv

# Carregar as variáveis de ambiente
load_dotenv()

# Obter a chave da API da OpenAI a partir das variáveis de ambiente
openai_api_key = os.getenv("OPENAI_API_KEY")

# Inicializar o cliente OpenAI
client = OpenAI(api_key=openai_api_key)

# Passo 1: Criar um Assistente
assistant = client.beta.assistants.create(
    name="Tutor de Matemática",
    instructions="Você é um assistente Financeiro e seu nome é João. O usuário tem uma conta premium.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o",
)

# Passo 2: Criar um Thread
thread = client.beta.threads.create()

def adicionar_mensagem(thread_id, role, content):
    return client.beta.threads.messages.create(
        thread_id=thread_id,
        role=role,
        content=content
    )

def criar_corrida(thread_id, assistant_id, instructions):
    return client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=instructions
    )

def listar_mensagens(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    # Converter o objeto em uma lista e filtrar a última mensagem do assistente
    messages_list = list(messages)
    for msg in reversed(messages_list):
        if msg.role == "assistant":
            print(f"Assistente: {msg.content}")
            break

# Loop para interação no terminal
print("Bem-vindo ao GITIA! Digite 'sair' para encerrar.")
while True:
    user_input = input("Você: ")
    if user_input.lower() == 'sair':
        break

    # Passo 3: Adicionar a mensagem do usuário ao thread
    adicionar_mensagem(thread.id, "user", user_input)

    # Passo 4: Criar uma corrida
    run = criar_corrida(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Por favor, trate o usuário como Paulo Lima. O usuário tem uma conta premium."
    )

    # Verificar o status da corrida e listar as mensagens
    if run.status == 'completed':
        listar_mensagens(thread.id)
    else:
        print(f"Status da corrida: {run.status}")