from tools.agenda import consulte_agenda
from tools.tarefas import liste_tarefas, adicione_tarefas, conclua_tarefa
from tools.logger import registre_log

print("--- INICIANDO TESTES ISOLADOS DAS TOOLS ---")

    #Teste da Agenda
print("\n 1. Testando: consulte_agenda")
data_teste = "2026-05-20"
resultado_agenda = consulte_agenda(data_teste)
registre_log("consulte_agenda",{"data": data_teste},resultado_agenda)
print(f"Eventos para {data_teste}: {resultado_agenda}")

    #Teste de listar tarefas
print("\n 2. Testando: liste_tarefas (pendente)")
resultado_listar = liste_tarefas("pendente")
registre_log("liste_tarefas", {"status": "pendente"}, resultado_listar)
print(f"Encontradas {len(resultado_listar)} tarefas pendentes.")

    #Teste de adicionar tarefa
print("\n 3. Testando: adicione_tarefa")
desc = "Estudar sistema de Tool Calling"
prazo = "2026-05-25"
resultado_add = adicione_tarefas(desc, prazo)
registre_log("adicione_tarefas", {"descricao": desc, "prazo": prazo}, resultado_add)
print(f"Tarefa criada: {resultado_add}")

    #Testar conclusao da tarefa recém-criada
print("\n 4. Testando: conclua_tarefa")
if "id" in resultado_add:
    id_nova_tarefa = resultado_add["id"]
    resultado_concluir = conclua_tarefa(id_nova_tarefa)
    registre_log("conclua_tarefa", {"id": id_nova_tarefa}, resultado_concluir)
    print(f"Status atualizado: {resultado_concluir}")
else:
    print("Erro: A tarefa não foi criada corretamente para ser concluida.\n")

print("\n--- TESTES FINALIZADOS ---")