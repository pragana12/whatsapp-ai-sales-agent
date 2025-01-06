from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from supabase import create_client, Client
import os
import requests
import json

# ESSE CÓDIGO É UM TESTE E NÃO FOI APROVADO ATÉ O MOMENTO !!!!!!


# Carregar variáveis de ambiente
load_dotenv()

# Configurar FastAPI
app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://your-frontend-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variáveis de Ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_INSTANCE = os.getenv("EVOLUTION_API_INSTANCE")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Conexão com Supabase
def conectar_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Carregar dados do Supabase
def carregar_dados(usuario_id, organization_uuid):
    supabase: Client = conectar_supabase()
    resultado = (
        supabase.table("ai_agent_configs")
        .select("*")
        .eq("usuario_m", usuario_id)
        .eq("organization_id", organization_uuid)
        .execute()
    )

    if not resultado.data:
        return None, None, None, None

    registro = resultado.data[0]
    baseclone = registro["personality"]
    nome = registro["agent_name"]
    contexto = registro["contexto"]
    treinamento = registro["treinamento"]
    return baseclone, nome, contexto, treinamento

# Configurar LLM
parser = StrOutputParser()
llm = ChatGroq(
    model="llama3-groq-70b-8192-tool-use-preview",
    api_key=GROQ_API_KEY,
    verbose=True,
    temperature=0.9,
)

# Template para a cadeia inicial
initial_template = PromptTemplate(
    input_variables=["pergunta", "treinamento", "baseclone", "nome", "contexto"],
    template="""

    Você é um assistente virtual que deve se comportar exatamente como {nome}.
    Seu trabalho é responder perguntas com base dados abaixo e ajudar o cliente a entender os benefícios, além de incentivá-lo de maneira amigável e confiante a realizar a compra.
    Importante: Você deve se passar pelo próprio {nome}, falando de forma bem informal, autêntica e descontraída, como se estivesse conversando diretamente com a pessoa. Utilize frases motivacionais e técnicas de persuasão amigáveis, adaptando seu tom à linguagem apresentada na base clone fornecida.
    Comece sempre perguntando o nome da pessoa.
    Crie um ambiente de confiança e empatia, e incentive o cliente a fazer perguntas sobre o produto ou serviço.
    não envie mensagens grandes, apenas mensagens curtas e objetivas.
    

Seu objetivo é:  
1. Responder a todas as perguntas de forma amigável e clara, como se fosse o próprio {nome}
2. Evitar parecer um robô ou usar textos prontos. Cada resposta deve ser personalizada e transmitir autenticidade.  
3. Garantir que suas respostas são detalhadas, úteis e 100% baseadas no conteúdo do arquivo de treinamento.  

A cada resposta, lembre-se de:\n
- Usar o estilo de escrita do {nome}, como se estivesse falando diretamente com a pessoa.  
- Ser confiante, amigável, e atencioso, como {nome} faria.  
- Garantir que a linguagem seja natural, sem qualquer indício de que você é um agente automatizado.  

Responda como se você fosse {nome}, garantindo que a resposta seja autêntica e personalizada.

    Exemplo de estilo de fala do {nome}:  
    {baseclone}

Suas respostas devem:  
- Ser informais e motivadoras, alinhadas ao estilo do {nome}.  
- Destacar os benefícios e diferenciais do produto, explicando como ele pode transformar a vida do cliente.  
- Criar conexão emocional com a pessoa, demonstrando que você entende as necessidades dela.  
- Ajudar a esclarecer dúvidas sobre o conteúdo, valor e resultados do produto.  
- Usar técnicas de venda sutis, como gerar urgência, valor percebido e confiança na escolha.  

Sempre use suas respostas de forma informal e termine com um incentivo positivo.

Informações sobre o produto ou serviço:
{treinamento}

Se precisar de mais informações, ou quiser saber algo do usuário você pode perguntar para que a conversa seja natural como uma bate papo.

Para que você possa continuar a conversa durante o chat, aqui está o contexto atual:
{contexto}

Ultima Pergunta do cliente abaixo: 

Pergunta: {pergunta}

Continue a conversa com o cliente, respondendo de forma amigável e autêntica, como se fosse o próprio {nome}.
Sempre faça uma pergunta ao final para incentivar o cliente a continuar a conversa.
Não comece falando ja dos produtos ou serviços. Interaja e incentive o cliente a perguntar sobre os produtos ou serviços.
Quando você perceber que o cliente esta interessado, você pode falar sobre os produtos ou serviços.
Use técnicas de PNL e persuasão para incentivar o cliente a comprar.
lembre-se que seu objetivo é caminhar a conversa para o fechamento da venda.
não fique conversando demais
se perceber que no contexto ja tem informação suficiente para ir para o fechamento da venda, você pode ir para o fechamento da venda.
Se achar que ainda precisa de mais informações continue pedindo informações ao cliente.
"""
)

# Configurar a cadeia inicial
initial_chain = initial_template | llm | parser

# Função para enviar mensagens pela Evolution API
def send_response_to_whatsapp(phone, message):
    route = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_API_INSTANCE}"
    headers = {
        'Content-Type': 'application/json',
        'apikey': EVOLUTION_API_KEY
    }
    payload = {
        "number": phone,
        "textMessage": {
            "text": message
        }
    }
    response = requests.post(route, json=payload, headers=headers)
    return response.json()

@app.post('/webhook')
async def webhook(request: Request):
    body = await request.body()
    json_body = json.loads(body)

    try:
        # Verifica o tipo do evento
        if json_body.get("event") != "MESSAGES_UPSERT":
            return {"status": "ignored", "message": "Evento não é MESSAGES_UPSERT"}

        # Processar mensagem (conforme o código anterior)
        message = None
        if "extendedTextMessage" in json_body["data"]["message"]:
            message = json_body["data"]["message"]["extendedTextMessage"]["text"]
        elif "conversation" in json_body["data"]["message"]:
            message = json_body["data"]["message"]["conversation"]
        else:
            return {"status": "error", "message": "Mensagem não contém formato esperado"}, 400

        sender = json_body["data"]["key"]["remoteJid"]
        isMessageFromMe = json_body["data"]["key"]["fromMe"]

        # Ignorar mensagens enviadas pelo próprio sistema
        if isMessageFromMe:
            return {"status": "ignored"}

        # Continuação conforme o código anterior
        usuario_id = "65893036-8fd4-4f0c-90a2-f32ce8c46c56"
        organization_uuid = "-a38f-03b1e27396f4"
        baseclone, nome, contexto, treinamento = carregar_dados(usuario_id, organization_uuid)

        if not baseclone or not nome or not contexto or not treinamento:
            return {"status": "error", "message": "Dados do agente não encontrados"}, 400

        resposta = initial_chain.invoke({
            "contexto": contexto,
            "nome": nome,
            "treinamento": treinamento,
            "baseclone": baseclone,
            "pergunta": message
        })

        send_response_to_whatsapp(sender, resposta)
        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": f"Erro interno: {str(e)}"}, 500


# Rota inicial para teste
@app.get('/')
async def root():
    return {"message": "Webhook da IA conectado!"}
