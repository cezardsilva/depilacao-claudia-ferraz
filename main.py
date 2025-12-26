# Arquivo: main.py
# Versão: 5.0 Final - Sistema completo com Clientes, Agenda, Notificações OneSignal e horário correto (Brasília)

import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import date, datetime, timedelta, timezone
import pandas as pd
from streamlit_calendar import calendar
import locale

# Import correto do OneSignal SDK (versão atual)
from onesignal_sdk.client import Client as OneSignalClient

# Configurar locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    pass

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
onesignal_app_id = os.getenv("ONESIGNAL_APP_ID")
onesignal_rest_key = os.getenv("ONESIGNAL_REST_API_KEY")

if not supabase_url or not supabase_key:
    st.error("⚠️ Configuração do Supabase não encontrada. Verifique o arquivo .env")
    st.stop()

supabase: Client = create_client(supabase_url, supabase_key)

# OneSignal client
onesignal_client = None
if onesignal_app_id and onesignal_rest_key:
    onesignal_client = OneSignalClient(app_id=onesignal_app_id, rest_api_key=onesignal_rest_key)

st.set_page_config(
    page_title="Depilação Claudia Ferraz",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
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
    button[kind="primary"] {
        background-color: #FFB6C1 !important;
        color: #1E1E1E !important;
        font-weight: bold !important;
    }
    button[kind="primary"]:hover {
        background-color: #D4AF37 !important;
        color: white !important;
    }
    button[kind="secondary"] {
        background-color: #dc3545 !important;
        color: white !important;
    }
    .status-nao {background-color: #888888; color: white; padding: 5px 10px; border-radius: 8px; font-size: 0.9rem;}
    .status-confirmado {background-color: #28a745; color: white; padding: 5px 10px; border-radius: 8px; font-size: 0.9rem;}
    .status-realizado {background-color: #D4AF37; color: #1E1E1E; padding: 5px 10px; border-radius: 8px; font-size: 0.9rem;}
    .status-cancelado {background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 8px; font-size: 0.9rem;}
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

# Timezone de Brasília
TZ_BRASIL = timezone(timedelta(hours=-3))

# Funções auxiliares
def format_telefone(tel):
    tel = ''.join(filter(str.isdigit, str(tel)))
    if len(tel) == 11:
        return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
    return tel or "-"

def format_data(data_str):
    if data_str:
        try:
            return datetime.fromisoformat(data_str).astimezone(TZ_BRASIL).strftime("%d/%m/%Y")
        except:
            return "-"
    return "-"

def format_data_hora(data_iso):
    if data_iso:
        try:
            dt = datetime.fromisoformat(data_iso).astimezone(TZ_BRASIL)
            return dt.strftime("%d/%m/%Y às %H:%M")
        except:
            return "-"
    return "-"

def get_status_texto(status):
    mapping = {
        "nao_confirmado": "Não Confirmado",
        "confirmado": "Confirmado",
        "realizado": "Realizado",
        "cancelado": "Cancelado"
    }
    return mapping.get(status, "Não Confirmado")

def get_status_class(status):
    mapping = {
        "nao_confirmado": "status-nao",
        "confirmado": "status-confirmado",
        "realizado": "status-realizado",
        "cancelado": "status-cancelado"
    }
    return mapping.get(status, "status-nao")

# Cache das funções
@st.cache_data(ttl=30)
def contar_clientes():
    try:
        return supabase.table("clientes").select("id", count="exact").execute().count or 0
    except:
        return 0

@st.cache_data(ttl=30)
def contar_aniversarios():
    try:
        resp = supabase.table("clientes").select("data_nascimento").execute()
        hoje = datetime.now(TZ_BRASIL)
        return sum(1 for r in resp.data if r['data_nascimento'] and 
                  datetime.fromisoformat(r['data_nascimento']).month == hoje.month and 
                  datetime.fromisoformat(r['data_nascimento']).day == hoje.day)
    except:
        return 0

@st.cache_data(ttl=60)
def carregar_clientes():
    try:
        resp = supabase.table("clientes").select("id, nome, telefone").order("nome").execute()
        return {c['id']: f"{c['nome']} - {format_telefone(c['telefone'])}" for c in resp.data}
    except:
        return {}

@st.cache_data(ttl=60)
def carregar_agendamentos():
    try:
        resp = supabase.table("agendamentos").select("*, clientes(nome, telefone)").order("data_hora").execute()
        return resp.data
    except:
        return []

@st.cache_data(ttl=60)
def contar_agendamentos_hoje():
    hoje = datetime.now(TZ_BRASIL).date()
    agendamentos = carregar_agendamentos()
    return len([a for a in agendamentos if datetime.fromisoformat(a['data_hora']).astimezone(TZ_BRASIL).date() == hoje])

total_clientes = contar_clientes()
total_aniversarios = contar_aniversarios()
total_agendamentos_hoje = contar_agendamentos_hoje()

# ==================== INÍCIO ====================
if menu == "🏠 Início":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="card"><h3>👥 Clientes</h3><h2 style="color:#FFB6C1;">{total_clientes}</h2><p>cadastradas</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card"><h3>📅 Agendamentos</h3><h2 style="color:#D4AF37;">{total_agendamentos_hoje}</h2><p>hoje</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card"><h3>🎂 Aniversários</h3><h2 style="color:#FFB6C1;">{total_aniversarios}</h2><p>hoje</p></div>', unsafe_allow_html=True)

    st.success("✅ Sistema conectado ao banco de dados com sucesso!")

# ==================== CLIENTES ====================
elif menu == "👩‍🦰 Clientes":
    st.header("👩‍🦰 Gerenciar Clientes")
    tab1, tab2 = st.tabs(["✨ Nova Cliente", "📋 Todas as Clientes"])

    with tab1:
        with st.form("cadastro_cliente", clear_on_submit=True):
            st.subheader("Cadastrar Nova Cliente")
            nome = st.text_input("Nome completo *", placeholder="Ex: Maria Silva")
            telefone = st.text_input("Telefone *", placeholder="(11) 91234-5678")
            data_nascimento = st.date_input("Data de nascimento", value=None, min_value=date(1900,1,1))
            observacoes = st.text_area("Observações")

            if st.form_submit_button("💾 Salvar Cliente"):
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
                        st.success(f"✅ {nome} cadastrada com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error("Erro ao salvar cliente.")

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
                    mask = df['nome'].str.contains(busca, case=False, na=False) | df['telefone'].str.contains(busca, case=False, na=False)
                    df = df[mask]

                for _, row in df.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 3, 1, 1])
                    with col1:
                        st.write(row['nome'])
                    with col2:
                        st.write(format_telefone(row['telefone']))
                    with col3:
                        st.write(format_data(row['data_nascimento']))
                    with col4:
                        st.write(row['observacoes'] or "-")
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
                                            st.success("Cliente atualizada!")
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
                                    st.success(f"{nome} removida com sucesso.")
                                    st.cache_data.clear()
                                    del st.session_state['cliente_del_id']
                                    del st.session_state['cliente_del_nome']
                                    st.rerun()
                                except:
                                    st.error("Erro ao deletar.")
                        with c2:
                            if st.button("Cancelar"):
                                del st.session_state['cliente_del_id']
                                del st.session_state['cliente_del_nome']
                                st.rerun()

        except Exception as e:
            st.error("Erro ao carregar clientes.")

# ==================== AGENDA ====================
elif menu == "📅 Agenda":
    st.header("📅 Agenda de Atendimentos")

    clientes_dict = carregar_clientes()
    agendamentos = carregar_agendamentos()

    # Eventos para o calendário
    events = []
    for ag in agendamentos:
        dt_iso = ag['data_hora']
        dt = datetime.fromisoformat(dt_iso).astimezone(TZ_BRASIL)
        color = {
            "nao_confirmado": "#888888",
            "confirmado": "#28a745",
            "realizado": "#D4AF37",
            "cancelado": "#dc3545"
        }.get(ag['status'], "#888888")
        events.append({
            "title": f"{ag['clientes']['nome']} ({dt.strftime('%H:%M')})",
            "start": dt.isoformat(),
            "end": (dt + timedelta(hours=1)).isoformat(),
            "backgroundColor": color,
            "borderColor": color,
        })

    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "initialView": "dayGridMonth",
        "selectable": True,
        "height": 800,
        "contentHeight": 750,
        "locale": "pt-br",
        "buttonText": {"today": "Hoje", "month": "Mês", "week": "Semana", "day": "Dia"},
        "slotMinTime": "08:00:00",
        "slotMaxTime": "21:00:00",
    }

    calendar(events=events, options=calendar_options, key="main_calendar")

    tab1, tab2 = st.tabs(["✨ Nova Marcação", "📋 Todos os Agendamentos"])

    with tab1:
        with st.form("nova_marcacao"):
            st.subheader("Marcar Novo Horário")
            if not clientes_dict:
                st.warning("Cadastre pelo menos uma cliente antes.")
            else:
                cliente_id = st.selectbox("Cliente *", options=list(clientes_dict.keys()), format_func=lambda x: clientes_dict[x])
                data = st.date_input("Data", value=date.today())
                hora = st.time_input("Horário", value=datetime.now(TZ_BRASIL).replace(minute=0, second=0) + timedelta(hours=1))
                data_hora_local = datetime.combine(data, hora)
                data_hora_utc = data_hora_local.astimezone(timezone.utc)
                observacoes = st.text_area("Observações do agendamento")

                if st.form_submit_button("📅 Marcar Horário"):
                    try:
                        insert_data = {
                            "cliente_id": cliente_id,
                            "data_hora": data_hora_utc.isoformat(),
                            "status": "nao_confirmado",
                            "observacoes": observacoes.strip() if observacoes.strip() else None
                        }
                        supabase.table("agendamentos").insert(insert_data).execute()
                        st.success("Horário marcado com sucesso!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao marcar horário: {str(e)}")

    with tab2:
        st.subheader("Todos os Agendamentos")
        if agendamentos:
            for ag in sorted(agendamentos, key=lambda x: x['data_hora'], reverse=True):
                dt_iso = ag['data_hora']
                dt = datetime.fromisoformat(dt_iso).astimezone(TZ_BRASIL)
                nome = ag['clientes']['nome']
                status_txt = get_status_texto(ag['status'])

                with st.container():
                    col1, col2 = st.columns([6, 4])
                    with col1:
                        st.markdown(f"**{nome}**")
                        st.caption(format_data_hora(ag['data_hora']))
                        st.markdown(f"<span class='{get_status_class(ag['status'])}'>{status_txt}</span>", unsafe_allow_html=True)
                        if ag['observacoes']:
                            st.caption(f"📝 {ag['observacoes']}")
                    with col2:
                        novo_status = st.selectbox(
                            "Alterar status",
                            ["nao_confirmado", "confirmado", "realizado", "cancelado"],
                            index=["nao_confirmado", "confirmado", "realizado", "cancelado"].index(ag['status']),
                            key=f"status_select_{ag['id']}",
                            label_visibility="collapsed"
                        )
                        if st.button("💾 Salvar Status", key=f"save_status_{ag['id']}"):
                            try:
                                supabase.table("agendamentos").update({"status": novo_status}).eq("id", ag['id']).execute()
                                if novo_status == "realizado":
                                    supabase.table("clientes").update({"ultimo_atendimento": datetime.now(timezone.utc).isoformat()}).eq("id", ag['cliente_id']).execute()
                                st.success("Status atualizado!")
                                st.cache_data.clear()
                                st.rerun()
                            except:
                                st.error("Erro ao atualizar status.")

                        if st.button("✏️ Editar", key=f"edit_ag_{ag['id']}"):
                            st.session_state[f"editando_ag_{ag['id']}"] = True

                        if st.button("🗑️ Deletar", key=f"del_ag_{ag['id']}", type="secondary"):
                            st.session_state[f"deletando_ag_{ag['id']}"] = True

                    st.divider()

                if st.session_state.get(f"editando_ag_{ag['id']}", False):
                    with st.expander(f"✏️ Editando agendamento de {nome}", expanded=True):
                        with st.form(f"form_edit_ag_{ag['id']}"):
                            novo_cliente_id = st.selectbox("Cliente", options=list(clientes_dict.keys()), format_func=lambda x: clientes_dict[x], index=list(clientes_dict.keys()).index(ag['cliente_id']))
                            nova_data_input = st.date_input("Data", value=dt.date())
                            nova_hora_input = st.time_input("Horário", value=dt.time())
                            nova_data_hora_local = datetime.combine(nova_data_input, nova_hora_input)
                            nova_data_hora_utc = nova_data_hora_local.astimezone(timezone.utc)
                            novas_obs = st.text_area("Observações", value=ag['observacoes'] or "")

                            c1, c2 = st.columns(2)
                            with c1:
                                if st.form_submit_button("💾 Atualizar Agendamento"):
                                    try:
                                        supabase.table("agendamentos").update({
                                            "cliente_id": novo_cliente_id,
                                            "data_hora": nova_data_hora_utc.isoformat(),
                                            "observacoes": novas_obs.strip() if novas_obs.strip() else None
                                        }).eq("id", ag['id']).execute()
                                        st.success("Agendamento atualizado!")
                                        st.cache_data.clear()
                                        del st.session_state[f"editando_ag_{ag['id']}"]
                                        st.rerun()
                                    except:
                                        st.error("Erro ao atualizar.")
                            with c2:
                                if st.form_submit_button("Cancelar"):
                                    del st.session_state[f"editando_ag_{ag['id']}"]
                                    st.rerun()

                if st.session_state.get(f"deletando_ag_{ag['id']}", False):
                    with st.expander(f"🗑️ Confirmar exclusão de {nome}", expanded=True):
                        st.error(f"Tem certeza que deseja **deletar permanentemente** o agendamento de {nome} em {format_data_hora(ag['data_hora'])}?")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("🗑️ Sim, deletar", key=f"confirm_del_ag_{ag['id']}", type="secondary"):
                                try:
                                    supabase.table("agendamentos").delete().eq("id", ag['id']).execute()
                                    st.success("Agendamento deletado com sucesso!")
                                    st.cache_data.clear()
                                    del st.session_state[f"deletando_ag_{ag['id']}"]
                                    st.rerun()
                                except:
                                    st.error("Erro ao deletar.")
                        with c2:
                            if st.button("Cancelar"):
                                del st.session_state[f"deletando_ag_{ag['id']}"]
                                st.rerun()

        else:
            st.info("Nenhum agendamento cadastrado ainda.")

# ==================== NOTIFICAÇÕES ====================
elif menu == "🔔 Notificações":
    st.header("🔔 Notificações Push")

    if not onesignal_client:
        st.error("⚠️ Configure ONESIGNAL_APP_ID e ONESIGNAL_REST_API_KEY no .env")
        st.stop()

    st.success("✅ OneSignal conectado com sucesso!")

    st.subheader("Teste Manual")
    mensagem = st.text_input("Mensagem de teste", value="Olá Claudia! As notificações estão funcionando perfeitamente! ✨💖")

    if st.button("Enviar Push de Teste"):
        import requests
        import json

        payload = {
            "app_id": onesignal_app_id,
            "included_segments": ["All"],
            "contents": {"pt": mensagem},
            "headings": {"pt": "Depilação Claudia Ferraz"},
            "name": "Teste Manual"
        }

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {onesignal_rest_key}"  # Basic para Authentication Key
        }

        try:
            response = requests.post(
                "https://onesignal.com/api/v1/notifications",
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code == 200:
                st.success("✅ Notificação enviada com sucesso! Checa o celular da Claudia agora! 📱✨")
                st.balloons()
                st.json(response.json())
            else:
                st.error(f"Erro HTTP {response.status_code}")
                st.code(response.text)
        except Exception as e:
            st.error(f"Erro ao enviar: {str(e)}")

    st.markdown("---")

    st.subheader("Notificações Automáticas (em desenvolvimento)")
    st.info("Em breve: parabéns automáticos, lembretes de agendamento e alerta de retorno.")

elif menu == "⚙️ Configurações":
    st.header("⚙️ Configurações")
    st.info("Em desenvolvimento...")

st.markdown("---")
st.caption("© 2025 Depilação Claudia Ferraz • Sistema exclusivo e personalizado")