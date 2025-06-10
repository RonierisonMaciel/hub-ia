import streamlit as st
import time
import logging
import re
import pandas as pd
import base64
import os
from rapidfuzz import process
from core.engine import auto_generate_and_run_query

try:
    from ollama._client import ResponseError
except ImportError:
    ResponseError = Exception

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA CHAMADA STREAMLIT)
# ============================================================================

st.set_page_config(
  
    page_title="Assistente Inteligente para Dados Públicos da Fecomércio",
    page_icon="ui/icons/detalhes.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mostrar a logo visível na página junto do título


# ============================================================================
# CONFIGURAÇÕES INICIAAS
# ============================================================================

# Configuração de logging
logging.basicConfig(filename="hubia_erros.log", level=logging.ERROR)

# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

def get_base64_image(image_path: str) -> str:
    """Converte uma imagem para base64 para uso em HTML/CSS"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        else:
            # Retorna uma imagem padrão em base64 se o ficheiro não existir
            # Esta é uma imagem 1x1 transparente como fallback
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    except Exception as e:
        logging.error(f"Erro ao carregar imagem {image_path}: {e}")
        return "iVBORw0KGgoAAAANSUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def corrigir_sql(sql: str) -> str:
    """Corrige problemas comuns em consultas SQL"""
    sql = re.sub(r"\"\s*-\s*(group|order|having|limit)\b", r"\"\n\1", sql, flags=re.IGNORECASE)
    sql = re.sub(r"([^\s])-(group|order|having|limit)\b", r"\1 \2", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s+;", ";", sql)
    return sql

def is_read_only_query(sql: str) -> bool:
    """Verifica se a consulta é apenas de leitura"""
    return sql.strip().lower().startswith("select")

def consultar(pergunta: str) -> tuple:
    """Executa consulta e retorna interpretação, SQL e dados"""
    resultado = auto_generate_and_run_query(pergunta.strip())
    sql_corrigido = corrigir_sql(resultado["sql"])
    return resultado["interpretacao"], sql_corrigido, resultado.get("resultado", [])

def sugerir_perguntas(pergunta: str) -> list:
    """Sugere perguntas relacionadas baseadas na pergunta atual"""
    pergunta_lower = pergunta.lower()
    
    sugestoes_por_tema = {
        "ipca": [
            "Qual a média do IPCA em 2023?",
            "Compare o IPCA entre Recife e Salvador",
            "Como variou o IPCA nos últimos 6 meses?"
        ],
        "pms": [
            "Qual foi a variação da PMS em São Paulo?",
            "PMS de 2020 a 2023 no Brasil",
            "Compare a PMS entre diferentes estados"
        ],
        "pmc": [
            "Como está o desempenho da PMC este ano?",
            "Compare a PMC entre diferentes regiões",
            "Qual a tendência da PMC nos últimos meses?"
        ],
        "cartão": [
            "Qual o volume de transações com cartão em 2023?",
            "Compare transações por débito e crédito",
            "Como evoluíram as transações digitais?"
        ]
    }
    
    for tema, sugestoes in sugestoes_por_tema.items():
        if tema in pergunta_lower or (tema == "cartão" and "cartao" in pergunta_lower):
            return sugestoes
    
    # Sugestões padrão
    return [
        "Qual a inflação acumulada em Recife?",
        "Como está o comércio em São Paulo?",
        "Mostre dados de serviços do último trimestre"
    ]

# ============================================================================
# ESTILOS CSS
# ============================================================================
def aplicar_estilos():
    """Aplica estilos CSS personalizados à aplicação"""
    st.markdown("""
        <style>
            /* Reset e configurações gerais */
            .main {
                padding-top: 0.5rem; 
            }

            /* Header personalizado */
            .header-container {
                background: linear-gradient(135deg, #f6d365 0%, #fda085 100%) !important;
                color: Black !important;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 0.5rem; /* Reduzido ainda mais */
                border-radius: 15px; /* Levemente reduzido */
                margin-bottom: 1.5rem; /* Reduzido ainda mais */
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
                position: relative;
                overflow: hidden;
                
            }

            .header-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                pointer-events: none;
                z-index: 0;
            }

            .title-container {
                color: Black !important;
                text-align: center;
                position: relative;
                z-index: 1;
               
            }

            .main-title {
                font-size: 1.8rem; /* Reduzido de 2.2rem */
                font-weight: 800;
                color: Black !important;
                margin: 0;
                letter-spacing: -0.5px; /* Levemente ajustado */
            }

            .sub-title {
                color: Black !important;
                font-size: 0.9rem; /* Reduzido de 1.1rem */
                color: rgba(255, 255, 255, 0.95);
                margin-top: 0.3rem; /* Reduzido de 0.5rem */
                font-weight: 400;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
            }

            /* Label do input */
            .input-label {
                margin-top: 25px;
                font-size: 1.1rem;
                font-weight: 700;
                color: #333;
                margin-bottom: 0.8rem;
                text-align: center;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }

            /* Estilo do input */
            .stTextInput > div > div > input {
                font-size: 1.1rem !important;
                padding: 0 0.5rem !important; /* Removemos o padding vertical para permitir centralização via flex */
                height: 100px !important;
                width: 250px !important;
                

                display: flex !important;           /* Habilita flexbox */
                align-items: center !important;     /* Centraliza verticalmente */
                justify-content: flex-start !important; /* Alinha à esquerda */

                border: none !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                transition: all 0.3s ease !important;
            }

            /* Estilo quando o input está em foco */
            .stTextInput > div > div > input:focus {
                outline: none !important;
                box-shadow: none !important;
                border: none !important;
            }

            /* Botão de envio melhorado */
            .stButton > button {
                background: linear-gradient(135deg, #f6d365 0%, #fda085 100%) !important;
                color: Black !important;
                border: none !important;
                padding: 0.8rem 2rem !important; /* Reduzido padding */
                border-radius: 15px !important;
                font-size: 1.1rem !important; /* Reduzido fonte */
                font-weight: 700 !important;
                transition: all 0.3s ease !important;
                width: 70% !important; /* Reduzido largura */
                display: block; /* Para centralizar */
                margin: 0.5rem auto; /* Centraliza o botão */
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
            }

            .stButton > button:hover {
                transform: translateY(-3px) !important;
                box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4) !important;
            }

            .stButton > button:active {
                transform: translateY(-1px) !important;
            }

            /* Área de resposta */
            .response-container {
                background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
                padding: 2.5rem;
                border-radius: 20px;
                border-left: 6px solid #667eea;
                margin: 2rem 0;
                deacti

            .response-text {
                font-size: 1.15rem;
                line-height: 1.7;
                color: #2c3e50;
                font-weight: 400;
            }

            /* Tabela de dados melhorada */
            .stDataFrame {
                border-radius: 15px !important;
                overflow: hidden !important;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1) !important;
                border: 1px solid #e8e8e8 !important;
            }

            /* Sidebar melhorada */
            .css-1d391kg {
                background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
            }

            /* Novo estilo para a logo na sidebar */
            .sidebar-logo {
                margin-top: -40px;
                width: 100px; /* Ajuste o tamanho conforme necessário */
                height: auto;
                display: block;
                margin-right: auto;
            }

            /* Sugestões melhoradas */
            .suggestions-container {
                background: linear-gradient(135deg, #e8f4fd 0%, #f0f8ff 100%);
                padding: 2rem;
                border-radius: 20px;
                margin-top: 2rem;
                border: 2px solid #b3d9ff;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }

            .suggestions-title {
                font-size: 1.3rem;
                font-weight: 700;
                color: #2c3e50;
                margin-bottom: 1.5rem;
                text-align: center;
            }

            .suggestion-item {
                background: white !important;
                color: #2c3e50 !important;
                border: 2px solid #e8f4fd !important;
                margin: 0.8rem 0 !important;
                border-radius: 12px !important;
                padding: 1rem 1.5rem !important;
                transition: all 0.3s ease !important;
                font-weight: 500 !important;
            }

            .suggestion-item:hover {
                transform: translateX(8px) !important;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
                border-color: #667eea !important;
            }

            /* Alertas e mensagens */
            .stAlert {
                border-radius: 15px !important;
                border: none !important;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
            }

            /* Histórico melhorado */
            .history-item {
                background: rgba(255, 255, 255, 0.15) !important;
                color: white !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                margin: 0.8rem 0 !important;
                border-radius: 10px !important;
                padding: 1rem !important;
                transition: all 0.3s ease !important;
                font-weight: 500 !important;
            }

            .history-item:hover {
                background: rgba(255, 255, 255, 0.3) !important;
                box-shadow: 0 4px 15px rgba(255, 255, 255, 0.2) !important;
                border-color: rgba(255, 255, 255, 0.4) !important;
            }
        </style>
    """, unsafe_allow_html=True)


# ============================================================================
# ESTADO DA SESSÃO
# ============================================================================

def inicializar_estado():
    """Inicializa o estado da sessão"""
    if "historico" not in st.session_state:
        st.session_state.historico = []
    if "resposta_atual" not in st.session_state:
        st.session_state.resposta_atual = None
    if "mostrar_sobre" not in st.session_state:
        st.session_state.mostrar_sobre = False

# ============================================================================
# COMPONENTES DA INTERFACE
# ============================================================================

def renderizar_header():
    """Renderiza o cabeçalho da aplicação"""
    st.markdown(f"""
        <div class="header-container fade-in">
            <div class="title-container">
                <h1 class="main-title">HuB‑IA</h1>
                <p class="sub-title">Assistente Inteligente para Dados Públicos da Fecomércio</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def renderizar_sidebar():
    """Renderiza a barra lateral"""
    with st.sidebar:
        logo_base64 = get_base64_image("UI/icons/logo.png")
        st.markdown(f"<img src=\"data:image/png;base64,{logo_base64}\" class=\"sidebar-logo\" alt=\"HuB-IA Logo\">", unsafe_allow_html=True)
        
        
        # Botão Sobre
        if st.button("Sobre o HuB-IA", use_container_width=True):
            st.session_state.mostrar_sobre = not st.session_state.mostrar_sobre

        st.markdown("---")
        
        # Histórico
        st.markdown("## 🕘 Histórico")
        
        if st.session_state.historico:
            # Mostra os últimos 10 itens do histórico
            for i, item in enumerate(reversed(st.session_state.historico[-10:])):
                pergunta_resumida = item["pergunta"][:45] + "..." if len(item["pergunta"]) > 45 else item["pergunta"]
                if st.button(f"📝 {pergunta_resumida}", key=f"hist_{i}", use_container_width=True):
                    st.session_state.resposta_atual = item
                    st.rerun()
        else:
            st.markdown("*Nenhuma consulta ainda*")
        
        # Botão limpar histórico (movido para a sidebar)
        if st.session_state.historico:
            st.markdown("---")
            if st.button("🧹 Limpar histórico", use_container_width=True):
                st.session_state.historico.clear()
                st.session_state.resposta_atual = None
                st.rerun()
        
        # Estatísticas do histórico
        if st.session_state.historico:
            st.markdown("---")
            st.markdown("### 📊 Estatísticas")
            st.metric("Total de consultas", len(st.session_state.historico))

def renderizar_sobre():
    """Renderiza a seção 'Sobre'"""
    st.markdown("""
        <div class="about-container fade-in">
            <h2>Sobre o HuB-IA</h2>
            <p>O <b>HuB-IA</b> é um assistente inteligente desenvolvido para facilitar o acesso e a análise de dados públicos da Fecomércio. Utilizando inteligência artificial, ele permite que você faça perguntas em linguagem natural e obtenha respostas precisas e insights valiosos a partir de grandes volumes de dados.</p>
            <h3>Funcionalidades:</h3>
            <ul>
                <li><b>Consultas em Linguagem Natural:</b> Faça perguntas como se estivesse conversando.</li>
                <li><b>Análise de Dados:</b> Obtenha tabelas e gráficos relevantes para suas perguntas.</li>
                <li><b>Histórico de Consultas:</b> Revise e reutilize suas perguntas anteriores.</li>
                <li><b>Sugestões Inteligentes:</b> Receba recomendações de perguntas para explorar ainda mais os dados.</li>
            </ul>
            <h3>Tecnologias Utilizadas:</h3>
            <ul>
                <li><b>Streamlit:</b> Para a construção da interface web interativa.</li>
                <li><b>Modelos de Linguagem (LLMs):</b> Para processamento de linguagem natural e geração de SQL.</li>
                <li><b>Pandas:</b> Para manipulação e análise de dados.</li>
                <li><b>SQL:</b> Para interação com bancos de dados.</li>
            </ul>
            <p>Desenvolvido com o objetivo de democratizar o acesso à informação e apoiar a tomada de decisões estratégicas.</p>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# LÓGICA PRINCIPAL DA APLICAÇÃO
# ============================================================================

def main():
    inicializar_estado()
    aplicar_estilos()

    renderizar_sidebar()
    renderizar_header()

    if st.session_state.mostrar_sobre:
        renderizar_sobre()
    else:
       
        pergunta_usuario = st.text_area(
        "Faça sua pergunta aqui:",
        placeholder="Ex: Qual o IPCA acumulado em 2023 em Recife?",
        height=100,  # altura em pixels
    )


        # Botões de ação
        col1, col2, col3 = st.columns([1, 2, 1]) # Colunas para centralizar o botão de enviar

        with col2: # Botão de enviar na coluna do meio
            enviar_button = st.button(" Enviar Pergunta  🚀", use_container_width=True)
        
        # O botão de limpar foi movido para a sidebar

        if enviar_button and pergunta_usuario:
            with st.spinner("Processando sua pergunta..."): # Adiciona spinner
                try:
                    interpretacao, sql_gerado, dados_resultado = consultar(pergunta_usuario)
                    st.session_state.resposta_atual = {
                        "pergunta": pergunta_usuario,
                        "interpretacao": interpretacao,
                        "sql": sql_gerado,
                        "resultado": dados_resultado
                    }
                    st.session_state.historico.append(st.session_state.resposta_atual)
                except ResponseError as e:
                    st.error(f"Erro na consulta: {e.msg}")
                    st.session_state.resposta_atual = None
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado: {e}")
                    st.session_state.resposta_atual = None
            st.rerun()

        if st.session_state.resposta_atual:
            st.markdown("""
                <div class="response-container fade-in">
                    <h3>✨ Interpretação:</h3>
                    <p class="response-text">{}</p>
            """.format(st.session_state.resposta_atual["interpretacao"]), unsafe_allow_html=True)

            if st.session_state.resposta_atual["resultado"]:
                df = pd.DataFrame(st.session_state.resposta_atual["resultado"])
                st.write("### 📊 Dados:")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Nenhum dado retornado para esta consulta.")

            st.markdown("""
                </div>
            """, unsafe_allow_html=True)

            # Sugestões de perguntas
            st.markdown("""
                <div class="suggestions-container fade-in">
                    <p class="suggestions-title">💡 Sugestões de Próximas Perguntas:</p>
            """, unsafe_allow_html=True)
            
            sugestoes = sugerir_perguntas(st.session_state.resposta_atual["pergunta"])
            for i, sugestao in enumerate(sugestoes):
                if st.button(sugestao, key=f"sug_{i}", use_container_width=True, help="Clique para usar esta sugestão como sua próxima pergunta.", type="secondary"):
                    st.session_state.resposta_atual = None # Limpa a resposta atual para nova consulta
                    st.session_state.pergunta_sugerida = sugestao # Armazena a sugestão para preencher o text_input
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.markdown("""
                <div class="placeholder-text fade-in">
                   
                </div>
            """, unsafe_allow_html=True)

    st.markdown("""
        <div class="footer">
            <p></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()


