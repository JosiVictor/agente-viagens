# ✈️ Assistente de Viagens com Agente ReAct (LangChain + Gemini)

## 1. Problema e solução
Planejar uma viagem exige abrir várias páginas: previsão do tempo, cotação da moeda, informações do destino e uma planilha para somar custos. Este projeto resolve isso com **um agente de IA** que conversa em português, decide sozinho quais ferramentas usar e junta tudo em um plano.

- **Público-alvo:** pessoas que planejam viagens de lazer e querem respostas rápidas e confiáveis.
- **Funcionalidades:** previsão de 7 dias, conversão de moedas, resumo de destinos (Wikipédia), cálculo de orçamento e memória da conversa.

## 2. Como funciona
| Componente | Implementação |
|---|---|
| LLM | Gemini (`gemini-3.5-flash-lite`) via `langchain-google-genai` |
| Framework | LangChain (`create_agent`) |
| Ferramentas | `previsao_do_tempo`, `converter_moeda`, `pesquisar_destino`, `calcular_orcamento` |
| ReAct | Ciclo Pensamento → Ação → Observação repetido até a resposta final; os passos aparecem na interface |
| Memória | `InMemorySaver` (checkpointer) com `thread_id` por conversa |
| Interface | Streamlit (`app.py`)

APIs externas usadas (gratuitas, sem chave): Open-Meteo, open.er-api.com e Wikipédia. Só o Gemini precisa de chave.

## 3. Estrutura
```
├── app.py            # interface Streamlit
├── src/
│   ├── config.py     # chave e modelo
│   ├── tools.py      # as 4 ferramentas
│   └── agent.py      # agente, memória e ReAct
├── requirements.txt
└── .env
```

## 4. Como executar
```bash
git clone <URL-DO-SEU-REPOSITORIO>
cd agente-viagens
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env        # Linux/Mac: cp .env.example .env
# edite o .env e cole sua GOOGLE_API_KEY (https://aistudio.google.com/apikey)
streamlit run app.py
```

## 5. Casos de uso testados
| # | Pergunta | Ferramentas esperadas | Resultado observado |
|---|---|---|---|
| 1 | "Vou para Santiago, no Chile, nesta semana. Como estará o clima nos próximos dias?" | previsao_do_tempo | _preencher_ |
| 2 | "Quanto são 800 dólares em reais hoje?" | converter_moeda | _preencher_ |
| 3 | "Quais são as principais atrações de Nova York?" | pesquisar_destino | _preencher_ |
| 4 | "Quero passar 6 dias em Roma, gastando 90 euros por dia, com passagem de R$ 5.200. Qual o total em reais?" | converter_moeda + calcular_orcamento | _preencher_ |
| 5 | "E se eu ficar 9 dias em vez de 6, e como estará o clima lá?" | memória + calcular_orcamento + previsao_do_tempo | _preencher_ |

## 6. Reflexão
**Sem o agente:** abrir site de clima, site de câmbio, Wikipédia e calculadora; copiar valores entre abas;

**Com o agente:** O agente escolhe as ferramentas, encadeia resultados (converte a moeda e depois calcula o orçamento) e lembra do contexto. Ainda é preciso conferir informações importantes, pois o LLM pode errar na interpretação; por isso os dados numéricos vêm sempre das ferramentas, não do modelo.
