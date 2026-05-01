from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
from langchain_groq import ChatGroq
from supabase import create_client, Client

# Carrega as variáveis de ambiente
load_dotenv()


# python
usuario_id = "65893036-8fd4-4f0c-90a2-f32ce8c46c56"
organization_uuid = "0c43a756-80da-4ee7-a38f-03b1e27396f4"

# Configuração da API OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = "https://kmfcaehfwzrpbdanhfyz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImttZmNhZWhmd3pycGJkYW5oZnl6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU5MjUxNDYsImV4cCI6MjA1MTUwMTE0Nn0.ZLtaZ6vuuoam2If4ItpG69LkrlA1mudSX9dCXYP-QUM"

def conectar_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)



# python
def carregar_dados(usuario, organizacao):
    supabase: Client = conectar_supabase()
    #resultado = supabase.table("ai_agent_configs").select("*").execute()
    # Correct
    resultado = (supabase.table("ai_agent_configs").select("*").eq("usuario_m", usuario_id).eq("organization_id", organization_uuid).execute())

    if not resultado.data:
        return None, None

    registro = resultado.data[0]
    baseclone = registro["personality"]
    nome = registro["agent_name"]
    contexto = registro["contexto"]
    treinamento = registro["treinamento"]
    return baseclone, nome, contexto, treinamento


# # Configuração do modelo e parser
# llm = ChatGroq(
#     model="llama3-groq-70b-8192-tool-use-preview", 
#     api_key=os.getenv("GROQ_API_KEY"),
# )

# # Configuração do modelo LLM
# llm = ChatOpenAI(
#     model="chatgpt-4o-latest",
#     openai_api_key=openai_api_key,
#     temperature=0.6,
# )
parser = StrOutputParser()

#Configuração do modelo e parser
llm = ChatGroq(
    model="llama3-groq-70b-8192-tool-use-preview", 
    api_key=os.getenv("GROQ_API_KEY"),
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


# Configuração do chat chain inicial
initial_chain = initial_template | llm | parser

    
baseclone, nome, treinamento, contexto = carregar_dados(usuario_id, organization_uuid)


print(baseclone, nome)


# Inicializar FastAPI
app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://your-frontend-domain.com",  # Adicione o domínio do seu frontend aqui
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo para a pergunta
class Pergunta(BaseModel):
    pergunta: str
    nome: str | None = None  # Optional field
    numero: str | None = None # Optional field

# Endpoint para o chatbot
@app.post("/chat")
async def chat(pergunta: Pergunta):
    try:
        # Print the additional fields
        print(f"Nome do usuário: {pergunta.nome}")
        print(f"Número do usuário: {pergunta.numero}")
        
        # Processar com invoke usando dicionário
        resposta = initial_chain.invoke({
            "contexto": contexto,
            "nome": nome,
            "treinamento": treinamento,
            "baseclone": baseclone,
            "pergunta": pergunta.pergunta
        })


        return {"resposta": resposta}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {str(e)}")

# Executar o servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)