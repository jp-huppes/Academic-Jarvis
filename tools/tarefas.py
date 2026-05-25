import json
import os

CAMINHO_TAREFAS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "memory", "tarefas.json"))

def liste_tarefas(status=None):
    """
    Lista tarefas academicas filtradas pelo status atual!

        In: String [pendente,concluida]
        Out: Lista de dicionários com as tarefas correspondentes
    """
    if not os.path.exists(CAMINHO_TAREFAS):
        return []
    
    try:
        with open(CAMINHO_TAREFAS, "r", encoding="utf-8") as f:
            tarefas = json.load(f)
    except Exception:
        return []
        
    # Normalização robusta para o filtro de status
    if status in ["pendente", "pendentes"]:
        return [t for t in tarefas if t.get("concluida") is False]
    elif status in ["concluidada", "concluida", "concluidas", "concluídas"]:
        return [t for t in tarefas if t.get("concluida") is True]
        
    return tarefas

def adicione_tarefas(titulo, prazo, descricao=""):
    if not os.path.exists(CAMINHO_TAREFAS):
        tarefas = []
    else:
        try:
            with open(CAMINHO_TAREFAS, "r", encoding="utf-8") as f:
                tarefas = json.load(f)
        except Exception:
            tarefas = []

    novo_id = str(max([int(t["id"]) for t in tarefas] + [0]) + 1)
    nova_tarefa = {
        "id": novo_id,
        "titulo": titulo,
        "prazo": prazo,
        "concluida": False,
        "descricao": descricao
    }
    tarefas.append(nova_tarefa)

    with open(CAMINHO_TAREFAS, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)
    return nova_tarefa

def conclua_tarefa(id_task=None, termo_busca=None):
    if not os.path.exists(CAMINHO_TAREFAS):
        return {"status": "erro", "mensagem": "Arquivo de tarefas não encontrado."}
        
    try:
        with open(CAMINHO_TAREFAS, "r", encoding="utf-8") as f:
            tarefas = json.load(f)
    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro ao ler arquivo: {e}"}

    # CASO 1: O usuário forneceu o ID diretamente
    if id_task:
        id_str = str(id_task).strip()
        for t in tarefas:
            if str(t.get("id")).strip() == id_str:
                t["concluida"] = True
                with open(CAMINHO_TAREFAS, "w", encoding="utf-8") as f:
                    json.dump(tarefas, f, indent=4, ensure_ascii=False)
                return {"status": "sucesso", "mensagem": f"Tarefa '{t.get('titulo')}' (ID {id_str}) concluída com sucesso!"}
        return {"status": "erro", "mensagem": f"Nenhuma tarefa encontrada com o ID {id_str}."}

    # CASO 2: ID ausente, mas temos um termo de busca (Ex: "redes")
    if termo_busca:
        termo = str(termo_busca).lower().strip()
        # Filtra apenas correspondências em tarefas ainda PENDENTES
        correspondencias = [
            t for t in tarefas
            if not t.get("concluida") and (
                termo in str(t.get("titulo", "")).lower() or 
                termo in str(t.get("descricao", "")).lower()
            )
        ]

        # Sub-caso A: Encontrou exatamente UMA tarefa correspondente -> Conclui direto!
        if len(correspondencias) == 1:
            tarefa_alvo = correspondencias[0]
            for t in tarefas:
                if t["id"] == tarefa_alvo["id"]:
                    t["concluida"] = True
            with open(CAMINHO_TAREFAS, "w", encoding="utf-8") as f:
                json.dump(tarefas, f, indent=4, ensure_ascii=False)
            return {
                "status": "sucesso",
                "mensagem": f"Tarefa resolvida automaticamente por texto: '{tarefa_alvo.get('titulo')}' (ID {tarefa_alvo['id']}) foi marcada como concluída."
            }

        # Sub-caso B: Encontrou MÚLTIPLAS tarefas com o mesmo termo -> Devolve para a LLM listar
        elif len(correspondencias) > 1:
            lista_opcoes = [{"id": t["id"], "titulo": t["titulo"], "prazo": t["prazo"]} for t in correspondencias]
            return {
                "status": "multiplas_opcoes",
                "mensagem": f"Encontrei mais de uma tarefa pendente correspondente ao termo '{termo_busca}'.",
                "opcoes": lista_opcoes
            }
        
        # Sub-caso C: Não encontrou nada
        else:
            return {
                "status": "erro",
                "mensagem": f"Nenhuma tarefa pendente encontrada correspondente ao termo '{termo_busca}'."
            }

    return {"status": "erro", "mensagem": "É necessário fornecer o 'id_task' ou um 'termo_busca' válido."}