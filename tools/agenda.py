import json
import os

CAMINHO_AGENDA = os.path.join("memory","agenda.json")

def consulte_agenda(data: str) -> list[dict]:
    """
    Função de consulta dos compromissos (aulas e provas) para um dia especifico

        In: String no formato 'AAAA-MM-DD'
        Out: List de dicionario contendo os eventos encontrados nessa data
    """

    if not os.path.exists(CAMINHO_AGENDA):
        return[]
    try:
        with open(CAMINHO_AGENDA,"r",encoding="utf-8") as file:
            events = json.load(file)
        
        filtered_events = [e for e in events if e["data"] == data]
        return filtered_events
    except Exception:
        return []
