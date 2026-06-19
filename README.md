# Academic JARVIS — AI Agent

O **Academic JARVIS** é um assistente inteligente projetado para auxiliar estudantes universitários no gerenciamento de sua rotina acadêmica e na extração de conhecimento de materiais didáticos.

O sistema opera como um **Agente Raciocinador**: utilizando de um modelo de linguagem (LLM) analisa cada mensagem do usuário, decide qual ferramenta local acionar (*Tool Calling*) e combina os resultados para gerar respostas contextualizadas. O agente integra gestão de agenda, lista de tarefas, busca semântica em PDFs (RAG), geração de planos de estudo e um sistema interativo de quiz baseado em Active Recall.

1. Link do video (1): https://youtu.be/03CtOU_9cgA

   Link do vídeo (2): .....

2. Link do arquivo usado no video no Docs: https://drive.google.com/file/d/1IA6u3JEIZeixIgAZ3N57Q0tAw8lfxhfN/view?usp=drive_link


---

## 1. Funcionalidades (Tools Implementadas)

| Ferramenta | Descrição |
|---|---|
| `consulte_agenda` | Consulta compromissos de um dia específico |
| `consulte_semana` | Consulta toda a agenda da semana atual, com filtro por tipo |
| `adicione_agenda` | Adiciona novo compromisso à agenda |
| `liste_tarefas` | Lista tarefas filtradas por status (pendente/concluída) |
| `adicione_tarefas` | Adiciona nova tarefa com título, prazo e descrição opcional |
| `conclua_tarefa` | Marca tarefa como concluída por ID ou por palavra-chave |
| `busque_material_rag` | Busca semântica bilíngue (PT+EN) nos materiais da pasta `/data` |
| `monte_plano_estudos` | Combina agenda, tarefas e RAG para gerar plano de estudos |
| `prepare_contexto_quiz` | Gera quiz de múltipla escolha personalizado via RAG |

### Melhorias de Aprendizado

- **Geração de Plano de Estudos:** a ferramenta `monte_plano_estudos` orquestra três fontes de dados simultaneamente e instrui a LLM a produzir um cronograma por dia com tarefas e resumo dos conceitos.
- **Quiz Interativo (Active Recall):** a aba *Quiz Prático* permite ao aluno escolher uma disciplina, gerar um simulado dinâmico baseado nos PDFs indexados e receber feedback imediato com explicação para cada questão.

---

## 2. Modelos de IA Utilizados

| Papel | Modelo | Localização |
|---|---|---|
| Orquestrador LLM | `Qwen2.5-14B-Instruct-AWQ` | API externa — servidor UFMS |
| Embeddings (RAG) | `paraphrase-multilingual-MiniLM-L12-v2` | Local (CPU/CUDA via `sentence-transformers`) |
| Tradução de query | `GoogleTranslator` (deep-translator) | Local |
| Vector Store | `ChromaDB` (persistente em disco) | Local (`data/chroma_db/`) |


> A busca RAG é **bilíngue**: cada consulta é traduzida automaticamente para PT e EN antes de ser enviada ao ChromaDB, compensando a diferença de idioma entre as perguntas (português) e os livros indexados (inglês).

---

## 3. Ferramentas de IA Usadas no Desenvolvimento

- **Claude (Anthropic)** — Desing de Prompts, auxiliar no planejamento de arquitetura.

- **Google Gemini** — 
Refatoração, Mitigação de Bugs e erros de sintaxe, alem de Otimização do pipeline.

---

## 4. Como Executar o Projeto

### Pré-requisitos

- Python **3.10** ou superior
- `pip` atualizado

### Instalação

**1. Clone o repositório:**
```bash
git clone https://github.com/jp-huppes/Academic-Jarvis.git
cd Academic-Jarvis
```

**2. Crie e ative o ambiente virtual:**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**4. Configure a chave de API:**

Crie um arquivo `.env` na raiz do projeto:
```
API_KEY=sua_chave_aqui
```
>SEGURANÇA: Certifique-se de que o arquivo .env esteja listado no seu .gitignore para evitar o vazamento acidental da chave (caso publique em um repositório público no GitHub)

### Indexação do RAG (primeira execução obrigatória)

Processa todos os PDFs e TXTs da pasta `/data` e alimenta o ChromaDB:
```bash
python indexar.py
```

> Este passo só precisa ser repetido se novos documentos forem adicionados à pasta "`/data`".

### Executar a Interface Gráfica (recomendado)

```bash
python -B -m streamlit run app.py
```

Acesse `http://localhost:8501` no navegador.

### Executar via Terminal (alternativo, sem quiz)

```bash
python main.py
```

---

## 5. Estrutura do Projeto

