import json
from openai import OpenAI
import openai
import os 
from dotenv import load_dotenv


from tools.agenda import consulte_agenda
from tools.tarefas import liste_tarefas, adicione_tarefas, conclua_tarefa
from tools.logger import registre_log
from tools.definitions import DADOS_DAS_FERRAMENTAS
from tools.estudos import busque_material_rag

load_dotenv()
# Associamos o texto enviado pela IA com a função real do Python
MAPEADOR_DE_TOOLS = {
    "consulte_agenda": consulte_agenda,
    "liste_tarefas": liste_tarefas,
    "adicione_tarefas": adicione_tarefas,
    "conclua_tarefa": conclua_tarefa,
    "buscar_material_rag": busque_material_rag
}
chave = os.getenv("API_KEY")
client = OpenAI(
    base_url='https://llm.liaufms.org/v1/gemma-3-12b-it',  
    api_key = chave
)

def execute_orquestrador(user_message: str):
    print(f"\n   Usuário: {user_message}")
    
    instrucoes_sistema = (
        "Você é o Academic JARVIS, um assistente inteligente. Hoje é terça-feira, 19 de maio de 2026.\n"
        "Você tem acesso a ferramentas locais para gerenciar a agenda, tarefas e pesquisar materiais de estudo do estudante.\n\n"
        "DIRETRIZ DE ESTUDOS: Sempre que o usuário fizer uma pergunta teórica sobre conceitos, algoritmos ou definições acadêmicas, "
        "você DEVE obrigatoriamente chamar a ferramenta 'consulte_material' para fundamentar sua resposta nos documentos locais.\n\n"
        "REGRA CRÍTICA: Se a pergunta do usuário exigir o uso de uma ferramenta, você DEVE responder EXCLUSIVAMENTE "
        "com um bloco JSON no seguinte formato (e absolutamente nada mais de texto):\n"
        "```json\n"
        '{"action": "NOME_DA_FUNCAO", "parameters": {"NOME_DO_PARAMETRO": "VALOR"}}\n'
        "```\n\n"
        f"As ferramentas disponíveis e seus respectivos schemas são:\n{json.dumps(DADOS_DAS_FERRAMENTAS, ensure_ascii=False, indent=2)}\n\n"
        "Se o usuário fizer uma saudação ou uma pergunta que não necessite de ferramentas, responda normalmente em português conversacional."
    )
    
    message = [
        {"role": "system", "content": instrucoes_sistema},
        {"role": "user", "content": user_message}
    ]
    
    try:
        print("   JARVIS pensando...")
        answer = client.chat.completions.create(
            model='google/gemma-3-12b-it',
            messages=message
        )
        ai_response = answer.choices[0].message.content.strip()

        if "{" in ai_response and "action" in ai_response:
            # BLOCO A: Trata estritamente o Parseamento do JSON gerado pela IA
            try:
                raw_json = ai_response
                if "```json" in raw_json:
                    raw_json = raw_json.split("```json")[1].split("```")[0]
                elif "```" in raw_json:
                    raw_json = raw_json.split("```")[1].split("```")[0]
                
                call = json.loads(raw_json.strip())
                function_name = call.get("action")
                arguments = call.get("parameters", {})
            except Exception as parse_error:
                print(f"      [Erro de Parseamento] Falha ao ler o JSON gerado pela IA: {parse_error}")
                print(f"   JARVIS bruto: {ai_response}")
                return

            print(f"      [Prompt Tool Calling] JARVIS usou: {function_name} com argumentos: {arguments}")

            # BLOCO B: Executa a função Python local de maneira isolada
            try:
                if function_name in MAPEADOR_DE_TOOLS:
                    real_function = MAPEADOR_DE_TOOLS[function_name]
                    
                    tool_results = real_function(**arguments)
                    registre_log(function_name, arguments, tool_results)

                    message.append({"role": "assistant", "content": ai_response})
                    message.append({
                        "role": "user", 
                        "content": f"Resultado retornado pela ferramenta {function_name}: {json.dumps(tool_results, ensure_ascii=False)}. Com base nisso, formule a resposta final para o estudante."
                    })

                    final_answer = client.chat.completions.create(
                        model='google/gemma-3-12b-it',
                        messages=message
                    )
                    print(f"      JARVIS: {final_answer.choices[0].message.content}")
                    return
            except Exception as tool_error:
                print(f"      [Erro de Execução] Erro interno dentro da função '{function_name}': {tool_error}")
                return

        # Caso não seja uma chamada de ferramenta, exibe o texto corrido da IA
        print(f"      JARVIS: {ai_response}")

    except openai.InternalServerError:
        print("      Erro: O servidor da universidade está instável. Tente novamente em alguns segundos.")
    except Exception as e:
        print(f"      Erro inesperado: {e}")

if __name__ == "__main__":

    # Executa a bateria de testes reais do Passo 2.3

    #execute_orquestrador("Quais tarefas eu tenho pendentes?")
    #execute_orquestrador("O que eu tenho para fazer no dia 2026-05-20?")
    #execute_orquestrador("Adicione uma tarefa chamada Estudar Ba
    #execute_orquestrador("Estou estudando IA. O que o material diz sobre o algoritmo A* (A-estrela)?")
    #execute_orquestrador("O que o nosso material de IA diz sobre a Busca Cega?")
    #execute_orquestrador("Me diga o que há nos arquivos sobre Embeddings.")
    execute_orquestrador("Explique o que o nosso material diz sobre regressão logística.")
    execute_orquestrador("Quais são as três implementações possíveis para uma fila de prioridades?")
