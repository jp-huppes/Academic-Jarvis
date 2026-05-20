#   Academic JARVIS - AI Agent

Um assistente inteligente em linha de comando (CLI) projetado para gerenciar tarefas, monitorar agenda estudantil e realizar buscas semânticas (RAG) em materiais acadêmicos locais.

##   Funcionalidades (Tools)
1. **Gestão de Tarefas e Agenda:** Lê, adiciona e conclui tarefas via manipulação de arquivos JSON locais.
2. **Busca Semântica Avançada (RAG):** Vasculha PDFs e resumos locais usando um banco de dados vetorial baseado em embeddings multilíngues.
3. **Memória Conversacional:** Mantém o contexto do chat ativo durante a execução.

##   Modelos de IA Utilizados
* **Orquestrador LLM:** `Gemma-3-12b-it` (via API externa / servidor acadêmico).
* **Embeddings (RAG):** `paraphrase-multilingual-MiniLM-L12-v2` rodando 100% localmente com suporte a GPU (Nvidia CUDA).
* **Vector Store:** `ChromaDB`.

##   Instalação e Configuração

1. **Crie um ambiente virtual e ative-o:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate