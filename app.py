import streamlit as st
from src.agent import criar_agente, perguntar

st.set_page_config(page_title="Assistente de Viagens", page_icon="✈️")
st.title("✈️ Assistente de Viagens")

if "agente" not in st.session_state:
    try:
        st.session_state.agente = criar_agente()
    except RuntimeError as erro:
        st.error(str(erro))
        st.stop()
    st.session_state.historico = [] 

with st.sidebar:
    st.header("Exemplos")
    st.markdown("- Vou para Santiago, no Chile, nesta semana. Como estará o clima nos próximos dias?\n"
                "- Quanto são 800 dólares em reais hoje?\n"
                "- Quais são as principais atrações de Nova York?\n"
                "- Quero passar 6 dias em Roma, gastando 90 euros por dia, com passagem de R$ 5.200. Qual o total em reais?\n"
                "- E se eu ficar 9 dias em vez de 6, e como estará o clima lá?")
    if st.button("🗑️ Nova conversa"):
        st.session_state.clear()
        st.rerun()

for papel, texto, passos in st.session_state.historico:
    with st.chat_message(papel):
        if passos:
            with st.expander("Ver raciocínio do agente"):
                for tipo, conteudo in passos:
                    st.markdown(f"**{tipo.capitalize()}:** {conteudo}")
        st.markdown(texto)

if pergunta := st.chat_input("Para onde você quer viajar?"):
    st.session_state.historico.append(("user", pergunta, []))
    with st.chat_message("user"):
        st.markdown(pergunta)
    with st.chat_message("assistant"):
        passos, resposta = [], ""
        with st.spinner("Pensando..."):
            for tipo, texto in perguntar(st.session_state.agente, pergunta, "streamlit"):
                if tipo == "resposta":
                    resposta = texto
                else:
                    passos.append((tipo, texto))
        with st.expander("Ver raciocínio do agente", expanded=False):
            for tipo, conteudo in passos:
                st.markdown(f"**{tipo.capitalize()}:** {conteudo}")
        st.markdown(resposta)
    st.session_state.historico.append(("assistant", resposta, passos))
