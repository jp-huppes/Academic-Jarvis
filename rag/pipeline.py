import os
import pdfplumber
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


CAMINHO_DATA = "data"
CAMINHO_CHROMA = "data/chroma_db"

class PipelineRAG:
    def __init__(self, device: str = None):
            #incialização do modelo de embeddigs
        if device is not None: 
            self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device=device)        
        else:
            try:
                self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cuda")
            except Exception:
                self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
         

            # incialização do banco vetorial persistente
        self.chroma_client = chromadb.PersistentClient(path=CAMINHO_CHROMA)
        self.collection = self.chroma_client.get_or_create_collection(name="materiais_estudo")
    
            #configurador de corte de texto
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1200, chunk_overlap = 250,separators=["\n\n", "\n", " ", ""],length_function=len)

    def extraia_txt_pdf(self, pdf_path: str) -> str:
        "Abre PDF e extrai todo texto legível dele"
        full_txt = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for pag in pdf.pages:
                    txt_pag = pag.extract_text()
                    if txt_pag:
                        full_txt.append(txt_pag)
        except Exception as e:
            print(f"  Erro ao ler PDF {pdf_path}: {e}")
        return "\n".join(full_txt)
    
    def inicialize_banco_vetorial(self):
        "Varre a pasta data/, então processa os arquivos novos e indexa no banco!"
        if not os.path.exists(CAMINHO_DATA):
            print("  Pasta 'data' nao encontrada.")
            return
        archives = [
            f
            for f in os.listdir(CAMINHO_DATA)
            if f.endswith(".pdf") or f.endswith(".txt")
        ]

        if not archives:
            print("  Nenhum arquivo PDF ou TXT encontrado para indexar.")
            return

        print(
            f" Foram encontrados {len(archives)} arquivos para processar no RAG.\n"
        )

        existing_ids = (
            set(self.collection.get()["ids"])
            if self.collection.count() > 0
            else set()
        )

        new_ids = []
        new_chunks = []
        new_metadata = []

        for idx, arch in enumerate(archives):
            full_path = os.path.join(CAMINHO_DATA, arch)

            if arch.endswith(".pdf"):
                txt = self.extraia_txt_pdf(full_path)
            else:
                with open(full_path, "r", encoding="utf-8") as file:
                    txt = file.read()

            if not txt.strip():
                continue
            chunks_list = self.text_splitter.split_text(txt)


            theoretical_ids = [f"{arch}_chunk_{i}" for i in range(len(chunks_list))]
            existing_data = self.collection.get(ids=theoretical_ids)
            registered_ids = set(existing_data["ids"]) if existing_data else set()

            new_chunks_arch = 0 

            for i, chunk in enumerate(chunks_list):
                chunk_id = theoretical_ids[i]     

                if chunk_id not in registered_ids:
                    new_chunks.append(chunk)
                    new_metadata.append({"fonte": arch, "fragmento": i})
                    new_ids.append(chunk_id)
                    new_chunks_arch += 1

            if new_chunks_arch > 0:
                print(f"  [{idx+1}/{len(archives)}] '{arch}' → {new_chunks_arch} novos fragmentos.")

        if new_chunks:
            print(
                f"\n  Gerando Embeddings para {len(new_chunks)} novos fragmentos...\nAguarde, isso pode levar alguns minutos de processamento..."
            )
            new_embeddings = self.model.encode(new_chunks).tolist()
            print("  Adicionando os novos registros ao ChromaDB em lotes...")
        
            tamanho_lote = 4000
            total_fragmentos = len(new_chunks)
            
            for i in range(0, total_fragmentos, tamanho_lote):
                fim = min(i + tamanho_lote, total_fragmentos)
                print(f"    -> Enviando lote: fragmentos {i} até {fim}...")
                
                self.collection.add(
                    documents=new_chunks[i:fim],
                    embeddings=new_embeddings[i:fim],
                    metadatas=new_metadata[i:fim],
                    ids=new_ids[i:fim],
                )
            print("  Banco de dados updated com sucesso!")
        else:
            print(
                "\n  Todos os arquivos já estão indexados no ChromaDB. Nenhuma duplicidade detectada!"
            )
    def busque_trechos_relevantes(self, query: str, top_k: int = 3) -> list:
        """Realiza busca semântica usando os vetores do modelo."""
        
        # força o encode a gerar o vetor da string de forma direta
        embedding_bruto = self.model.encode(query)
        
        # convertemos para uma lista Python nativa e achatamos completamente . garante que seja uma lista simples de floats unidimensional, n importa o que aconteça
        import numpy as np
        if isinstance(embedding_bruto, np.ndarray):
            query_embedding = embedding_bruto.flatten().tolist()
        else:
            query_embedding = np.array(embedding_bruto).flatten().tolist()

        # passamos o vetor limpo e envelopado em apenas UM nivel de lista externa exigido pelo ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        formatted_sections = []
        
        if results and results['documents'] and results['documents'][0]:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            distances = results['distances'][0]

            for doc, meta, dist in zip(docs, metas, distances):
            
            fonte = meta.get('fonte', meta.get('arquivo', 'Livro Local'))
            formatted_sections.append(f"[Origem: {fonte}]\n{doc}")
                    
        return formatted_sections
