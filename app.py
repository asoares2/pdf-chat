import streamlit as st
import PyPDF2
from anthropic import Anthropic
import tempfile
import os
from io import BytesIO


def check_api_key():
    """Verifica se a API key está configurada corretamente."""
    try:
        if "secrets" not in st.__dict__:
            return False, "Secrets não configuradas no Streamlit."
            
        if "ANTHROPIC_API_KEY" not in st.secrets:
            return False, "ANTHROPIC_API_KEY não encontrada nas secrets. Verifique a configuração."
            
        if not st.secrets["ANTHROPIC_API_KEY"]:
            return False, "ANTHROPIC_API_KEY está vazia."
            
        return True, "API key configurada corretamente."
    except Exception as e:
        return False, f"Erro ao verificar API key: {str(e)}"

def get_claude_response(prompt, pdf_content):
    """Obtém resposta da API do Claude."""
    # Verifica a API key
    is_valid, message = check_api_key()
    if not is_valid:
        return f"Erro: {message}"
    
    try:
        client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        system_prompt = f"""Você é um assistente útil que ajuda a responder perguntas sobre o seguinte documento:

        {pdf_content}

        Por favor, responda às perguntas baseando-se apenas no conteúdo do documento fornecido."""

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Erro ao obter resposta: {str(e)}"



# Configuração da página Streamlit
st.set_page_config(page_title="Chat com PDF", layout="wide")

# Inicialização das variáveis de estado da sessão
if 'pdf_content' not in st.session_state:
    st.session_state.pdf_content = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_file_name' not in st.session_state:
    st.session_state.current_file_name = None
if 'user_question' not in st.session_state:
    st.session_state.user_question = ""

def extract_text_from_pdf(pdf_file):
    """Extrai texto do arquivo PDF."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def get_claude_response(prompt, pdf_content):
    """Obtém resposta da API do Claude."""
    # Usa a API key das secrets do Streamlit
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    client = Anthropic(api_key=api_key)
    
    system_prompt = f"""Você é um assistente útil que ajuda a responder perguntas sobre o seguinte documento:

    {pdf_content}

    Por favor, responda às perguntas baseando-se apenas no conteúdo do documento fornecido."""

    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Erro ao obter resposta: {str(e)}"

def process_input():
    if st.session_state.user_question:
        question = st.session_state.user_question
        st.session_state.user_question = ""
        st.session_state.chat_history.append(("user", question))
        response = get_claude_response(question, st.session_state.pdf_content)
        st.session_state.chat_history.append(("assistant", response))

# Interface principal
st.title("📚 Chat com PDF")

# Upload do arquivo
uploaded_file = st.sidebar.file_uploader("Faça upload do seu PDF", type="pdf")

if uploaded_file:
    # Verifica se é um novo arquivo
    current_file_name = uploaded_file.name
    if current_file_name != st.session_state.current_file_name:
        # Novo arquivo detectado - atualiza o conteúdo
        st.session_state.pdf_content = extract_text_from_pdf(uploaded_file)
        st.session_state.current_file_name = current_file_name
        st.session_state.chat_history = []  # Limpa o histórico do chat
        st.sidebar.success(f"Novo PDF carregado: {current_file_name}")

    # Área de chat
    st.subheader("💬 Chat")
    
    # Mostra qual arquivo está sendo analisado
    st.info(f"📄 Arquivo atual: {st.session_state.current_file_name}")
    
    # Campo de entrada para a pergunta com callback
    st.text_input(
        "Digite sua pergunta sobre o documento:",
        key="user_question",
        on_change=process_input,
        value=st.session_state.user_question
    )

    # Exibe o histórico do chat
    for role, content in reversed(st.session_state.chat_history):
        if role == "user":
            st.write("🧑 Você:", content)
        else:
            st.write("🤖 Assistente:", content)

else:
    st.info("Por favor, faça upload de um arquivo PDF no menu lateral para começar.")

# Botão para limpar o histórico
if st.sidebar.button("Limpar Histórico"):
    st.session_state.chat_history = []
    st.experimental_rerun()
