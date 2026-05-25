"""
app.py — Interface JARVIS Acadêmico
Frontend Streamlit para o assistente com RAG + Tool Calling.

Estrutura do projeto esperada:
    jarvis/
    ├── app.py              <- este arquivo
    ├── .env                <- API_KEY=...
    ├── memory/
    │   ├── agenda.json
    │   └── tarefas.json
    ├── logs/
    ├── rag/pipeline.py
    └── tools/
        ├── agenda.py       -> consulte_agenda, consulte_semana
        ├── tarefas.py      -> liste_tarefas, adicione_tarefas, conclua_tarefa
        ├── estudos.py      -> busque_material_rag
        ├── logger.py       -> registre_log
        └── definitions.py  -> DADOS_DAS_FERRAMENTAS
"""

# ─────────────────────────────────────────────────────────────
# SEÇÃO 1 — CONFIGURAÇÃO INICIAL E CACHE
# ─────────────────────────────────────────────────────────────

import json
import os
import logging
from datetime import datetime, date

import streamlit as st
import pandas as pd  # MOVIDO PARA O TOPO: Evita NameError na Sidebar
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Academic JARVIS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Data calculada uma única vez por rerun
HOJE_STR  = datetime.now().strftime("%A, %d de %B de %Y — %H:%M")
HOJE_DATE = datetime.now().date()


@st.cache_resource
def carregue_rag():
    """
    Carrega PipelineRAG uma única vez por sessão do servidor.
    Forçamos o uso da CPU aqui para evitar concorrência de C-Level com as threads do Streamlit.
    """
    from rag.pipeline import PipelineRAG  # type: ignore
    return PipelineRAG(device="cpu")


def obtenha_rag():
    """Ponto único de acesso ao RAG."""
    chave = os.getenv("API_KEY", "")
    if not chave:
        st.error(
            "⚠️ **Chave de API não encontrada.**\n\n"
            "Crie um arquivo `.env` na raiz do projeto com `API_KEY=sua_chave`."
        )
        st.stop()
    try:
        return carregue_rag()
    except Exception as exc:
        st.error(f"❌ **Falha ao inicializar o RAG:** {exc}")
        st.stop()


# ─────────────────────────────────────────────────────────────
# SEÇÃO 2 — SESSION STATE
# ─────────────────────────────────────────────────────────────

def _system_prompt() -> str:
    """Gera o prompt de sistema com data e ferramentas (idêntico ao main.py)."""
    from tools.definitions import DADOS_DAS_FERRAMENTAS  # type: ignore
    hoje = datetime.now().strftime("%A, %d de %B de %Y")
    tools_json = json.dumps(DADOS_DAS_FERRAMENTAS, indent=2, ensure_ascii=False)
    return (
        f"Você é o Academic JARVIS, um assistente inteligente acadêmico. Hoje é {hoje}\n"
        "Você tem acesso a ferramentas locais para gerenciar a agenda, tarefas e buscar "
        "materiais de estudo (RAG).\n\n"
        f"FERRAMENTAS DISPONÍVEIS:\n{tools_json}\n\n"
        "REGRA CRÍTICA: Se a pergunta do usuário exigir o uso de uma ferramenta, você DEVE "
        "responder EXCLUSIVAMENTE com um JSON estruturado seguindo o formato exato das "
        "ferramentas disponíveis.\n"
        'Exemplo: {"nome_ferramenta": "liste_tarefas", "argumentos": {"status": "pendente"}}\n'
        "NAO use marcacoes markdown (como ```json). Responda apenas com o JSON puro."
    )


def _inicialize_state():
    if "historico" not in st.session_state:
        st.session_state.historico = [{"role": "system", "content": _system_prompt()}]

    if "mensagens_tela" not in st.session_state:
        st.session_state.mensagens_tela = []

    if "logs_ferramentas" not in st.session_state:
        st.session_state.logs_ferramentas = []

    if "ultima_fontes_rag" not in st.session_state:
        st.session_state.ultima_fontes_rag = []


_inicialize_state()


# ─────────────────────────────────────────────────────────────
# SEÇÃO 5 — FUNÇÃO CENTRAL DE RESPOSTA
# ─────────────────────────────────────────────────────────────

