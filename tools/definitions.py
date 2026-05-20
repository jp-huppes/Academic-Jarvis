
"""

Array de dicionário
    - Função é simples, deixar claro para a LLM (Gemma) o que cada uma das funções que ele tem em mãos:
        - O que ela faz
        - Quais parâmetros elas esperam receber

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
                        "description": "A data desejada no formato 'AAAA-MM-DD' (Ex: '2026-05-20')."
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
                        "description": "O status das tarefas. Use 'pendente' para o que falta fazer ou 'concluida' para o que já fez."
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
    {
        "type": "function",
        "function": {
            "name": "conclua_tarefa",
            "description": "Procura uma tarefa acadêmica pelo seu ID numérico e altera o status dela para 'concluida'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_": {
                        "type": "integer",
                        "description": "O ID numérico único da tarefa que deve ser marcada como concluída."
                    }
                },
                "required": ["id_"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_material_rag",
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
    }
]