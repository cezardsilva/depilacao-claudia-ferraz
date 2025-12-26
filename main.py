# Arquivo: main.py
# Versão: 3.3 - Refinamentos: formatação telefone/data, contagem aniversários

import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import date, datetime
import pandas as pd

# Carregar variáveis
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    st.error("⚠️ Configuração do Supabase não encontrada.")
    st.stop()

supabase: Client = create_client(supabase_url, supabase_key)

st.set_page_config(page_title="Depilação Claudia Ferraz", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# CSS
st.markdown("""
    <style>
    .main-header {font-size: 3.5rem; font-weight: 700; text-align: center;
                  background: linear-gradient(90deg, #D4AF37, #FFB6C1);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .sub-header {font-size: 1.8rem; text-align: center; color: #FFB6C1;}
    .card {background-color: #2D2D2D; padding: 2rem; border-radius: 15px;
           box-shadow: 0 4px 15px rgba(255, 182, 193, 0.2); text-align: center;}
    button[kind="primary"] {background-color: #FFB6C1 !important; color: #1E1E1E !important;}
    button[kind="primary"]:hover {background-color: #D4AF37 !important; color: white !important;}
    button[kind="secondary"] {background-color: #ff4b4b !important; color: white !important;}
    </style>
    """, unsafe_allow_html=True)

# Header e Sidebar
st.markdown('<h1 class="main-header">✨ Depilação Claudia Ferraz ✨</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Agenda de Clientes & Agendamentos</h2>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Navegação")
    menu = st.radio("Escolha uma opção",
        ["🏠 Início", "👩‍🦰 Clientes", "📅 Agenda", "🔔 Notificações", "⚙️ Configurações"],
        label_visibility="collapsed")
    st.markdown("---")
    st.caption("💖 Feito com carinho para a Claudia")

# Funções auxiliares
def format_telefone(tel):
    tel = ''.join(filter(str.isdigit, tel))  # Remove não-dígitos
    if len(tel) == 11:
        return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
    return tel

def format_data(data_str):
    if data_str:
        try:
            d = datetime.fromisoformat(data_str)
            return d.strftime("%d/%m/%Y")
        except:
            return data_str
    return "-"

# Contar clientes
@st.cache_data(ttl=30)
def contar_clientes():
    try:
        return supabase.table("clientes").select("id", count="exact").execute().count or 0
    except:
        return 0

# Contar aniversários no mês atual
@st.cache_data(ttl=30)
def contar_aniversarios():
    try:
        response = supabase.table("clientes").select("data_nascimento").execute()
        mes_atual = datetime.now().month
        cont = 0
        for r in response.data:
            if r['data_nascimento']:
                d = datetime.fromisoformat(r['data_nascimento'])
                if d.month == mes_atual:
                    cont += 1
        return cont
    except:
        return 0

total_clientes = contar_clientes()
total_aniversarios = contar_aniversarios()

if menu == "🏠 Início":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="card"><h3>👥 Clientes</h3><h2 style="color:#FFB6C1;">{total_clientes}</h2><p>cadastradas</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h3>📅 Agendamentos</h3><h2 style="color:#D4AF37;">0</h2><p>hoje</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card"><h3>🎂 Aniversários</h3><h2 style="color:#FFB6C1;">{total_aniversarios}</h2><p>neste mês</p></div>', unsafe_allow_html=True)
    st.success("✅ Sistema conectado com sucesso!")
    if total_clientes > 0:
        st.balloons()

elif menu == "👩‍🦰 Clientes":
    st.header("👩‍🦰 Gerenciar Clientes")
    tab1, tab2 = st.tabs(["✨ Nova Cliente", "📋 Todas as Clientes"])

    with tab1:
        with st.form("cadastro_cliente", clear_on_submit=True):
            st.subheader("Cadastrar Nova Cliente")
            nome = st.text_input("Nome completo *", placeholder="Ex: Maria Silva")
            telefone = st.text_input("Telefone *", placeholder="(11) 91234-5678")
            data_nascimento = st.date_input("Data de nascimento", value=None, min_value=date(1900,1,1))
            observacoes = st.text_area("Observações", placeholder="Ex: prefere horários à tarde...")

            if st.form_submit_button("💾 Salvar Cliente"):
                if not nome.strip() or not telefone.strip():
                    st.error("⚠️ Nome e telefone obrigatórios!")
                else:
                    try:
                        data = {
                            "nome": nome.strip(),
                            "telefone": telefone.strip(),
                            "data_nascimento": str(data_nascimento) if data_nascimento else None,
                            "observacoes": observacoes.strip() if observacoes.strip() else None
                        }
                        supabase.table("clientes").insert(data).execute()
                        st.success(f"✅ {nome} cadastrada!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error("Erro ao salvar.")

    with tab2:
        st.subheader("Todas as Clientes")

        try:
            response = supabase.table("clientes").select("*").order("nome").execute()
            if not response.data:
                st.info("Nenhuma cliente cadastrada ainda.")
            else:
                df = pd.DataFrame(response.data)

                busca = st.text_input("🔍 Buscar por nome ou telefone")
                if busca:
                    mask = df['nome'].str.contains(busca, case=False) | df['telefone'].str.contains(busca, case=False)
                    df = df[mask]

                for _, row in df.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 3, 1, 1])
                    with col1: st.write(row['nome'])
                    with col2: st.write(format_telefone(row['telefone']))
                    with col3: st.write(format_data(row['data_nascimento']))
                    with col4: st.write(row['observacoes'] or "-")
                    with col5:
                        if st.button("✏️", key=f"edit_{row['id']}"):
                            st.session_state['cliente_edit'] = row.to_dict()
                    with col6:
                        if st.button("🗑️", key=f"del_{row['id']}", type="secondary"):
                            st.session_state['cliente_del_id'] = row['id']
                            st.session_state['cliente_del_nome'] = row['nome']

                if 'cliente_edit' in st.session_state:
                    cliente = st.session_state['cliente_edit']
                    with st.expander(f"✏️ Editando: {cliente['nome']}", expanded=True):
                        with st.form("form_edit"):
                            novo_nome = st.text_input("Nome *", value=cliente['nome'])
                            novo_tel = st.text_input("Telefone *", value=cliente['telefone'], placeholder="(11) 91234-5678")
                            nova_data = date.fromisoformat(cliente['data_nascimento']) if cliente['data_nascimento'] else None
                            novo_nasc = st.date_input("Data de nascimento", value=nova_data)
                            novas_obs = st.text_area("Observações", value=cliente['observacoes'] or "")

                            c1, c2 = st.columns(2)
                            with c1:
                                if st.form_submit_button("💾 Atualizar"):
                                    if not novo_nome.strip() or not novo_tel.strip():
                                        st.error("Campos obrigatórios!")
                                    else:
                                        try:
                                            supabase.table("clientes").update({
                                                "nome": novo_nome.strip(),
                                                "telefone": novo_tel.strip(),
                                                "data_nascimento": str(novo_nasc) if novo_nasc else None,
                                                "observacoes": novas_obs.strip() if novas_obs.strip() else None
                                            }).eq("id", cliente['id']).execute()
                                            st.success("Atualizado!")
                                            st.cache_data.clear()
                                            del st.session_state['cliente_edit']
                                            st.rerun()
                                        except:
                                            st.error("Erro ao atualizar.")
                            with c2:
                                if st.form_submit_button("Cancelar"):
                                    del st.session_state['cliente_edit']
                                    st.rerun()

                if 'cliente_del_id' in st.session_state:
                    nome = st.session_state['cliente_del_nome']
                    with st.expander("🗑️ Confirmação de Exclusão", expanded=True):
                        st.error(f"Tem certeza que deseja deletar **{nome}**?")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("🗑️ Sim, deletar", type="secondary"):
                                try:
                                    supabase.table("clientes").delete().eq("id", st.session_state['cliente_del_id']).execute()
                                    st.success(f"{nome} removida.")
                                    st.cache_data.clear()
                                    del st.session_state['cliente_del_id']
                                    del st.session_state['cliente_del_nome']
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao deletar: {str(e)}")  # Log para debug
                        with c2:
                            if st.button("Cancelar"):
                                del st.session_state['cliente_del_id']
                                del st.session_state['cliente_del_nome']
                                st.rerun()

        except Exception as e:
            st.error("Erro ao carregar dados.")

st.markdown("---")
st.caption("© 2025 Depilação Claudia Ferraz • Sistema exclusivo e personalizado")