def _mapeador() -> dict:
    from tools.agenda  import consulte_agenda, consulte_semana, adicione_agenda            # type: ignore
    from tools.tarefas import liste_tarefas, adicione_tarefas, conclua_tarefa  # type: ignore
    from tools.estudos import busque_material_rag                          # type: ignore
    return {
        "consulte_agenda":     consulte_agenda,
        "consulte_semana":     consulte_semana,
        "adicione_agenda":     adicione_agenda,
        "liste_tarefas":       liste_tarefas,
        "adicione_tarefas":    adicione_tarefas,
        "conclua_tarefa":      conclua_tarefa,
        "busque_material_rag": busque_material_rag
    }


def _execute_tool(nome: str, args: dict) -> tuple:
    fontes_rag = []
    mapa = _mapeador()

    if nome not in mapa:
        return f"[Ferramenta desconhecida: {nome}]", fontes_rag

    try:
        resultado = mapa[nome](**args)
    except Exception as exc:
        logging.exception(f"Erro ao executar {nome}")
        return f"[Erro ao executar {nome}: {exc}]", fontes_rag

    if nome == "busque_material_rag" and isinstance(resultado, list):
        fontes_rag = resultado
        return json.dumps(resultado, ensure_ascii=False), fontes_rag

    return json.dumps(resultado, ensure_ascii=False, default=str), fontes_rag


def _registre_log(nome: str, args: dict, resultado: str):
    try:
        from tools.logger import registre_log  # type: ignore
        registre_log(nome, args, resultado)
    except Exception:
        pass

    entrada = {
        "nome":    nome,
        "horario": datetime.now().strftime("%H:%M:%S"),
        "input":   args,
        "output":  resultado[:400] + ("…" if len(resultado) > 400 else ""),
    }
    st.session_state.logs_ferramentas.insert(0, entrada)
    if len(st.session_state.logs_ferramentas) > 10:
        st.session_state.logs_ferramentas = st.session_state.logs_ferramentas[:10]


def _chame_llm(mensagens: list) -> str:
    import os
    import openai
    from openai import OpenAI 

    try:
        client = OpenAI(
            base_url="https://llm.liaufms.org/v1/gemma-3-12b-it",
            api_key=os.getenv("API_KEY", ""),
        )

        resposta = client.chat.completions.create(
            model="google/gemma-3-12b-it",
            messages=mensagens,
        )

        return resposta.choices[0].message.content or "O Jarvis não retornou nenhuma resposta."
    
    except (openai.APIConnectionError, openai.APIStatusError) as e:
        return f"Erro crítico na chamada da LLM: Erro de conexão com o servidor da UFMS ({e})."
    except Exception as e:
        return f"Erro crítico na chamada da LLM: {e}"
    
def processe_mensagem(user_message: str) -> tuple:
    MAX_ITER = 3
    fontes_acumuladas = []

    if st.session_state.historico[-1]["content"] != user_message:
        st.session_state.historico.append({"role": "user", "content": user_message})

    for i in range(MAX_ITER):
        try:
            resposta_bruta = _chame_llm(st.session_state.historico)
            if not resposta_bruta:
                raise ValueError("A API retornou uma resposta vazia.")
        except Exception as exc:
            msg_erro = f"Erro crítico na chamada da LLM: {exc}"
            return msg_erro, fontes_acumuladas

        tool_call = None
        try:
            texto_limpo = resposta_bruta.replace("```json", "").replace("```", "").strip()
            dados = json.loads(texto_limpo)
            if isinstance(dados, dict) and "nome_ferramenta" in dados:
                tool_call = dados
        except (json.JSONDecodeError, TypeError):
            pass 

        if tool_call is None:
            st.session_state.historico.append({"role": "assistant", "content": resposta_bruta})
            return resposta_bruta, fontes_acumuladas

        nome = tool_call.get("nome_ferramenta", "desconhecida")
        args = tool_call.get("argumentos", {})

        if len(st.session_state.historico) > 10:
            ultimas_msgs = [m["content"] for m in st.session_state.historico[-4:]]
            if any(nome in str(m) for m in ultimas_msgs) and i > 1:
                return "Interrompido: O assistente entrou em loop chamando a mesma ferramenta repetidamente.", fontes_acumuladas

        resultado_str, fontes_rag = _execute_tool(nome, args)
        fontes_acumuladas.extend(fontes_rag)
        _registre_log(nome, args, resultado_str)

        st.session_state.historico.append({"role": "assistant", "content": resposta_bruta})
        st.session_state.historico.append({
            "role": "user",
            "content": f"Resultado da ferramenta {nome}: {resultado_str}.",
        })

    msg_final = "Não foi possível consolidar uma resposta textual dentro do limite de interações."
    return msg_final, fontes_acumuladas


