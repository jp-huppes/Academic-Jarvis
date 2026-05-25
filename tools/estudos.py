import os 
from rag.pipeline import PipelineRAG

_instancia_rag = None

def busque_material_rag(query: str) -> list[str]:
    """
    Busca trechos relevantes em arquivos PDF e TXT usando busca semântica (RAG).
    """
    global _instancia_rag

    if _instancia_rag is None:
        try:
            print("   [RAG] Inicializando banco de dados vetorial de forma isolada...")
            _instancia_rag = PipelineRAG(device="cpu")
        except Exception as e:
            return [f"Erro ao carregar o modelo ou banco de dados: {e}"]

    try:
        # Busca no ChromaDB
        parts = _instancia_rag.busque_trechos_relevantes(query, top_k=5)

        # Se o banco de dados retornar vazio para o termo
        if not parts:
            return [
                f"Aviso do Banco de Dados: O termo '{query}' não retornou fragmentos diretos nos livros locais.\n"
                "Por favor, responda o aluno usando seu conhecimento geral (explicando o conceito de forma clara), "
                "mas avise de maneira amigável que esse termo exato não consta explicitamente nos PDFs da pasta 'data'."
            ]
            
        return parts
        
    except Exception as e:
        return [f"Erro interno ao consultar o banco de dados vetorial: {e}"]