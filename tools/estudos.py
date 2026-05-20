import os 
from rag.pipeline import PipelineRAG

_instancia_rag = PipelineRAG()

def busque_material_rag(query:str)->list[str]:
    """
    Busca trechos relevantes em arquivos PDF e TXT. Usa de busca semântica (RAG)
    In: Query -> uma pergunta, um termo de busca
    Out: Lista de parágrafos relacionados encontrados nos materiais didáticos
    """
    try:
        parts = _instancia_rag.busque_trechos_relevantes(query, top_k=3)

        if not parts:
            return [f"Nenhum trecho relevante foi encontrado nos materiais de estudo para: '{query}'."]
        return parts
    except Exception as e:
        return [f"Erro interno ao consultar o banco de dados: {e}"]
    
    