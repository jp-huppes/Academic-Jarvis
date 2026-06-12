import json
from rag.pipeline import PipelineRAG
from datetime import datetime, timedelta

from tools.tarefas import liste_tarefas
from tools.agenda import consulte_agenda

_instancia_rag = None


def busque_material_rag(query: str) -> list[str]:
    """
    Busca trechos relevantes em arquivos PDF e TXT usando busca semantica (RAG).
        In:  query — pergunta ou termo de busca
        Out: lista de strings com os trechos mais relevantes encontrados
    """
    global _instancia_rag

    if _instancia_rag is None:
        try:
            print("   [RAG] Inicializando banco de dados vetorial de forma isolada...")
            _instancia_rag = PipelineRAG(device="cpu")
        except Exception as e:
            return [f"Erro ao carregar o modelo ou banco de dados: {e}"]

    try:
        parts = _instancia_rag.busque_trechos_relevantes(query, top_k=5)

        if not parts:
            return [
                f"Aviso do Banco de Dados: O termo '{query}' não retornou fragmentos diretos nos livros locais.\n"
                "Por favor, responda o aluno usando seu conhecimento geral (explicando o conceito de forma clara), "
                "mas avise de maneira amigável que esse termo exato não consta explicitamente nos PDFs da pasta 'data'."
            ]

        return parts

    except Exception as e:
        return [f"Erro interno ao consultar o banco de dados vetorial: {e}"]


def monte_plano_estudos(disciplina: str, data_prova: str = "") -> str:
    """
    Orquestrador: consolida dados de múltiplas fontes locais (Agenda, Tarefas, RAG)
    e retorna um prompt estruturado para que a LLM monte um plano de estudos.
        In:  disciplina  — nome da matéria ou tema (ex: 'Redes', 'IA')
             data_prova  — data da prova no formato 'AAAA-MM-DD' (opcional)
        Out: string com instruções + dados JSON para a LLM formatar o plano
    """
    today = datetime.now().date()

    result = {
        "disciplina": disciplina,
        "data_hoje": str(today),
        "dias_ate_prova": None,
        "eventos_relevantes": [],
        "tarefas_pendentes_da_disciplina": [],
        "todas_tarefas_pendentes": [],
        "trechos_do_material": [],
    }
    disciplina = disciplina.lower()

    # ------------------------------------------------------------------ #
    # 1. CALCULO DE DIAS ATE A PROVA (somente se a data for informada)
    # ------------------------------------------------------------------ #
    if data_prova:
        try:
            dt_test = datetime.strptime(data_prova, "%Y-%m-%d").date()
            result["dias_ate_prova"] = (dt_test - today).days
        except ValueError:
            result["erro"] = f"Formato de data inválido: '{data_prova}'. Use 'AAAA-MM-DD'."
            return json.dumps(result, ensure_ascii=False)

    # ------------------------------------------------------------------ #
    # 2. BUSCA DE EVENTOS NA AGENDA (proximas 2 semanas)
    # ------------------------------------------------------------------ #
    try:
        collected_events = []
        for offset in range(15):
            day = today + timedelta(days=offset)
            events_on_day = consulte_agenda(str(day))

            if isinstance(events_on_day, list):
                for event in events_on_day:
                    if isinstance(event, dict):
                        event_disc = str(event.get("disciplina", "")).lower()
                        event_type = str(event.get("tipo", "")).lower()

                        # filtro dentro do loop
                        if (disciplina in event_disc) or (disciplina in event_type):
                            event["dias_a_partir_de_hoje"] = offset
                            collected_events.append(event)

        result["eventos_relevantes"] = collected_events

    except Exception as e:
        result["erro_agenda"] = f"Falha ao consultar agenda: {e}"

    # ------------------------------------------------------------------ #
    # 3. BUSCA DE TAREFAS PENDENTES
    # ------------------------------------------------------------------ #
    try:
        all_pending = liste_tarefas("pendente")

        if isinstance(all_pending, list):
            result["todas_tarefas_pendentes"] = [
                t.get("titulo", t.get("descricao", "Tarefa sem nome"))
                for t in all_pending
                if isinstance(t, dict)
            ]

            result["tarefas_pendentes_da_disciplina"] = [
                t for t in all_pending
                if isinstance(t, dict) and (
                    disciplina in str(t.get("titulo", "")).lower()
                    or disciplina in str(t.get("descricao", "")).lower()
                )
            ]
    except Exception as e:
        result["erro_tarefas"] = f"Falha ao consultar tarefas: {e}"

    # ------------------------------------------------------------------ #
    # 4. BUSCA DE TRECHOS RELEVANTES NO RAG
    # ------------------------------------------------------------------ #
    try:
        parts = busque_material_rag(f"conceitos principais fundamentais de {disciplina}")
        result["trechos_do_material"] = parts
    except Exception as e:
        result["erro_rag"] = f"Falha ao consultar RAG: {e}"

    # ------------------------------------------------------------------ #
    # Retorna prompt estruturado para a LLM formatar o plano final
    # ------------------------------------------------------------------ #
    output = f"""
    INSTRUÇÕES DE SISTEMA PARA A LLM:
    Os dados brutos abaixo foram coletados dinamicamente do banco de dados do aluno.
    Sua missão é agir como um tutor e criar um plano de estudos textual, separando os dias,
    incluindo as tarefas que ele precisa fazer e resumindo os conceitos do RAG que ele precisa ler.

    DADOS DO ALUNO (em JSON):
    {json.dumps(result, indent=4, ensure_ascii=False)}
    """

    return output