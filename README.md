# 📊 Consultor Econômico Fecomércio - IA

Este projeto é uma aplicação web interativa desenvolvida com **Streamlit**, que permite consultas inteligentes sobre dados econômicos armazenados em um banco de dados **MongoDB**. A interface simula um consultor econômico virtual que interpreta os dados e responde perguntas em linguagem natural.

## 🔍 Objetivo

Facilitar o acesso e a interpretação de indicadores econômicos por meio de uma interface simples, acessível e baseada em IA.

## ✅ Funcionalidades

- Interface web com **Streamlit**
- Conexão com base de dados MongoDB (Atlas)
- Consulta de dados econômicos via linguagem natural
- Exibição dos dados em formato tabular
- Geração de contexto para respostas automatizadas

## 🧰 Tecnologias utilizadas

- Python
- Streamlit
- PyMongo
- Requests
- Pandas
- MongoDB Atlas

## 🚀 Como executar

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/seu-usuario/seu-projeto.git
   cd seu-projeto

## Crie um ambiente virtual (opcional, mas recomendado):

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

## Instale as dependências:

bash
Copy
Edit
pip install -r requirements.txt

## Execute o app:

streamlit run app.py


## 🛠 Estrutura esperada
text
Copy
Edit
consultor-economico/
├── app.py
├── requirements.txt
└── README.md

## Certifique-se de que o banco de dados MongoDB esteja corretamente configurado e acessível via URI.

## 📌 Observações
Para segurança, evite deixar credenciais como admin:admin no código em produção.

O código está configurado para buscar todos os dados da coleção fecomercio.json e gerar um contexto em Markdown.

A lógica de IA pode ser expandida para integrar com modelos de linguagem como OpenAI GPT, se desejado.