# ─────────────────────────────────────────────────────────────
# HELPERS — DADOS PARA O DASHBOARD (Caches de 30s)
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def _carregue_tarefas_pendentes() -> list:
    try:
        from tools.tarefas import liste_tarefas  # type: ignore
        return liste_tarefas("pendente")
    except Exception:
        return []


@st.cache_data(ttl=30)
def _carregue_tarefas_concluidas() -> list:
    try:
        from tools.tarefas import liste_tarefas  # type: ignore
        return liste_tarefas("concluida")
    except Exception:
        return []


@st.cache_data(ttl=30)
def _carregue_eventos_semana() -> list:
    try:
        from tools.agenda import consulte_semana  # type: ignore
        return consulte_semana()
    except Exception:
        return []


def _calcule_metricas(pendentes: list, concluidas: list) -> dict:
    vencendo = 0
    for t in pendentes:
        try:
            prazo = date.fromisoformat(t["prazo"])
            if 0 <= (prazo - HOJE_DATE).days <= 2:
                vencendo += 1
        except (KeyError, ValueError):
            pass
    return {
        "concluidas":         len(concluidas),
        "pendentes":          len(pendentes),
        "total":              len(pendentes) + len(concluidas),
        "vencendo_em_2_dias": vencendo,
    }


def _tarefas_urgentes(pendentes: list) -> list:
    urgentes = []
    for t in pendentes:
        try:
            prazo = date.fromisoformat(t["prazo"])
            if 0 <= (prazo - HOJE_DATE).days <= 2:
                urgentes.append(t["descricao"])
        except (KeyError, ValueError):
            pass
    return urgentes


# ─────────────────────────────────────────────────────────────
# CSS PERSONALIZADO
# ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer     {visibility: hidden;}

.sidebar-label {
    font-size: 0.70rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #6B7280;
    margin: 1rem 0 0.3rem 0;
}

.tool-badge {
    display: inline-block;
    background: #0F2942;
    color: #60A5FA;
    border: 1px solid #1E40AF;
    border-radius: 4px;
    padding: 2px 10px;
    font-size: 0.78rem;
    font-family: monospace;
    margin: 3px 2px;
}

