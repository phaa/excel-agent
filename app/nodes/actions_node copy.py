import os
import shutil
import asyncio

#from app.utils.excel import apply_actions
from app.utils.logger import log
from app.state import GraphState


async def actions_node(state: GraphState) -> GraphState:
    """
    Executa ações sobre a planilha com segurança, sem travar o loop async.
    """

    file_path = state.get("file_path")
    actions = state.get("actions", [])
    print(actions)

    if not file_path or not os.path.exists(file_path):
        log("action_node", "Arquivo Excel não encontrado.")
        return {
            "status": "error",
            "message": "Arquivo não encontrado."
        }

    # Criar backup
    backup_path = file_path + ".bak"
    #shutil.copy(file_path, backup_path)
    #log("action_node", f"Backup criado em {backup_path}")

    try:
        if actions:
            #loop = asyncio.get_event_loop()
            #await loop.run_in_executor(None, apply_actions, file_path, actions)
            log("action_node", f"{len(actions)} ações aplicadas com sucesso.")
            return {
                "status": "success",
                "message": f"{len(actions)} ações executadas.",
                "backup": backup_path
            }
        else:
            log("action_node", "Nenhuma ação recebida para execução.")
            return {
                "status": "noop",
                "message": "Nenhuma ação executada."
            }

    except Exception as e:
        # Rollback
        #shutil.copy(backup_path, file_path)
        log("action_node_error", f"Falha ao aplicar ações. Rollback executado: {e}")
        return {
            "status": "error",
            "message": str(e),
            "rolled_back": True
        }