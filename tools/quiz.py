import json
from tools.tarefas import liste_tarefas
from tools.estudos import busque_material_rag


def prepare_contexto_quiz(disciplina: str, pipeline_rag = None) -> str:
    """
    coleta materiais do RAG e histórico de tarefas para montar o contexto de um Quiz.
    retorna um prompt instruindo a LLM a gerar perguntas de múltipla escolha em JSON puro.
        In:  disciplina — nome da matéria ou tema que o aluno quer praticar
        Out: string com instruções + dados JSON para a LLM gerar o quiz
    """
    result = {
        "disciplina": disciplina,
        "trechos_rag": [],
        "tarefas_estudadas": [],
    }


    disciplina = disciplina.lower()

    # ------------------------------------------------------------------ #
    # 1. BUSCA DE CONCEITOS NO RAG
    # ------------------------------------------------------------------ #
    try:
        query_search = f"principais definições e conceitos para avaliação de {disciplina}"
        parts = busque_material_rag(query_search)

        if not parts:
            result["trechos_rag"] = [
                f"Aviso: Não encontramos fragmentos diretos para '{disciplina}' nos materiais locais."
            ]
        else:
            result["trechos_rag"] = parts

    except Exception as e:
        result["erro_rag"] = f"Falha ao consultar RAG para o quiz: {e}"

    # ------------------------------------------------------------------ #
    # HISTORICO DE TAREFAS (dedicacao do aluno a disciplina)
    # ------------------------------------------------------------------ #
    try:
        all_pending   = liste_tarefas("pendente")
        all_completed = liste_tarefas("concluida")

        filtered_tasks = []

        if isinstance(all_pending, list):
            filtered_tasks.extend([
                f"[PENDENTE] {t.get('titulo', t.get('descricao', ''))}"
                for t in all_pending
                if isinstance(t, dict) and (
                    disciplina in str(t.get("titulo", "")).lower()
                    or disciplina in str(t.get("descricao", "")).lower()
                )
            ])

        if isinstance(all_completed, list):
            filtered_tasks.extend([
                f"[ESTUDADO] {t.get('titulo', t.get('descricao', ''))}"
                for t in all_completed
                if isinstance(t, dict) and (
                    disciplina in str(t.get("titulo", "")).lower()
                    or disciplina in str(t.get("descricao", "")).lower()
                )
            ])

        result["tarefas_estudadas"] = filtered_tasks

    except Exception as e:
        result["erro_tarefas"] = f"Falha ao consultar histórico de tarefas: {e}"

    # ------------------------------------------------------------------ #
    # Retorna prompt com contrato de saida JSON para a LLM
    # ------------------------------------------------------------------ #
    output = f"""
    INSTRUÇÕES DE SISTEMA PARA A LLM (MODO QUIZ):
    Você é um professor criando um quiz de múltipla escolha focado em Active Recall
    para testar o conhecimento do aluno sobre a disciplina de {disciplina}.
    Use os dados abaixo (conceitos teóricos extraídos do RAG e o histórico de tarefas do aluno)
    para formular perguntas relevantes, desafiadoras e alinhadas ao que ele tem estudado.

    DADOS DO ALUNO E MATERIAIS DE ESTUDO (em JSON):
    {json.dumps(result, indent=4, ensure_ascii=False)}

    REQUISITO CRÍTICO DE SAÍDA (CONTRATO DE API):
    Você não deve gerar nenhum texto de saudação, confirmação ou formatação Markdown.
    Você deve responder ÚNICA e EXCLUSIVAMENTE com uma lista (array) JSON contendo exatamente 3 a 5 perguntas.
    A sua resposta deve ser um JSON válido que possa ser lido diretamente pela função `json.loads()` do Python.

    ESTRUTURA OBRIGATÓRIA DO JSON:
    [
        {{
            "id": 1,
            "pergunta": "Texto da pergunta gerada?",
            "alternativas": {{
                "A": "Primeira opção",
                "B": "Segunda opção",
                "C": "Terceira opção",
                "D": "Quarta opção"
            }},
            "resposta_correta": "C",
            "explicacao": "Explicação didática focada em reforço positivo, detalhando por que a alternativa está correta baseada no material do RAG."
        }}
    ]
    """
    return output