# Arquivo: main.py
# Versão: 3.1 - Cadastro, Listagem, Edição e Exclusão de Clientes

import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import date
import pandas as pd

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

# CSS personalizado (com melhorias para botões)
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
        border-radius: 8px;
        font-weight: bold;
        height: 2.5rem;
    }
    button[kind="primary"] {
        background-color: #FFB6C1 !important;
        color: #1E1E1E !important;
    }
    button[kind="primary"]:hover {
        background-color: #D4AF37 !important;
        color: white !important;
    }
    button[kind="secondary"] {
        background-color: #ff4b4b !important;
        color: white !important;
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

# Função para contar clientes (com cache)
@st.cache_data(ttl=30)
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
    if total_clientes > 0:
        st.balloons()

elif menu == "👩‍🦰 Clientes":
    st.header("👩‍🦰 Gerenciar Clientes")

    tab1, tab2 = st.tabs(["✨ Nova Cliente", "📋 Todas as Clientes"])

    with tab1:
        with st.form("cadastro_cliente", clear_on_submit=True):
            st.subheader("Cadastrar Nova Cliente")
            nome = st.text_input("Nome completo *", placeholder="Ex: Maria Silva")
            telefone = st.text_input("Telefone *", placeholder="(XX) XXXXX-XXXX")
            data_nascimento = st.date_input("Data de nascimento", value=None, min_value=date(1900,1,1))
            observacoes = st.text_area("Observações", placeholder="Ex: prefere horários à tarde, pele sensível...")

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
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error("❌ Erro ao salvar. Verifique os dados.")

    with tab2:
        st.subheader("Todas as Clientes")

        try:
            response = supabase.table("clientes").select("*").order("nome").execute()
            if response.data:
                df = pd.DataFrame(response.data)
                df_display = df[['nome', 'telefone', 'data_nascimento', 'observacoes']].copy()
                df_display.columns = ['Nome', 'Telefone', 'Data de Nascimento', 'Observações']

                # Busca
                busca = st.text_input("🔍 Buscar por nome ou telefone", key="busca_clientes")
                if busca:
                    mask = df_display.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)
                    df_display = df_display[mask]

                # Adicionar colunas de ação
                for idx, row in df_display.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 4, 1, 1])
                    with col1:
                        st.write(row['Nome'])
                    with col2:
                        st.write(row['Telefone'])
                    with col3:
                        st.write(row['Data de Nascimento'] or "-")
                    with col4:
                        st.write(row['Observações'] or "-")
                    with col5:
                        if st.button("✏️", key=f"edit_{row.name}"):
                            st.session_state.editando = df.iloc[row.name].to_dict()
                            st.rerun()
                    with col6:
                        if st.button("🗑️", key=f"delete_{row.name}", type="secondary"):
                            st.session_state.deletando_id = df.iloc[row.name]['id']
                            st.session_state.deletando_nome = row['Nome']
                            st.rerun()

                # Modal de edição
                if 'editando' in st.session_state:
                    cliente = st.session_state.editando
                    with st.form("editar_cliente"):
                        st.subheader(f"Editando: {cliente['nome']}")
                        novo_nome = st.text_input("Nome completo *", value=cliente['nome'])
                        novo_telefone = st.text_input("Telefone *", value=cliente['telefone'])
                        nova_data = cliente['data_nascimento']
                        if nova_data:
                            nova_data = date.fromisoformat(nova_data)
                        novo_nascimento = st.date_input("Data de nascimento", value=nova_data or None)
                        novas_obs = st.text_area("Observações", value=cliente['observacoes'] or "")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Atualizar"):
                                if not novo_nome.strip() or not novo_telefone.strip():
                                    st.error("Nome e telefone obrigatórios!")
                                else:
                                    try:
                                        update_data = {
                                            "nome": novo_nome.strip(),
                                            "telefone": novo_telefone.strip(),
                                            "data_nascimento": str(novo_nascimento) if novo_nascimento else None,
                                            "observacoes": novas_obs.strip() if novas_obs.strip() else None
                                        }
                                        supabase.table("clientes").update(update_data).eq("id", cliente['id']).execute()
                                        st.success("Cliente atualizada!")
                                        st.cache_data.clear()
                                        del st.session_state.editando
                                        st.rerun()
                                    except Exception as e:
                                        st.error("Erro ao atualizar.")
                        with col2:
                            if st.form_submit_button("Cancelar"):
                                del st.session_state.editando
                                st.rerun()

                # Confirmação de deleção
                if 'deletando_id' in st.session_state:
                    st.error(f"Tem certeza que deseja **deletar** a cliente **{st.session_state.deletando_nome}**?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Sim, deletar", type="secondary"):
                            try:
                                supabase.table("clientes").delete().eq("id", st.session_state.deletando_id).execute()
                                st.success("Cliente removida.")
                                st.cache_data.clear()
                                del st.session_state.deletando_id
                                del st.session_state.deletando_nome
                                st.rerun()
                            except:
                                st.error("Erro ao deletar.")
                    with col2:
                        if st.button("Cancelar"):
                            del st.session_state.deletando_id
                            del st.session_state.deletando_nome
                            st.rerun()

            else:
                st.info("Nenhuma cliente cadastrada ainda. Cadastre a primeira!")

        except Exception as e:
            st.error("Erro ao carregar clientes.")

st.markdown("---")
st.caption("© 2025 Depilação Claudia Ferraz • Sistema exclusivo e personalizado")