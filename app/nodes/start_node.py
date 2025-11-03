from langchain_core.messages import AIMessage, SystemMessage
from app.utils.logger import log
from app.state import GraphState
from app.llm import load_llm


SYSTEM = """
You are an expert AI assistant specialized in understanding and manipulating spreadsheet data.

Your task is to classify the user's natural language instruction into one of several possible intents.
Follow these rules carefully:

1. **Jailbreak or unrelated request**
   - If the user attempts to make you perform actions outside spreadsheet operations 
     (e.g., code execution, web access, or unrelated tasks), respond with:
     `"unknown_subject"`.

2. **Information request**
   - If the user is asking to *view*, *read*, or *analyze* spreadsheet data (not modify it), respond with:
     `"information"`.

3. **Edit request**
   - If the user wants to *add*, *update*, *delete*, or otherwise *modify* spreadsheet data, respond with:
     `"edit"`.

4. **Unknown subject**
   - If the user's request refers to something that does not exist in the available spreadsheets, respond with:
     `"unknown_subject"`.

5. **Unknown action**
   - If the request is not something that can logically be done with spreadsheets, respond with:
     `"unknown_action"`.

6. **Missing sheet name**
   - If the user refers to an operation but does not specify which spreadsheet to use, respond with:
     `"unknown_sheetname"`.

**Output format rules:**
- Return only a **single lowercase string** (no explanations, punctuation, or extra text).
- Do not include quotes, markdown, or any other formatting.

Your only valid responses are one of the following strings:
`information`, `edit`, `unknown_subject`, `unknown_action`, `unknown_sheetname`.
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

    