```
Academic-Jarvis/
│
├── .streamlit/             # Tema e configurações visuais do Streamlit
├── data/                   # Dataset: PDFs e TXTs acadêmicos (36 arquivos)
│   └── chroma_db/          # [Gerado] Banco vetorial ChromaDB (não versionar)
│
├── logs/
│   └── tool_calls.jsonl    # Registro automático de todas as chamadas de ferramentas
│
├── memory/
│   ├── agenda.json         # Dados persistentes da agenda acadêmica
│   └── tarefas.json        # Dados persistentes da lista de tarefas
│
├── rag/
│   └── pipeline.py         # Pipeline RAG: leitura, chunking, embeddings e busca
│
├── tools/
│   ├── agenda.py           # Backend das ferramentas de calendário
│   ├── tarefas.py          # Backend das ferramentas de tarefas
│   ├── estudos.py          # Tool RAG com busca bilíngue e geração de plano de estudos
│   ├── quiz.py             # Geração de quiz de múltipla escolha via RAG
│   ├── logger.py           # Sistema de log JSONL de tool calls
│   └── definitions.py      # Schemas JSON das ferramentas para o Tool Calling
│
├── app.py                  # Interface gráfica Streamlit (execução principal)
├── main.py                 # Interface de linha de comando (CLI)
├── indexar.py              # Script de indexação e atualização do banco RAG
├── requirements.txt        # Dependências do projeto
└── README.md               # Este arquivo
```

---

## 6. Dataset

### Origem e Composição

A pasta `/data` contém **36 documentos acadêmicos** cobrindo as disciplinas do curso. Entre as principais referências indexadas:

| Arquivo | Conteúdo |
|---|---|
| `computer_networking_top-down_approach.pdf` | Redes de Computadores — Kurose & Ross |
| `Machine_Learning.pdf` | Aprendizado de Máquina — Tom Mitchell |
| `algoritmos-teoria-e-pratica-thomas-cormen.pdf` | Algoritmos — Thomas Cormen |
| `Deep+Learning+Ian+Goodfellow.pdf` | Deep Learning — Ian Goodfellow |
| `2020-Scrum-Guide-Portuguese-European.pdf` | Metodologias Ágeis — Scrum Guide |

Outros documentos cobrem: Álgebra Linear, Teoria da Computação (LFA), Linguagens de Programação (C++ e Java), Probabilidade e Estatística, e resumos de aulas em formato TXT.

### Tipo de Dados

Arquivos em formato **PDF** (livros e apostilas) e **TXT** (notas e resumos de aula).

### Limitações Conhecidas

- **Restrição textual:** a extração por meio `pdfplumber` lê estritamente texto plano. Diagramas, imagens, gráficos e tabelas complexas não são indexados.
- **Alinhamento linguístico:** os livros estão majoritariamente em inglês (língua de origem) enquanto as consultas ocorrem em português. Mitigado pela busca bilíngue automática com `deep-translator`.
- **Cobertura temática:** o dataset cobre as disciplinas do semestre atual. Ou seja, tópicos fora desse escopo retornam respostas baseadas no conhecimento geral da LLM, com aviso ao usuário.

### Estratégia de Chunking

| Parâmetro | Valor |
|---|---|
| Algoritmo | `RecursiveCharacterTextSplitter` (LangChain) |
| Tamanho do chunk | 1200 caracteres |
| Sobreposição (overlap) | 250 caracteres |
| Separadores de prioridade | `\n\n` → `\n` → ` ` → `""` |

O `RecursiveCharacterTextSplitter` respeita quebras naturais de parágrafo e sentença antes de cortar por tamanho fixo, preservando a coerência semântica dos fragmentos. A sobreposição de 250 caracteres garante continuidade entre chunks vizinhos, evitando perda de contexto em fronteiras.

**Impacto no RAG:** chunks maiores (1200 VS 500 da versão anterior) reduzem a fragmentação de explicações técnicas longas, melhorando a qualidade das respostas. O overlap maior garante que sentenças divididas na borda de um chunk sejam capturadas pelo chunk seguinte.

---

## 7. Arquitetura do Sistema

```
Usuário
   ↓
Interface (Streamlit / CLI)
   ↓
Orquestrador — LLM Qwen2.5-14B
   ↓ decide qual tool chamar (até 3 iterações por turno)
Tool Router (MAPEADOR_DE_TOOLS)
    ├── consulte_agenda / consulte_semana / adicione_agenda  →  memory/agenda.json
    ├── liste_tarefas / adicione_tarefas / conclua_tarefa    →  memory/tarefas.json
    ├── busque_material_rag  →  Tradutor (PT ↔ EN)  →  ChromaDB (Base Bilíngue)
    ├── monte_plano_estudos  ─  →  Agenda + Tarefas + RAG
    └── prepare_contexto_quiz ─  →  RAG → JSON → Quiz Engine
                                          ↓
                               logs/tool_calls.jsonl
```

