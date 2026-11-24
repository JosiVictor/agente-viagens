from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from src.config import GEMINI_MODEL, GOOGLE_API_KEY, validar_config
from src.tools import FERRAMENTAS

SYSTEM_PROMPT = """Você é o Viajante, um assistente de planejamento de viagens.
Fale sempre em português, de forma simpática e objetiva.

Siga o método React: use as ferramentas disponíveis para obter informações, raciocine passo a passo e só então dê a resposta final.
- Nunca invente clima, cotações ou valores: use as ferramentas.
- Use calcular_orcamento para somar custos.
- Se faltar informação essencial (destino, nº de dias, orçamento), pergunte.
- Use o histórico da conversa, entenda pelo contexto.
- Na resposta final, resuma o plano em tópicos curtos."""


def _texto(conteudo) -> str:
    if isinstance(conteudo, str):
        return conteudo
    return "".join(
        bloco.get("text", "") if isinstance(bloco, dict) else str(bloco)
        for bloco in conteudo
    )


def criar_agente():
    validar_config()
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY, temperature=0.3
    )
    return create_agent(
        model=llm,
        tools=FERRAMENTAS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),  
    )


def perguntar(agente, pergunta: str, thread_id: str = "sessao-1"):
    config = {"configurable": {"thread_id": thread_id}}
    entrada = {"messages": [{"role": "user", "content": pergunta}]}
    try:
        for atualizacao in agente.stream(entrada, config, stream_mode="updates"):
            for conteudo in atualizacao.values():
                for msg in (conteudo or {}).get("messages", []):
                    if isinstance(msg, AIMessage) and msg.tool_calls:
                        for chamada in msg.tool_calls:
                            yield "acao", f"{chamada['name']}({chamada['args']})"
                    elif isinstance(msg, ToolMessage):
                        yield "observacao", _texto(msg.content)
                    elif isinstance(msg, AIMessage):
                        yield "resposta", _texto(msg.content)
    except Exception as erro:
        yield "resposta", f"Desculpe, ocorreu um erro ao processar: {erro}"
