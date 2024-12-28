from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import AgentExecutor
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Carregar as variáveis de ambiente
load_dotenv()

# Configuração do modelo e parser
llm = ChatGroq(
    model="llama3-8b-8192", 
    api_key=os.getenv("GROQ_API_KEY"),
)



prompt_template = """
Você é um assistente especializado em marketing digital e afiliados. Seu trabalho é responder perguntas com base no texto fornecido abaixo e ajudar o cliente a entender os benefícios do curso digital do Julio Tavares, além de incentivá-lo de maneira amigável e confiante a realizar a compra.  

Importante: Você deve se passar pelo próprio Julio Tavares, falando de forma bem informal, autêntica e descontraída, como se estivesse conversando diretamente com a pessoa. Utilize frases motivacionais e técnicas de persuasão amigáveis, adaptando seu tom à linguagem apresentada no texto de exemplo.  

Exemplo de estilo de fala do Julio:  
"Depois dá uma olhada no saldo aí pra vê quando é pra colocar de novo."  
"Boaaa mano, eu vou lançar meu curso! Se tudo der como eu tô planejando, eu vou arrastar tu pro meu time."  
"Vai dar certo pô! Tu é muito bom no que faz. Se for vender o robô, vende um valor alto pq eles vão vender e vai faturar muito em cima."  

Suas respostas devem:
- Curtas e objetivas, alinhadas ao estilo do Julio.  
- Ser informais e motivadoras, alinhadas ao estilo do Julio.  
- Destacar os benefícios e diferenciais do curso, explicando como ele pode transformar a vida do cliente em poucas palavras 
- Criar conexão emocional com a pessoa, demonstrando que você entende as necessidades dela.  
- Ajudar a esclarecer dúvidas sobre o conteúdo, valor e resultados do curso.  
- Usar técnicas de venda sutis, como gerar urgência, valor percebido e confiança na escolha. 
- Não parecer um robô, seja autêntico e humano.
- Não pareça que quer vender algo e sim ajudar a pessoa a tomar a melhor decisão para ela. 


Texto:
{context}

Pergunta: {question}
Resposta:

"""

# Criar o prompt do LangChain
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template,
)


# Texto de referência para o chatbot (o texto fornecido acima)
context = """
Perguntas e Respostas Baseadas no Texto

1. O que é esse programa que está sendo oferecido?
É um programa de vendas de produtos digitais prontos, onde você pode se tornar sócio do Júlio Tavares, ganhar 100% de comissão em cada venda e trabalhar de forma simples com as ferramentas e materiais já disponibilizados.

2. O que preciso fazer para começar?
Basta preencher seus dados no formulário indicado, escolher a forma de pagamento (Pix ou parcelamento em até 12 vezes no cartão de crédito) e obter acesso imediato ao programa.

3. Quem pode participar desse programa?
Qualquer pessoa que deseja ganhar uma renda extra, trabalhando de casa, com um celular e acesso à internet, sem a necessidade de aparecer ou conversar com desconhecidos.

4. Preciso criar os produtos que vou vender?
Não. Todos os produtos já vêm prontos, incluindo páginas de vendas, criativos e materiais de divulgação.

5. É necessário aparecer ou conversar com pessoas?
Não. Você não precisa mostrar o rosto, falar com ninguém pelo WhatsApp ou insistir para que alguém compre.

6. Quanto posso ganhar com esse programa?
É possível faturar entre R$3.000 e R$10.000 ou mais por mês, dependendo de sua dedicação e estratégias de vendas.

7. Quais são as vantagens desse programa em relação a outros?

    Produtos prontos para venda.
    100% de comissão por venda.
    Estratégias ensinadas diretamente pelo Júlio Tavares.
    Trabalhar de qualquer lugar e no seu ritmo.
    Sem chefe, sem pressão.

8. O que está incluído no programa?

    Produtos digitais prontos para venda.
    Aulas sobre tráfego direto para anúncios eficazes.
    Encontros com o Júlio Tavares para orientação.
    Acesso à maior comunidade de infoprodutores que vende sem ser afiliado.

9. Quem é Júlio Tavares?
Ele é um profissional com aproximadamente 15 milhões de seguidores na internet, que encontrou o sucesso no marketing digital e deseja compartilhar seu método com outras pessoas.

10. Como funcionam os pagamentos?
Você pode pagar via Pix ou parcelar em até 12 vezes no cartão de crédito. Após o pagamento, o acesso ao programa é imediato.

11. E se eu nunca tiver vendido nada na internet?
Isso não é um problema. O programa inclui todo o treinamento necessário para que você aprenda a vender e tenha sucesso, mesmo sendo iniciante.

12. Qual é o diferencial desse programa?
Você vende produtos digitais com 100% de comissão e não precisa se preocupar com a criação de nada ou mesmo ser famoso para alcançar resultados.

13. Quanto tempo demora para começar a ganhar dinheiro?
Os resultados dependem do empenho de cada pessoa, mas com dedicação e aplicação das estratégias ensinadas, é possível obter resultados rapidamente.

14. Esse programa é um curso?
Não, é mais que um curso. Ele oferece produtos prontos, treinamento, suporte e materiais para começar a vender imediatamente.

15. Qual é a promessa principal do programa?
Ajudar você a mudar de vida, trabalhando de casa, sem chefe, e gerando renda extra de forma simples e prática.

"""


# Montagem da cadeia corretamente
cadeia = prompt | llm

# resposta = cadeia.invoke({"context": context, "question": "Quanto tempo demora para começar a ganhar dinheiro?"})

# # Exibir a resposta final com extração de texto
# print(resposta.content)



# ------------------ Perguntas Via API  -----------------------------


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

# Endpoint para o chat
@app.post("/chat")
async def chat(pergunta: Pergunta):
    try:
        resposta = cadeia.invoke({"context": context, "question": pergunta.pergunta})
        
        # Resposta_final
        return {"resposta": resposta.content}


    except Exception as e:
        # Em caso de erro, retorna uma mensagem de erro
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {e}")

# Executar o servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)