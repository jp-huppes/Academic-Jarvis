# Academic JARVIS - AI Agent

O **Academic JARVIS** é um assistente inteligente projetado para auxiliar estudantes no gerenciamento de sua rotina de estudos e na extração de conhecimento de materiais didáticos.

O sistema utiliza um modelo de linguagem (LLM) operando como um **Agente Raciocinador** capaz de acionar ferramentas locais (*Tool Calling*) para manipular calendários, listas de tarefas e realizar buscas semânticas em uma base de dados vetorial (RAG) alimentada por PDFs técnicos da faculdade e livros didáticos de domínio público.

1. Link do video: https://youtu.be/03CtOU_9cgA

2. Link do arquivo usado no video no Docs: https://drive.google.com/file/d/1IA6u3JEIZeixIgAZ3N57Q0tAw8lfxhfN/view?usp=drive_link

---

## 1. Funcionalidades (Tools)

1. **Gestão de Tarefas e Agenda:** Lê, adiciona e concluí compromissos acadêmicos via manipulação de arquivos JSON locais.
2. **Busca Semântica Avançada (RAG):** Vasculha PDFs e resumos técnicos usando um banco de dados vetorial baseado em embeddings multilíngues.
3. **Memória Conversacional:** Mantém o contexto do chat ativo durante a execução das chamadas de ferramentas.

---

## 2. Modelos de IA Utilizados

* **Orquestrador LLM:** `Gemma-3-12b-it` (via API externa / servidor acadêmico), responsável pelo raciocínio lógico e seleção de ferramentas.
* **Embeddings (RAG):** `paraphrase-multilingual-MiniLM-L12-v2` rodando 100% localmente com suporte a aceleração por hardware (Nvidia CUDA).
* **Vector Store:** `ChromaDB` para indexação e persistência dos vetores.

---

## 3. Como Executar o Projeto?

### Pré-requisitos
Certifique-se de ter o **Python 3.10 ou superior** instalado em sua máquina.

### Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/jp-huppes/Academic-Jarvis.git]
   cd Academic-Jarvis

2. **Instale dependências:**
    ```bash
    pip install -r requirements.txt
    
3. **Variaveis**
   Crie um arquivo chamado .env na raiz do projeto e insira a sua credencial de acesso:
   ```bash
      API_KEY = "Sua_Chave_Aqui"

5. **Inicialização**

   Antes de rodar o assistente pela primeira vez, processe os PDFs locais executando o script de ingestão:
      ```bash
      python indexar.py
      ```
   Então, para abrir a interface gráfica web via navegador:
      ```bash
       python -B -m streamlit run app.py
      ```
   Caso queira interagir com o assistente diretamente pelo terminal:
      ```bash
      python main.py
      ```

### Documentação do Dataset

 1. **Origem e Composição dos Dados**
   A pasta /data reúne uma biblioteca técnica com mais de 10 documentos acadêmicos que cobre o núclos de diciplinas do curso. Entre as principais referências indexadas estão:
      - computer_networking_top-down_aproach.pdf (Redes de Computadores - Kurose)
      - Machine_Learning.pdf (Aprendizado de Máquina - Tom Mitchell)
      - algoritmos-teoria-e-partica-thomas-cormen.pdf (Algoritmos - Thomas Cormen)
      - Deep+Learning+Ian+Goodfellow.pdf (Deep Learning - Ian Goodfellow)
      - 2020-Scrum-Guide-Portuguese-European-As_regras_do_jogo.pdf (Metodologias Ágeis)

   Enquanto outros livros e notas de aula cobrem Álgebra Linear, Teoria da Computação e Linguagens de Programação (C++ e Java).

   2. **Tipo de Dados**
      Em sua maioria os arquivos tetuais tem formato em PDF e resumos em TXT.

   3. **Limitações Conhecidas**
      - Restrição Textual: a extração via 'pdfplumber' lê estritamente caracteres de texto plano. Diagramas de arquitetura, imagens de redes, gráficos de funções e tabelas complexas não são indexados na base vetorial.
      - Alinhamento Linguístico: Embora o modelo de embeddings seja multilíngue, os livros base estão em inglês e as requisições do chat ocorrem em português, o que pode gerar pequenas distorções de proximidade semântica em termos técnicos muito específicos.
   
   4. **Estratégia de Chunking (Fragmentação)**
      Para preservar o contexto sem estourar a janela de tokens do modelo de embeddings:
      - Algoritmo: RecursiveCharacterTextSplitter (LangChain), dividindo os textos de forma inteligente ao priorizar quebras de parágrafos e pontos finais.
      - Configuração: Blocos fixos de 1000 caracteres com sobreposição (overlap) de 200 caracteres entre pedaços vizinhos, garantindo a continuidade de sentenças divididas nas bordas.

### Estrutura de Pastas e Arquivos

```text
├── .streamlit/             # Configurações visuais e de tema do Streamlit
├── data/                  # Pasta contendo os PDFs originais do Dataset
│   └── chroma_db/         # [Diretório Local] Banco vetorial gerado pelo indexar.py
├── logs/                  # Histórico local de execuções e tool calls
├── memory/                # Arquivos de persistência de dados 
├── rag/
│   └── pipeline.py        # Arquitetura de busca semântica e recuperação vetorial
├── tools/
│   ├── agenda.py          # Funções de backend para controle do calendário
│   ├── tarefas.py         # Funções de backend para lista de afazeres
│   ├── estudos.py         # Ferramenta de integração com o módulo de RAG
│   └── definitions.py     # Esquemas de declaração JSON para o Tool Calling do modelo
├── app.py                 # Interface gráfica web em Streamlit (Execução Oficial)
├── indexar.py             # Script automatizado de leitura, chunking e indexação
├── requirements.txt       # Relação de bibliotecas e dependências de terceiros
└── README.md              # Documentação principal e instruções de entrega
