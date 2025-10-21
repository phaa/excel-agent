from langchain_core.messages import AIMessage, SystemMessage
from app.utils.logger import log
from app.state import GraphState
from app.llm import load_llm


SYSTEM = """
You are an expert AI assistant specialized in manipulating spreadsheet data.

The user provides a natural language instructions.
- You must verify if the user is asking for information or requesting an edit.
- You must verify if the user is providing the name of a specific spreadsheet to work on.
- Do not describe what you are doing — only output a single string.
- If the user is asking for information, return a single string "information".
- If the user is requesting an edit, return a single string "edit".
- If the user is asking for something that cannot be found in our spreadsheets, return "unknown_subject".
- If the user is asking for something that is not possible to do with spreadsheets, return "unknown_action".
- If the user did not provide the name of a specific spreadsheet, return "unknown_sheetname".
"""

async def start_node(state: GraphState) -> GraphState:
    llm = load_llm()
    msgs = [SystemMessage(content=SYSTEM)]
    msgs += state.get("messages") # Add initial user messages

    ai: AIMessage = await llm.ainvoke(msgs)
    ai_response = ai.content.strip().lower()

    if ai_response.startswith("unknown_"):
        # Immediately redirect to result_node with error status
        status_msg = ""
        match ai_response:
            case "unknown_subject":
                status_msg = "User query is not related to spreadsheets"
            case "unknown_action":
                status_msg = "User requested an action that is not possible with spreadsheets"
            case "unknown_sheetname":   
                status_msg = "User did not provide a valid spreadsheet name"
            case _:
                status_msg = "Unrecognized error"

        log("start_node", status_msg, level="ERROR")
        return {
            "status": "error", 
            "status_msg": status_msg
        } 

    return {"subject": ai_response}

    