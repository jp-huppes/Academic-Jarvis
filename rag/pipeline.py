import os
import pdfplumber
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

CAMINHO_DATA = "data"
CAMINHO_CHROMA = "data/chroma_db"

class PipelineRAG:
    def __init__(self):
            #incialização do modelo de embeddigs
        try: 
            self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cuda")
        except Exception:
            self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")

            # incialização do banco vetorial persistente
        self.chroma_client = chromadb.PersistentClient(path=CAMINHO_CHROMA)
        self.collection = self.chroma_client.get_or_create_collection(name="materiais_estudo")
    
            #configurador de corte de texto
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50,length_function=len)

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
        return "/n".join(full_txt)
    
    def inicialize_banco_vetorial(self):
        "Varre a pasta data/, então processa os arquivos novos e indexa no banco!"
        if not os.path.exists(CAMINHO_DATA):
            print("  Pasta 'data' nao encontrada")
            return
        archives = [f for f in os.listdir(CAMINHO_DATA) if f.endswith(".pdf") or f.endswith(".txt")]

        if not archives:
            print("  Nenhum arquivo PDF ou TXT encontrado para indexar")
        print(f" Foram encontrados {len(archives)} arquivos para processar no RAG\n")

        total_chunks = [];total_metadata = []; total_ids = []
        id_count = 0

        for idx, arch in enumerate(archives):
            full_path = os.path.join(CAMINHO_DATA, arch)

            if arch.endswith(".pdf"):
                txt = self.extraia_txt_pdf(full_path)
            else:
                with open(full_path,"r",encoding="utf-8") as file:
                    txt = file.read()
            
            if not txt.strip():
                continue
        
            #Corte -> Chunks do txt
            chunks = self.text_splitter.split_text(txt)
            print(f"  [{idx+1}/{len(archives)}] Processando '{arch}'-> Gerados {len(chunks)} chunks...")    
            
            for i, chunks in enumerate(chunks):
                total_chunks.append(chunks)
                total_metadata.append({
                    "fonte":arch, 
                    "fragmento":i
                })
                total_ids.append(f"doc_{idx}_chunk_{i}_{id_count}");id_count += 1

        if total_chunks:
            print("  Gerando Embeddings e salvando no ChromaDB\nAgurde, isso pode levar alguns segundos....")

            embeddings = self.model.encode(total_chunks).tolist()
            self.collection.add(
                documents= total_chunks,
                embeddings= embeddings,
                metadatas=total_metadata,
                ids= total_ids
            )
            print("  Banco vetorial RAG incializado e atualizado com sucesso!")
        else:
            print("  Nenhum chunk novo extraido...")
    
    def busque_trechos_relevantes(self,query: str, top_k: int = 3) -> list:
        "Realiza busca semantica usando vetores."
        query_embedding = self.model.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        formatted_sections = []
        if results and results['documents']:
            #extraimos os documentos e os metadados retornados pelo Chroma
            docs = results['documents'][0]
            metas = results['metadatas'][0]

            for doc, meta in zip(docs, metas):
                formatted_sections.append(f"[Origem: {meta['fonte']}]\n{doc}")
                
        return formatted_sections