.rag-card {
    background: #0F172A;
    border-left: 3px solid #3B82F6;
    border-radius: 6px;
    padding: 8px 14px;
    margin: 6px 0;
    font-size: 0.83rem;
    color: #94A3B8;
    line-height: 1.5;
}
.rag-card b { color: #60A5FA; }

.status-on  { color: #22C55E; font-weight: 700; }
.status-off { color: #EF4444; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SEÇÃO 3 — SIDEBAR
# ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🤖 Academic JARVIS")
    st.caption("Assistente acadêmico · RAG + Tools")

    # ── Bloco A: Status do Sistema ────────────────────────────
    st.markdown('<p class="sidebar-label">⚙️ Status do Sistema</p>', unsafe_allow_html=True)
    st.caption(f"🕐 {HOJE_STR}")

    if os.getenv("API_KEY", ""):
        st.markdown('<span class="status-on">● API conectada</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-off">● API KEY ausente</span>', unsafe_allow_html=True)

    try:
        # Só inicializa o RAG quando o Streamlit estiver pronto
        n_docs = obtenha_rag().collection.count()
        st.caption(f"📄 {n_docs} fragmentos indexados no RAG")
    except Exception:
        st.caption("📄 RAG: contagem indisponível")

    st.divider()

    # ── Bloco B: Logs ao Vivo ─────────────────────────────────
    st.markdown('<p class="sidebar-label">📋 Logs de Ferramentas</p>', unsafe_allow_html=True)

    if not st.session_state.logs_ferramentas:
        st.caption("Nenhuma ferramenta chamada ainda.")
    else:
        for log in st.session_state.logs_ferramentas:
            with st.expander(f"⚙️ `{log['nome']}` — {log['horario']}"):
                st.caption("**Input:**")
                st.json(log["input"])
                st.caption("**Output:**")
                st.code(log["output"], language=None)

    st.divider()

    # ── Bloco C: Agenda Compacta na Sidebar ────────────────────
    st.markdown('<p class="sidebar-label">📅 Próximos Compromissos</p>', unsafe_allow_html=True)
    
    # CORREÇÃO: Puxa os dados da agenda que antes causavam NameError
    eventos_sidebar = _carregue_eventos_semana()

    if eventos_sidebar:
        df_ev_side = pd.DataFrame(eventos_sidebar)
        
        for col in ["data", "hora", "disciplina", "tipo"]:
            if col not in df_ev_side.columns:
                df_ev_side[col] = ""

        df_ev_side = df_ev_side[["data", "hora", "disciplina", "tipo"]].sort_values("data", ignore_index=True)
        df_ev_side.insert(
            0, "📌",
            df_ev_side["tipo"].apply(lambda t: "🔴" if str(t).lower() == "prova" else "🟢")
        )

        st.dataframe(
            df_ev_side,
            hide_index=True,
            column_config={
                "📌":          st.column_config.TextColumn("", width="small"),
                "data":        st.column_config.DateColumn("Data", format="DD/MM"),
                "hora":        st.column_config.TextColumn("Hora", width="small"),
                "disciplina":  st.column_config.TextColumn("Matéria"),
                "tipo":        None,
            },
        )
    else:
        st.caption("Nenhum compromisso esta semana.")


# ─────────────────────────────────────────────────────────────
# SEÇÃO 4 — ÁREA PRINCIPAL COM TABS
# ─────────────────────────────────────────────────────────────

tab_chat, tab_dashboard = st.tabs(["💬 Chat", "📊 Dashboard"])


# ════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ════════════════════════════════════════════════════════════

with tab_chat:

    pendentes_cache = _carregue_tarefas_pendentes()

    if not st.session_state.mensagens_tela:
        urgentes = _tarefas_urgentes(pendentes_cache)
        if urgentes:
            itens_md = "\n".join(f"• **{t}**" for t in urgentes)
            st.warning(f"⏰ **Prazos próximos (≤ 2 dias):**\n\n{itens_md}", icon="🚨")

    for msg in st.session_state.mensagens_tela:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            fontes = msg.get("fontes_rag", [])
            if fontes:
                with st.expander("📚 Fontes consultadas pelo RAG"):
                    for trecho in fontes:
                        partes   = trecho.split("\n", 1)
                        origem   = partes[0] if len(partes) > 1 else "Fonte"
                        conteudo = partes[1] if len(partes) > 1 else trecho
                        st.markdown(
                            f'<div class="rag-card"><b>{origem}</b><br>{conteudo}</div>',
                            unsafe_allow_html=True,
                        )

    if user_message := st.chat_input("Fale com o JARVIS…"):

        st.session_state.mensagens_tela.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)

        with st.chat_message("assistant"):
            badge_slot    = st.empty()
            resposta_slot = st.empty()

            with st.spinner("JARVIS pensando…"):
                resposta_final, fontes_rag = processe_mensagem(user_message)

            agora = datetime.now()
            badges_html = ""
            for log in st.session_state.logs_ferramentas[:5]:
                try:
                    log_dt = datetime.strptime(
                        f"{agora.strftime('%Y-%m-%d')} {log['horario']}",
                        "%Y-%m-%d %H:%M:%S",
                    )
                    if (agora - log_dt).seconds <= 60:
                        badges_html += f'<span class="tool-badge">⚙️ {log["nome"]}</span> '
                except Exception:
                    pass
            if badges_html:
                badge_slot.markdown(badges_html, unsafe_allow_html=True)

            resposta_slot.markdown(resposta_final)

            if fontes_rag:
                st.session_state.ultima_fontes_rag = fontes_rag
                with st.expander("📚 Fontes consultadas pelo RAG"):
                    for trecho in fontes_rag:
                        partes   = trecho.split("\n", 1)
                        origem   = partes[0] if len(partes) > 1 else "Fonte"
                        conteudo = partes[1] if len(partes) > 1 else trecho
                        st.markdown(
                            f'<div class="rag-card"><b>{origem}</b><br>{conteudo}</div>',
                            unsafe_allow_html=True,
                        )

        st.session_state.mensagens_tela.append({
            "role":       "assistant",
            "content":    resposta_final,
            "fontes_rag": fontes_rag,
        })

        _carregue_tarefas_pendentes.clear()
        _carregue_tarefas_concluidas.clear()
        _carregue_eventos_semana.clear()


# ════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ════════════════════════════════════════════════════════════

with tab_dashboard:

    pendentes  = _carregue_tarefas_pendentes()
    concluidas = _carregue_tarefas_concluidas()
    eventos    = _carregue_eventos_semana()
    metricas   = _calcule_metricas(pendentes, concluidas)

    st.subheader("📊 Visão Geral Acadêmica")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("✅ Concluídas", metricas["concluidas"])

    with col2:
        st.metric("⏳ Pendentes", metricas["pendentes"])

    with col3:
        vencendo = metricas["vencendo_em_2_dias"]
        st.metric(
            "🚨 Vencendo em 2 dias",
            vencendo,
            delta=int(vencendo) if vencendo > 0 else None,
            delta_color="inverse",
        )

    st.divider()

    total  = metricas["total"]
    n_conc = metricas["concluidas"]
    prog   = n_conc / total if total > 0 else 0.0

    st.markdown("**📈 Progresso Geral das Tarefas**")
    st.progress(prog, text=f"{n_conc} de {total} tarefas concluídas — {int(prog * 100)}%")

    st.divider()

    st.markdown("**📅 Agenda da Semana**")

    if eventos:
        df_ev = pd.DataFrame(eventos)
        for col in ["data", "hora", "disciplina", "tipo"]:
            if col not in df_ev.columns:
                df_ev[col] = ""

        df_ev = df_ev[["data", "hora", "disciplina", "tipo"]].sort_values("data", ignore_index=True)
        df_ev.insert(
            0, "📌",
            df_ev["tipo"].apply(lambda t: "🔴 PROVA" if str(t).lower() == "prova" else "🟢 Aula")
        )

        st.dataframe(
            df_ev,
            hide_index=True,
            column_config={
                "📌":          st.column_config.TextColumn("Tipo",        width="small"),
                "data":        st.column_config.DateColumn("Data",        format="DD/MM/YYYY"),
                "hora":        st.column_config.TextColumn("Hora",        width="small"),
                "disciplina":  st.column_config.TextColumn("Disciplina"),
                "tipo":        None,
            },
        )
    else:
        st.info("Nenhum evento encontrado para esta semana.")

    st.divider()

    st.markdown("**📋 Tarefas Pendentes**")

    if pendentes:
        df_t = pd.DataFrame(pendentes)
        
        for col in ["id", "descricao", "prazo", "status"]:
            if col not in df_t.columns:
                df_t[col] = ""
                
        df_t = df_t[["id", "descricao", "prazo", "status"]].sort_values("prazo", ignore_index=True)

        def _icone_prazo(prazo_str: str) -> str:
            try:
                prazo_dt = date.fromisoformat(str(prazo_str))
                if prazo_dt < HOJE_DATE:
                    return "🔴 Vencida"
                if (prazo_dt - HOJE_DATE).days <= 2:
                    return "🟡 Urgente"
            except (ValueError, TypeError):
                pass
            return "🟢 Ok"

        df_t.insert(0, "⚡", df_t["prazo"].apply(_icone_prazo))

        st.dataframe(
            df_t,
            hide_index=True,
            column_config={
                "⚡":        st.column_config.TextColumn("Status",   width="small"),
                "id":        st.column_config.NumberColumn("ID",     width="small"),
                "descricao": st.column_config.TextColumn("Descrição"),
                "prazo":     st.column_config.DateColumn("Prazo",    format="DD/MM/YYYY"),
                "status":    None,
            },
        )
        st.caption("🔴 Vencida  ·  🟡 Urgente (≤ 2 dias)  ·  🟢 Ok")
    else:
        st.success("🎉 Nenhuma tarefa pendente! Tudo em dia.")