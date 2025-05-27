import streamlit as st
from core.engine import auto_generate_and_run_query
from core.history import init_history_db
from ui.layout import apply_custom_styles
from ui.typing_effect import render_typing_effect

# ✅ TEM QUE SER O PRIMEIRO COMANDO DO STREAMLIT
st.set_page_config(
    page_title="HuB-IA",
    page_icon="ui/static/detalhe.png",
    layout="centered"
)

init_history_db()
apply_custom_styles()

# ✅ Exibe a logo no canto superior
st.logo(
    image="ui/static/logo.png.png",
    size="large"
)

# Cria colunas para centralizar a imagem com espaçamento
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

st.markdown('<h1 aria-label="assistente HuB-IA">O que você quer saber?</h1>', unsafe_allow_html=True)

with st.form(key="consulta_form"):
    col1, col2 = st.columns([5, 1])
    with col1:
        question = st.text_input("Pergunte alguma coisa", label_visibility="collapsed", placeholder="Ex: Qual foi o IPCA em Recife?", key="question")
    with col2:
        submit = st.form_submit_button("⬆", use_container_width=True)

if submit and question.strip():
    try:
        resposta = auto_generate_and_run_query(question.strip())
        render_typing_effect(resposta["interpretacao"])
    except Exception as e:
        st.error(f"Erro: {e}")
