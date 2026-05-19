import json
import os

CAMINHO_TAREFA = os.path.join("memory","tarefas.json")

def liste_tarefas(status: str = "pendente") -> list[dict]:
    """
    Lista tarefas academicas filtradas pelo status atual!

        In: String [pendente,concluida]
        Out: Lista de dicionários com as tarefas correspondentes
    """
    if not os.path.exists(CAMINHO_TAREFA):
        return []
    try:
        with open(CAMINHO_TAREFA,"r",encoding="utf-8") as file:
            tasks = json.load(file)
        tasks_events = [t for t in tasks if t["status"] == status]
        return tasks_events
    except Exception:
        return []

def adicione_tarefas(descricao: str, prazo: str) -> dict:
    """
    Adiciona tarefa a lisat com status inicial 'pendente'

        In: descricao do que precisa ser feito
            data limite no formato 'AAAA-MM-DD'
        Out: Dicionário da nova tarefa ou dicionário com mensagem de erro
    """
    try:
        tasks = []
        if os.path.exists(CAMINHO_TAREFA):
            with open(CAMINHO_TAREFA,"r",encoding="utf-8") as file:
                tasks = json.load(file)
        new_id = max([t["id"] for t in tasks], default=0) + 1

        new_task = {
            "id": new_id,
            "descricao":descricao,
            "prazo": prazo,
            "status": "pendente"
        }

        tasks.append(new_task)
        with open(CAMINHO_TAREFA, 'w',encoding="utf-8") as file:
            json.dump(tasks,file,indent=2,ensure_ascii=False)
        return new_task
    except Exception as e:
        return {"erro": f"Falha ao adicionar tarefa: {str(e)}"}

def conclua_tarefa(id_: int) -> dict:
    """
    Procura tarefa por ID e altera status para 'concluida'
        In:  ID da tarefa
        Out: Dicioário da tarefa atualizada ou dicionário com mensagem de erro. 
    """

    try: 
        if not os.path.exists(CAMINHO_TAREFA):
            return{"erro": "Ficheiro de dados não encontrado."}
        with open(CAMINHO_TAREFA, 'r',encoding="utf-8") as file:
            tasks = json.load(file)
            
        att_tasks = None
        for t in tasks:
            if t["id"] == id_:
                t["status"] = "concluida"
                att_tasks = t
                break
        if not att_tasks:
            return {"erro": f"Nenhuma tarefa encontrada com o ID {id_}."}
        
        with open(CAMINHO_TAREFA, "w",encoding="utf-8") as file:
            json.dump(tasks,file,indent=2,ensure_ascii=False)
        return att_tasks
    except Exception as e:
        return {"erro": f"Falha ao concluir tarefa: {str(e)}"}
        

        