from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from app.llm import load_llm
from app.utils.logger import log
from app.state import GraphState

SYSTEM = """
You are an expert AI assistant specialized in interacting with users about spreadsheet operations.
- You must provide a clear and concise final message to the user based on the status of their request.
- If the status is 'error', apologize and explain that you cannot process their request.
- If the status is 'success', confirm that their request was processed successfully.
- If the status is 'noop', inform them that no changes were necessary.
- Do not include any technical details or internal states in your message.
- Keep the message friendly and professional.

Query made by the user: {query}

Status of the operation: {status}

Actions taken (if any): {actions}

Result of the operation (if any): {result}
"""

async def result_node(state: GraphState) -> GraphState:
    """
    Generate a final message based on the status and actions taken.
    """

    llm = load_llm()
    
    # May have actions or results depending on the previous nodes
    actions = state.get("actions", [])
    result = state.get("result", None)
    status = state.get("status")
    
    query = None
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            query = msg.content
            break

    if status == "success":
        message = f"Consulta '{query}' processada com sucesso. {len(actions)} alterações aplicadas."
    elif status == "noop":
        message = f"Consulta '{query}' não exigiu alterações."
    elif status == "error":
        message = f"Sinto muito, mas eu não posso processar o que voce pediu."
    else:
        message = "Resultado indefinido."

    log("result_node", message, level="ERROR" if status == "error" else "INFO")

    print(query)

    if actions: 
        print("actions")
        return {"messages": [AIMessage(content=actions)]}
    
    elif result: # return friendly message explaining the result from the executed pandas code
        print("result")
        # Filter only HumanMessage and AIMessage for the final conversation
        # Avoid technical details in the final message
        conversation = [
            msg for msg in state.get("messages", []) 
            if isinstance(msg, (HumanMessage, AIMessage))
        ]
        
        msgs = [SystemMessage(content=SYSTEM.format(
            query=query,
            status=status,
            actions=actions,
            result=result
        ))]
        msgs += conversation

        ai: AIMessage = await llm.ainvoke(msgs)
        return {"messages": [ai]}
