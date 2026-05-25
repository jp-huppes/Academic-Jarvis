"""
Array de dicionários de Ferramentas (Tool Calling)
    - Função: Deixar claro para a LLM (Gemma) quais funções ela tem à disposição.
    - Estrutura padrão: Define o nome, o que a função faz (description) e quais 
      parâmetros (properties) ela deve enviar obrigatoriamente (required).
"""

DADOS_DAS_FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "consulte_agenda",
            "description": "Consulta os compromissos acadêmicos (aulas e provas) de um dia específico.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "A data específica para consulta no formato 'AAAA-MM-DD'. Importante: Calcule esta data com base no dia atual fornecido no prompt de sistema. Por exemplo, se hoje é Domingo 24 de Maio de 2026, quarta-feira será '2026-05-27'."
                    }
                },
                "required": ["data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "liste_tarefas",
            "description": "Lista as tarefas acadêmicas filtradas pelo status atual do progresso.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pendente", "concluida"],
                        "description": "O status das tarefas. Use 'pendente' para o que falta fazer ou 'concluida' para o que já foi feito."
                    }
                },
                "required": ["status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adicione_tarefas",
            "description": "Adiciona uma nova tarefa acadêmica à lista do estudante com status inicial pendente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "descricao": {
                        "type": "string",
                        "description": "O que precisa ser feito (Ex: 'Estudar para a prova de Cálculo')."
                    },
                    "prazo": {
                        "type": "string",
                        "description": "A data limite para entrega no formato 'AAAA-MM-DD' (Ex: '2026-05-25')."
                    }
                },
                "required": ["descricao", "prazo"]
            }
        }
    },
    {"type": "function",
        "function": {
            "name": "conclua_tarefa",
            "description": "Marca uma tarefa específica como concluída no sistema. Pode ser feita informando o ID numérico diretamente ou por uma palavra-chave (termo de busca) caso o usuário não saiba o ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_task": {
                        "type": "string",
                        "description": "O ID numérico único da tarefa que será marcada como concluída. Deixe vazio se o usuário não informar o ID explicitamente."
                    },
                    "termo_busca": {
                        "type": "string",
                        "description": "Palavra-chave extraída do pedido do usuário para identificar a tarefa por texto quando o ID não for fornecido (ex: se o usuário disser 'conclua a de redes', envie 'redes')."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "busque_material_rag",
            "description": "Busca conteúdos, conceitos, fórmulas e explicações nos materiais didáticos de estudo (PDFs e TXTs) usando busca semântica. Use sempre que o aluno fizer perguntas teóricas ou dúvidas sobre matérias escolares.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A pergunta ou conceito exato que o estudante quer saber (ex: 'O que é uma fila de prioridades?', 'Explique regressão logística')."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consulte_semana",
            "description": "Consulta todos os compromissos acadêmicos (aulas e provas) da semana atual inteira.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "nome_ferramenta": "adicione_agenda",
        "descricao": "Adiciona um novo compromisso na agenda do aluno (como aulas, provas, revisões ou reuniões). Use sempre que o usuário pedir explicitamente para marcar ou agendar algo na agenda acadêmica.",
        "argumentos": {
            "data": {"type": "string", "description": "Data do compromisso no formato exato 'AAAA-MM-DD'"},
            "hora": {"type": "string", "description": "Horário do compromisso no formato exato 'HH:MM'"},
            "disciplina": {"type": "string", "description": "Nome da matéria, disciplina ou título do compromisso"},
            "tipo": {"type": "string", "description": "Tipo do evento, obrigatoriamente um destes: 'Aula', 'Prova', 'Trabalho', 'Reunião'"},
            "local": {"type": "string", "description": "Local opcional do evento (Ex: 'Sala 105, Bloco 1' ou 'Google Meet')"}
        }
    }
]