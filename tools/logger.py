import json
import os
from datetime import datetime

CAMINHO_LOGS = os.path.join("logs","tool_calls.jsonl")

def registre_log(tool_name: str, inputs: dict, output: any):
    """
    Registra chamada de ferramenta em um arquivo JSONL.
        In: nome da ferramenta usada
            dicionário com os parâmetros enviados para a ferramenta
            retorno da ferramenta [sucesso,erro]
    """
    register = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "input": inputs,
        "output": output
    }

    try:
        with open(CAMINHO_LOGS, "a", encoding="utf-8") as file:
            file.write(json.dumps(register,ensure_ascii=False)+ "\n")
    except Exception as e:
        print(f"Erro ao salvar log: {e}")