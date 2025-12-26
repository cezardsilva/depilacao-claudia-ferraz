# Arquivo: main.py
# Versão: 3.0 - Cadastro e listagem de clientes com interface bonita

import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import date

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

# CSS personalizado (melhorado)
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
    .card {
        background-color: #2D2D2D;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255, 182, 193, 0.2);
        margin: 1rem 0;
        text-align: center;
    }
    .stButton>button {
        background-color: #FFB6C1;
        color: #1E1E1E;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.5rem;
    }
    .stButton>button:hover {
        background-color: #D4AF37;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">✨ Depilação Claudia Ferraz ✨</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Agenda de Clientes & Agendamentos</h2>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Navegação")
    menu = st.radio(
        "Escolha uma opção",
        ["🏠 Início", "👩‍🦰 Clientes", "📅 Agenda", "🔔 Notificações", "⚙️ Configurações"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("💖 Feito com carinho para a Claudia")

# Função para contar clientes
@st.cache_data(ttl=60)  # Atualiza a cada 60 segundos
def contar_clientes():
    try:
        response = supabase.table("clientes").select("id", count="exact").execute()
        return response.count or 0
    except:
        return 0

total_clientes = contar_clientes()

# Conteúdo principal
if menu == "🏠 Início":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="card">
                <h3>👥 Clientes</h3>
                <h2 style="color:#FFB6C1;">{total_clientes}</h2>
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
    if total_clientes == 0:
        st.info("🚀 Próximo passo: cadastrar a primeira cliente!")
    else:
        st.balloons()

elif menu == "👩‍🦰 Clientes":
    st.header("👩‍🦰 Gerenciar Clientes")

    # Tabs: Cadastro e Listagem
    tab1, tab2 = st.tabs(["✨ Nova Cliente", "📋 Todas as Clientes"])

    with tab1:
        with st.form("cadastro_cliente", clear_on_submit=True):
            st.subheader("Cadastrar Nova Cliente")

            nome = st.text_input("Nome completo *", placeholder="Ex: Maria Silva")
            telefone = st.text_input("Telefone *", placeholder="(XX) XXXXX-XXXX")
            data_nascimento = st.date_input("Data de nascimento", value=None, min_value=date(1900,1,1))
            observacoes = st.text_area("Observações", placeholder="Ex: prefere horários à tarde, pele sensível...")

            col1, col2, col3 = st.columns([1,1,2])
            with col1:
                submitted = st.form_submit_button("💾 Salvar Cliente")

            if submitted:
                if not nome.strip() or not telefone.strip():
                    st.error("⚠️ Nome e telefone são obrigatórios!")
                else:
                    try:
                        data = {
                            "nome": nome.strip(),
                            "telefone": telefone.strip(),
                            "data_nascimento": str(data_nascimento) if data_nascimento else None,
                            "observacoes": observacoes.strip() if observacoes.strip() else None
                        }
                        supabase.table("clientes").insert(data).execute()
                        st.success(f"✅ Cliente **{nome}** cadastrada com sucesso!")
                        st.cache_data.clear()  # Limpa cache para atualizar contagem
                    except Exception as e:
                        st.error("❌ Erro ao salvar. Tente novamente.")

    with tab2:
        st.subheader("Todas as Clientes")

        try:
            response = supabase.table("clientes").select("*").order("nome").execute()
            if response.data:
                import pandas as pd
                df = pd.DataFrame(response.data)
                df = df[['nome', 'telefone', 'data_nascimento', 'observacoes']]
                df.columns = ['Nome', 'Telefone', 'Data de Nascimento', 'Observações']

                # Busca
                busca = st.text_input("🔍 Buscar por nome ou telefone")
                if busca:
                    df = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)]

                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma cliente cadastrada ainda. Vamos começar?")
        except Exception as e:
            st.error("Erro ao carregar clientes.")

st.markdown("---")
st.caption("© 2025 Depilação Claudia Ferraz • Sistema exclusivo e personalizado")