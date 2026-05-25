import json
from openai import OpenAI
import openai
import os 
import re 
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from tools.agenda import consulte_agenda, consulte_semana
from tools.tarefas import liste_tarefas, adicione_tarefas, conclua_tarefa
from tools.logger import registre_log
from tools.definitions import DADOS_DAS_FERRAMENTAS
from tools.estudos import busque_material_rag

MAPEADOR_DE_TOOLS = {
    "consulte_agenda": consulte_agenda,
    "consulte_semana": consulte_semana,
    "liste_tarefas": liste_tarefas,
    "adicione_tarefas": adicione_tarefas,
    "conclua_tarefa": conclua_tarefa,
    "busque_material_rag": busque_material_rag 
}

chave = os.getenv("API_KEY")

hoje_str = datetime.now().strftime("%A, %d de %B de %Y")
hoje_date = datetime.now().date()

if not chave:
    print("ERRO: A chave não foi encontrada no arquivo .env")
    exit(1)

client = OpenAI(
    base_url='https://llm.liaufms.org/v1/gemma-3-12b-it',  
    api_key=chave
)

INSTRUCOES = (
    f"Você é o Academic JARVIS, um assistente inteligente acadêmico de alta performance. "
    f"ÂNCORA TEMPORAL CRÍTICA: Hoje é estritamente {hoje_str}.\n"
    "Qualquer menção a 'hoje', 'amanhã', 'ontem', 'essa semana' ou 'próximos dias' deve ser calculada "
    f"tendo como base FIXA e IMUTÁVEL o dia {hoje_str}. Não mude sua referência temporal ao longo da conversa.\n\n"
    
    "Você tem acesso a ferramentas locais para gerenciar a agenda, tarefas e buscar materiais de estudo (RAG).\n\n"
    
    f"FERRAMENTAS DISPONÍVEIS:\n{json.dumps(DADOS_DAS_FERRAMENTAS, indent=2, ensure_ascii=False)}\n\n"
    
    "REGRAS DE FORMATAÇÃO E TOMADA DE DECISÃO:\n"
    "1. Se a pergunta do usuário exigir dados que você não possui (como o conteúdo da agenda, tarefas ou PDFs), "
    "você deve obrigatoriamente chamar a ferramenta adequada.\n"
    "2. Para chamar uma ferramenta, responda EXCLUSIVAMENTE com o JSON puro estruturado.\n"
    '   Exemplo: {"nome_ferramenta": "liste_tarefas", "argumentos": {"status": "pendente"}}\n'
    "3. Se o usuário pedir para concluir/alterar uma tarefa e NÃO fornecer um ID, NÃO pare a conversa para perguntar. "
    "Extraia o assunto principal do pedido e chame a ferramenta 'conclua_tarefa' usando o argumento 'termo_busca'.\n"
    "4. Se o histórico já contém os resultados das ferramentas necessários para responder o usuário, "
    "NÃO chame a ferramenta de novo. Formule a resposta final diretamente em prosa de forma clara e amigável."
)

def iniciar_chat():
    historico = [{"role": "system", "content": INSTRUCOES}]

    print("="*60)
    print("   JARVIS Online!")
    
    # COMPORTAMENTO PROATIVO: Aviso de Prazos Próximos
    try:
        tarefas_pendentes = liste_tarefas("pendente")
        if tarefas_pendentes:
            tarefas_criticas = [
                t for t in tarefas_pendentes
                if 0 <= (datetime.strptime(t["prazo"], "%Y-%m-%d").date() - hoje_date).days <= 2
            ]
            if tarefas_criticas:
                print("\n     [ALERTA DO SISTEMA: PRAZOS PRÓXIMOS]")
                for t in tarefas_criticas:
                    print(f"     • ID {t['id']}: '{t.get('titulo', t.get('descricao', 'Sem título'))}' (Prazo: {t['prazo']})")
                print("="*60)
    except Exception as e:
        print(f"  [Falha silenciosa ao checar prazos: {e}]")

    print("   Comandos especiais: \n   'sair': encerrar\n   'limpar': zerar a memória")
    
    while True:
        try:
            user_message = input("\nUser: ").strip()
            if not user_message:
                continue
            if user_message.lower() in ['sair','exit','quit']:
                print("   JARVIS: Desconectando dos sistemas da UFMS. Até a próxima!")
                break
            if user_message.lower() in ['limpar','clear']:
                os.system('cls' if os.name == 'nt' else 'clear')      
                historico = [{"role": "system", "content": INSTRUCOES}]
                print("   JARVIS: Memória do contexto da conversa redefinida.")
                continue
            
            historico.append({'role':'user','content':user_message})
            print("   JARVIS pensando...")

            max_work = 5
            for work in range(max_work):
                try:
                    resposta = client.chat.completions.create(
                        model='google/gemma-3-12b-it',
                        messages=historico
                    )

                    resposta_ai = resposta.choices[0].message.content

                    # Captura robusta: Procura um padrão JSON {...} independente do texto ao redor
                    match_json = re.search(r'\{.*\}', resposta_ai, re.DOTALL)
                    
                    if match_json:
                        try:
                            texto_json = match_json.group(0).strip()
                            tool_call = json.loads(texto_json)
                            
                            if isinstance(tool_call, dict) and "nome_ferramenta" in tool_call:
                                nome_func = tool_call["nome_ferramenta"]
                                args = tool_call.get("argumentos", {})
                                
                                # Se a IA pensou alto antes do JSON, exibe o pensamento dela
                                preambulo = resposta_ai.split('{')[0].strip()
                                if preambulo:
                                    print(f"\n   JARVIS (Pensamento): {preambulo}")
                                
                                print(f"    [Executando Tool: {nome_func} com args {args}]")

                                if nome_func in MAPEADOR_DE_TOOLS:
                                    tool_result = MAPEADOR_DE_TOOLS[nome_func](**args)
                                    registre_log(nome_func, args, tool_result)

                                    historico.append({"role": "assistant", "content": resposta_ai})
                                    historico.append({
                                        "role": "user",
                                        "content": f"Resultado da ferramenta {nome_func}: {json.dumps(tool_result, ensure_ascii=False)}."
                                    })
                                    continue
                                else:
                                    print(f"   JARVIS tentou chamar uma ferramenta desconhecida: {nome_func}")
                                    break
                        except json.JSONDecodeError:
                            # Se falhar o parse do Regex, trata como texto comum de segurança
                            pass

                    # Se não encontrou JSON válido ou se o processamento caiu aqui, é resposta final em prosa
                    print(f"\n   JARVIS: {resposta_ai}")
                    historico.append({"role": "assistant", "content": resposta_ai})
                    break

                except openai.APIConnectionError:
                    print("   Erro de Rede: Não foi possível conectar à API.")
                    break
                except openai.AuthenticationError:
                    print("   Erro de Autenticação: Sua chave no arquivo parece inválida.")
                    break
                except Exception as e:
                    print(f"   Erro Inesperado no agente: {e}")
                    registre_log("erro_sistema", {}, str(e))
                    break

        except KeyboardInterrupt:
            print("\n   JARVIS: Interrupção detectada. Encerrando sessão com segurança.")
            break

if __name__ == "__main__":
    iniciar_chat()