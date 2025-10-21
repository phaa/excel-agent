from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from app.utils.json_parser import robust_json_loads
from app.utils.logger import log
from app.state import GraphState
from app.llm import load_llm


SYSTEM = """
  Your task is to *analyze the intent* and *generate a JSON list of actions* needed to perform it.
	Each action MUST be one of the following operations:

	[
	{{
		"action": "add_row",
		"sheet": "Sheet1",
		"values": {{"A": 101, "B": "Novo Cliente", "C": "Ativo"}}
	}},
	{{
		"action": "update_cell",
		"sheet": "Sheet1",
		"row": 5,
		"col": "C",
		"value": "Approved"
	}},
	{{
		"action": "delete_row",
		"sheet": "Sheet1",
		"row": 10
	}},
	{{
		"action": "update_column",
		"sheet": "Sheet1",
		"column": "Status",
		"condition": "Status == 'Atrasado'",
		"new_value": "Pago"
	}},
	{{
		"action": "add_column",
		"sheet": "Sheet1",
		"column_name": "NovaColuna",
		"default_value": null
	}},
	{{
		"action": "delete_column",
		"sheet": "Sheet1",
		"column_name": "Obsoleta"
	}}
	]

	Rules:
	- Always return a **pure JSON array** (no text, comments, or explanations).
	- The `sheet` field is mandatory (default to "Sheet1" if not provided).
	- Prefer using column names instead of indexes when possible.
	- Do not describe what you are doing — only output JSON to be parsed by a JsonOutputParser().
	- The `condition` field uses pandas-style boolean expressions.
	- If the user asks a question (not an edit), respond with a JSON object:
	{{"action": "read", "query": "<natural language interpretation>"}}
	- If no valid action is found, return [] (an empty JSON list).
    
	Context provided to you consist in a dict in which the keys are sheet names and the fields are the metadata about each sheet:
  Fields:
	- Columns: "columns"
	- Data types: "types"
	- First five samples: "samples"
	- Row count: "num_rows"
    
  Here is the spreadsheets available:
  {spreadsheets}
  
	Here is the context for the spreadsheets:
  {metadata}
  """


async def actions_node(state: GraphState) -> GraphState:
    llm = load_llm()
    parser = JsonOutputParser()
    chain = llm | parser
    
    metadata = state.get("metadata", {})
    metadata = {k: v for k, v in metadata.items() if k != "data"} 

    spreadsheets = metadata.keys()
    
    query = None
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            query = msg.content
            break	

    if not query:
        log("actions_node", "No user query found in messages.")
        return {"actions": []} # Evita quebrar o fluxo

    messages = [
        SystemMessage(content=SYSTEM.format(
            spreadsheets=", ".join(spreadsheets),
            metadata=metadata
          )),
        HumanMessage(content=query),
    ]

    try:
        actions = await chain.ainvoke(messages) # already a json
        log("reason_node", f"JSON actions geradas: {actions}")
        return {"actions": actions, "status": "success"}
    
    except Exception as e:
        log("actions_node", str(e))
        return {"actions": [{"action": "error", "message": str(e)}]}