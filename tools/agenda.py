import json
import os
from datetime import datetime, timedelta

CAMINHO_AGENDA = os.path.join(os.path.dirname(__file__), "..", "memory", "agenda.json")

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

def consulte_semana() -> list[dict]:
    """
    Consulta os compromissos (aulas e provas) para a semana atual.
        Out: Lista de dicionários contendo os eventos encontrados nesta semana
    """
    if not os.path.exists(CAMINHO_AGENDA):
        return []
    try:
        with open(CAMINHO_AGENDA, "r", encoding="utf-8") as file:
            events = json.load(file)
        
        hoje = datetime.now()
        # Calcula a data da segunda-feira e do domingo desta semana
        segunda = hoje - timedelta(days=hoje.weekday())
        domingo = segunda + timedelta(days=6)
        
        # Converte para string no formato AAAA-MM-DD
        str_segunda = segunda.strftime("%Y-%m-%d")
        str_domingo = domingo.strftime("%Y-%m-%d")
        
        # Filtra os eventos que estão entre segunda e domingo
        filtered_events = [e for e in events if str_segunda <= e["data"] <= str_domingo]
        return filtered_events
    except Exception:
        return []
    
def adicione_agenda(data: str, hora: str, disciplina: str, tipo: str, local: str = "") -> dict:
    """
    Adiciona um novo compromisso (aula, prova, reunião, etc.) na agenda.
    In: data: String no formato 'AAAA-MM-DD'
        hora: String no formato 'HH:MM'
        disciplina: Nome da matéria ou compromisso
        tipo: Tipo do evento (Ex: 'Aula', 'Prova', 'Trabalho')
        local: Sala de aula, bloco ou link (Opcional)
    Out: Dicionário confirmando o sucesso e os dados salvos
    """
    try:
        events = []
        # Se o arquivo já existir, lê os eventos atuais
        if os.path.exists(CAMINHO_AGENDA):
            with open(CAMINHO_AGENDA, "r", encoding="utf-8") as file:
                try:
                    events = json.load(file)
                except json.JSONDecodeError:
                    events = []

        # Monta o novo compromisso estruturado
        novo_evento = {
            "data": data,
            "hora": hora,
            "disciplina": disciplina,
            "tipo": tipo,
            "local": local
        }

        # Adiciona e salva de volta
        events.append(novo_evento)
        with open(CAMINHO_AGENDA, "w", encoding="utf-8") as file:
            json.dump(events, file, indent=4, ensure_ascii=False)

        return {"status": "sucesso", "mensagem": "Compromisso adicionado à agenda", "evento": novo_evento}
        
    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro ao salvar na agenda: {e}"}