import time
import sys
from rag.pipeline import PipelineRAG

def rodar_indexacao_pura():
    print("=" * 60)
    print("🚀 INICIANDO PROCESSO DE INDEXAÇÃO DO JARVIS (RAG)")
    print("=" * 60)
    print("🤖 Carregando modelo de IA e preparando o ChromaDB...\n")
    
    # Marca o tempo inicial para sabermos quanto tempo levou
    tempo_inicio = time.time()
    
    try:
        # Inicializa o Pipeline (configura o tamanho do chunk corrigido para 1200)
        pipeline = PipelineRAG()
        
        # Roda a função de varredura e alimentação do banco
        pipeline.inicialize_banco_vetorial()
        
        # Calcula o tempo total gasto
        tempo_fim = time.time()
        tempo_total = tempo_fim - tempo_inicio
        
        print("\n" + "=" * 60)
        print("✅ BANCO DE VETORES ATUALIZADO COM SUCESSO!")
        print(f"⏱️ Tempo total de processamento: {tempo_total:.2f} segundos ({tempo_total/60:.2f} minutos).")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Ocorreu um erro crítico durante a indexação: {e}", file=sys.stderr)
        print("=" * 60)

if __name__ == "__main__":
    rodar_indexacao_pura()