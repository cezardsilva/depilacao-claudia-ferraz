# Arquivo: main.py
# Versão: 1.0 - Configuração inicial e teste de conexão com Supabase

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

# Configuração básica da página
st.set_page_config(
    page_title="Depilação Claudia Ferraz",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("✨ Depilação Claudia Ferraz")
st.markdown("### Agenda de Clientes & Agendamentos")

# Teste de conexão com o banco
with st.spinner("Conectando ao banco de dados..."):
    try:
        response = supabase.table("clientes").select("id", count="exact").limit(1).execute()
        st.success("✅ Conexão com Supabase estabelecida com sucesso!")
        st.info(f"Total de clientes na base: {response.count or 0}")
    except Exception as e:
        st.error("❌ Erro ao conectar com o Supabase")
        st.exception(e)
        st.stop()

st.markdown("---")
st.info("🚀 Próximos passos: vamos criar a interface bonita com tema personalizado!")