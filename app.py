import streamlit as st
import requests
import pymongo
import pandas as pd

st.set_page_config(page_title="Consultor Econômico IA", layout="centered")
st.title("📊 Consultor Econômico Fecomércio - IA")
# -----------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS MONGO
# -----------------------------
@st.cache_resource
def conectar_mongo():
    cliente = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.chxornv.mongodb.net/")
    db = cliente["fecomercio"]  # nome do banco
    colecao = db["fecomercio.json"]  # nome da coleção
    return colecao

colecao = conectar_mongo()

# -----------------------------
# FUNÇÃO PARA OBTER DADOS ECONÔMICOS DO MONGO
# -----------------------------
def consultar_dado(pergunta):
    # Exemplo simples: identificar o termo (ex: IPCA, Recife, 2024)
    dados = colecao.find()
    df = pd.DataFrame(list(dados))

    # Passar todo o dataframe para o modelo junto da pergunta (modo simplificado)
    contexto = df.to_markdown(index=False)
    prompt = f"""
    VOCÊ É UM CONSULTOR ECONÔMICO. RESPONDA COM BASE NOS DADOS ABAIXO:

    {contexto}

    PERGUNTA: {pergunta}

    RESPOSTA:
    """

    resposta = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi4",
            "prompt": prompt,
            "stream": False
        }
    )

    return resposta.json().get("response", "Erro ao gerar resposta.")

# -----------------------------
# STREAMLIT - INTERFACE
# -----------------------------


pergunta = st.text_input("Digite sua pergunta sobre os dados econômicos:", "Qual o IPCA de Recife em 2024?")

if st.button("Perguntar"):
    resposta = consultar_dado(pergunta)
    st.markdown("### Resposta da IA")
    st.success(resposta)