---

## 8. Avaliação do Sistema (Testes de Integração)

O sistema foi submetido a um plano de testes práticos focado em estressar as capacidades de recuperação (RAG), uso de ferramentas (Tasks/Agenda) e raciocínio (Plano de Estudos) da LLM.

### Tabela de Resultados

| # | Categoria | Pergunta | Tool Acionada | Resposta do JARVIS | Classificação |
|---|---|---|---|---|---|
| 1 | RAG | O que é o protocolo TCP e como ele garante a entrega confiável de dados? | `busque_material_rag` | Explicou corretamente os mecanismos (Acknowledgment, Retransmissão, Sequencing, Checksum) usando o material. Citou as fontes ao final. | **Correta** |
| 2 | RAG | Explique o algoritmo QuickSort e qual é sua complexidade de tempo no pior caso. | `busque_material_rag` | Descreveu o particionamento via pivô e acertou a complexidade do pior caso ($O(n^2)$) e do caso médio. | **Correta** |
| 3 | RAG | O que é overfitting em Machine Learning e como podemos evitá-lo? | `busque_material_rag` | Definiu o conceito e listou múltiplas técnicas precisas extraídas dos livros (L1/L2, Dropout, Cross-Validation, Early Stopping). | **Correta** |
| 4 | Agenda | O que tenho na agenda para hoje? | `consulte_agenda` | Consultou a data do sistema (19/06/2026) e confirmou que a agenda do dia estava livre. | **Correta** |
| 5 | Agenda | Quais provas tenho marcadas esta semana? | `consulte_semana` | Filtrou com sucesso apenas as 3 provas (LFA, Prob/Est e Álgebra Linear) dentre todos os eventos retornados pela Tool. | **Correta** |
| 6 | Tarefas | Liste todas as minhas tarefas pendentes. | `liste_tarefas` | Listou 8 tarefas corretamente com suas respectivas descrições e prazos do arquivo JSON. | **Correta** |
| 7 | Tarefas | Adiciona uma tarefa chamada "Revisar conteúdo de Scrum" com prazo para a próxima sexta-feira. | `adicione_tarefas` | Adicionou a tarefa com sucesso, mas **errou o cálculo da data**. "Próxima sexta" a partir de 19/06 seria 26/06, mas a LLM agendou para 24/06 (quarta-feira). | **Parcialmente Correta** |
| 8 | Planejamento | Monte um plano de estudos completo para a disciplina de IA. | `monte_plano_estudos` | Estruturou um plano coerente de 5 dias combinando ML, DL e criação de quizzes, mas sofreu de *memory leak*, incluindo a tarefa "Scrum" (da pergunta anterior) no plano de IA. | **Parcialmente Correta** |
| 9 | Quiz | Quero fazer um simulado sobre algoritmos de ordenação. | `prepare_contexto_quiz` | Confirmou a geração do JSON estruturado e redirecionou o usuário para a aba 'Quiz Prático'. A interface renderizou com sucesso. | **Correta** |
| 10 | Falha Intencional | Quais são as equações diferenciais usadas no modelo SIR? | `busque_material_rag` | Respondeu detalhadamente com conhecimento interno (já que não há livros de biologia no RAG), mas **falsificou a tag** de fontes consultadas, falhando no isolamento do contexto. | **Incorreta (Esperada)** |

### Análise de Comportamento e Oportunidades de Melhoria

A execução prática revelou que o core do RAG e das APIs internas está operando de forma perfeitamente estável. Os pontos de falha (Questões 7, 8 e 10) demonstram comportamentos nativos de Modelos de Linguagem (LLMs) que validam a necessidade de *guardrails* adicionais no futuro:

* **Raciocínio Matemático (Erro de Datas Relativas):** A LLM falhou no cálculo de deslocamento de dias do calendário. A mitigação ideal é delegar essa responsabilidade para o código Python ao invés de depender do raciocínio da IA.
* **Vazamento de Contexto (Memory Leak em Planos):** Ao orquestrar o plano de estudos, a IA puxou tarefas que estavam apenas no histórico ativo da conversa, misturando contextos. Pode ser mitigado reforçando o *System Prompt* para se ater estritamente ao Payload da *tool*.
* **Alucinação Positiva (Falsa Citação):** Ao não encontrar dados no RAG sobre um tema, a IA usou conhecimento pré-treinado para não deixar o usuário sem resposta, mas manteve a máscara de citação do sistema. Reforços nas condicionais de falha do RAG resolverão este comportamento.
