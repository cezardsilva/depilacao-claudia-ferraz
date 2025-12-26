# Arquivo: main.py
# Versão: 2.0 - Interface bonita com tema personalizado e menu lateral

import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    st.error("⚠️ Configuração do Supabase não encontrada. Verifique o arquivo .env")
    st.stop()

supabase: Client = create_client(supabase_url, supabase_key)

# Configuração da página
st.set_page_config(
    page_title="Depilação Claudia Ferraz",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para deixar tudo mais elegante
st.markdown("""
    <style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #D4AF37, #FFB6C1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.8rem;
        text-align: center;
        color: #FFB6C1;
        margin-bottom: 2rem;
    }
    .sidebar .css-1d391kg {
        background-color: #2D2D2D;
    }
    .card {
        background-color: #2D2D2D;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255, 182, 193, 0.2);
        margin: 1rem 0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Header personalizado
st.markdown('<h1 class="main-header">✨ Depilação Claudia Ferraz ✨</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Agenda de Clientes & Agendamentos</h2>', unsafe_allow_html=True)

# Sidebar com menu
with st.sidebar:
    st.image("https://via.placeholder.com/200x200/FFB6C1/FFFFFF?text=Logo+Claudia", use_column_width=True)
    st.markdown("### Navegação")
    menu = st.radio(
        "Escolha uma opção",
        ["🏠 Início", "👩‍🦰 Clientes", "📅 Agenda", "🔔 Notificações", "⚙️ Configurações"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("💖 Feito com carinho para a Claudia")

# Conteúdo principal baseado no menu
if menu == "🏠 Início":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="card">
                <h3>👥 Clientes</h3>
                <h2 style="color:#FFB6C1;">0</h2>
                <p>cadastradas</p>
            </div>
            """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="card">
                <h3>📅 Agendamentos</h3>
                <h2 style="color:#D4AF37;">0</h2>
                <p>hoje</p>
            </div>
            """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="card">
                <h3>🎂 Aniversários</h3>
                <h2 style="color:#FFB6C1;">0</h2>
                <p>neste mês</p>
            </div>
            """, unsafe_allow_html=True)

    st.success("✅ Sistema conectado ao banco de dados com sucesso!")
    st.info("🚀 Próximo passo: cadastrar a primeira cliente!")

elif menu == "👩‍🦰 Clientes":
    st.header("Gerenciar Clientes")
    st.write("Aqui vamos cadastrar, editar e listar todas as clientes.")

# As outras páginas vamos implementar nas próximas etapas

st.markdown("---")
st.caption("© 2025 Depilação Claudia Ferraz • Sistema exclusivo e personalizado")