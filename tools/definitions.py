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
                        "description": "A data específica para consulta no formato 'AAAA-MM-DD'. Calcule esta data com base no dia atual fornecido no prompt de sistema."
                    }
                },
                "required": ["data"]
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
        "type": "function",
        "function": {
            "name": "adicione_agenda",
            "description": "Adiciona um novo compromisso na agenda do aluno (como aulas, provas, revisões ou reuniões). Use sempre que o usuário pedir explicitamente para marcar ou agendar algo na agenda acadêmica.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data":       {"type": "string", "description": "Data do compromisso no formato exato 'AAAA-MM-DD'."},
                    "hora":       {"type": "string", "description": "Horário do compromisso no formato exato 'HH:MM'."},
                    "disciplina": {"type": "string", "description": "Nome da matéria, disciplina ou título do compromisso."},
                    "tipo":       {"type": "string", "description": "Tipo do evento — um destes: 'Aula', 'Prova', 'Trabalho', 'Reunião'."},
                    "local":      {"type": "string", "description": "Local opcional do evento (Ex: 'Sala 105, Bloco 1' ou 'Google Meet')."}
                },
                "required": ["data", "hora", "disciplina", "tipo"]
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
                    "titulo": {
                        "type": "string",
                        "description": "Título curto da tarefa — o que precisa ser feito (Ex: 'Estudar para a prova de Cálculo')."
                    },
                    "prazo": {
                        "type": "string",
                        "description": "A data limite para entrega no formato 'AAAA-MM-DD' (Ex: '2026-05-25')."
                    },
                    "descricao": {
                        "type": "string",
                        "description": "Opcional. Detalhes adicionais sobre a tarefa (Ex: 'Focar nos capítulos 3 e 4')."
                    }
                },
                "required": ["titulo", "prazo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "conclua_tarefa",
            "description": "Marca uma tarefa específica como concluída. Pode ser pelo ID numérico ou por uma palavra-chave se o usuário não souber o ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_task": {
                        "type": "string",
                        "description": "O ID numérico único da tarefa. Deixe vazio se o usuário não informar o ID explicitamente."
                    },
                    "termo_busca": {
                        "type": "string",
                        "description": "Palavra-chave extraída do pedido do usuário para identificar a tarefa por texto (ex: se o usuário disser 'conclua a de redes', envie 'redes')."
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
            "name": "monte_plano_estudos",
            "description": "Gera um plano de estudos inteligente e personalizado combinando as pendências de tarefas do aluno, os compromissos da agenda e os tópicos teóricos extraídos dos livros via RAG.",
            "parameters": {
                "type": "object",
                "properties": {
                    "disciplina": {
                        "type": "string",
                        "description": "O nome da disciplina ou matéria para a qual o plano deve ser gerado (Ex: 'Redes', 'Algoritmos')."
                    },
                    "data_prova": {
                        "type": "string",
                        "description": "Opcional. A data da prova no formato 'AAAA-MM-DD' para organizar um cronograma regressivo até o dia do exame."
                    }
                },
                "required": ["disciplina"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "prepare_contexto_quiz",
            "description": "Cria um simulado/quiz de múltipla escolha personalizado sobre uma disciplina específica usando materiais do RAG e histórico do aluno. Use sempre que o usuário pedir para testar seus conhecimentos, fazer um quiz, perguntas ou simulado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "disciplina": {
                        "type": "string",
                        "description": "O nome da disciplina ou assunto que o usuário quer praticar (ex: 'Redes de Computadores', 'Cálculo', 'Estrutura de Dados')."
                    }
                },
                "required": ["disciplina"]
            }
        }
    }
]