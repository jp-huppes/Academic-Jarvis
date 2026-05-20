from rag.pipeline import PipelineRAG

if __name__ == "__main__":
    rag = PipelineRAG()
    rag.inicialize_banco_vetorial()

    print("\n  Testando busca por significado")
    resultado = rag.busque_trechos_relevantes("O que é uma fila de prioridade?")
    for r in resultado:
        print(f"\n{r}\n" + "-"*40)
