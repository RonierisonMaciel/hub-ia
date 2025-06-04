import streamlit as st
import requests
import pymongo
import pandas as pd

# -----------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------
st.set_page_config(page_title="Consultor Econômico IA", layout="centered")
st.title("📊 Consultor Econômico Fecomércio - IA")

# -----------------------------
# CONEXÃO COM MONGODB
# -----------------------------
@st.cache_resource
def conectar_mongo():
    cliente = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.chxornv.mongodb.net/")
    db = cliente["fecomercio"]  # nome do banco
    colecao = db["fecomercio.json"]  # nome da coleção
    return colecao

colecao = conectar_mongo()

# -----------------------------
# FUNÇÃO DE SEGURANÇA PARA FILTRAR COMANDOS PROIBIDOS
# -----------------------------
def contem_comando_proibido(texto):
    comandos_proibidos = ['delete', 'drop', 'remove', 'update', 'insert', 'shutdown', 'kill']
    texto_lower = texto.lower()
    return any(comando in texto_lower for comando in comandos_proibidos)

# -----------------------------
# FUNÇÃO PARA CONSULTAR DADOS
# -----------------------------
def consultar_dado(pergunta):
    if contem_comando_proibido(pergunta):
        return "❌ Ação não permitida. Comandos como DELETE, DROP, UPDATE, etc. são bloqueados por segurança."

    try:
        dados = colecao.find()
        df = pd.DataFrame(list(dados))

        if df.empty:
            return "Nenhum dado encontrado no banco de dados."

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
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        if resposta.status_code == 200:
            return resposta.json().get("response", "❌ Erro: resposta vazia.")
        else:
            return f"❌ Erro ao consultar o modelo: {resposta.status_code}"

    except Exception as e:
        return f"❌ Erro ao consultar dados: {e}"

# -----------------------------
# INTERFACE COM O USUÁRIO
# -----------------------------
pergunta = st.text_input("Digite sua pergunta econômica:")

if pergunta:
    resposta = consultar_dado(pergunta)
    st.markdown(f"### 🧠 Resposta:\n{resposta}")
