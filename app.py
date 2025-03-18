import streamlit as st
from gpt4all import GPT4All
from database import generate_response

st.title("🏦 BDI (Banco de Dados Intelligence)")




# 🎛️ Interface no Streamlit
with st.form("query_form"):
    user_input = st.text_area("Digite sua pergunta:", "Qual foi o último valor do IPCA em Recife?")
    submitted = st.form_submit_button("Consultar")

    if submitted:
        response = generate_response(user_input)
        st.markdown(response)
