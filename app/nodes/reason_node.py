import re
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from app.utils.logger import log
from app.state import GraphState
from app.llm import load_llm


SYSTEM = """
You are a wizard writing Pandas code.

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

The user wants:
{query}

Generate **only** Python code that uses a DataFrame.
This dataframe is already loaded in the metadata.
You can access the dataframe through metadata['SheetName']['data'].
SheetName is the name of the spreadsheet mentioned by the user in the query.
The downstream code executor is expecting a dataframe named df.
The result must be saved in the variable `result`.
Se a operacao permitir tente conservar o BuildID do veículo ao longo da operacao.
Caso nao seja possivel, ignore este requisito. 

Don't print anything, don't read files.
"""

async def reason_node(state: GraphState) -> GraphState:
    llm = load_llm()

    metadata = state.get("metadata", {})
    metadata = {k: v for k, v in metadata.items() if k != "data"}  
    spreadsheets = metadata.keys()
    
    query = None
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            query = msg.content
            break	

    if not query:
        log("reason_node", "No user query found in messages.", level="ERROR")
        return {"messages": []} # Evita quebrar o fluxo

    messages = [
        SystemMessage(content=SYSTEM.format(
            metadata=metadata,
            spreadsheets=", ".join(spreadsheets),
            query=query
          )),
        HumanMessage(content=query),
    ]

    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()

        # Extrai o código puro do markdown
        code = re.search(r"```python(.*?)```", content, re.S)
        if code:
            code = code.group(1).strip()
        else:
            code = content

        log("reason_node", f"Código gerado: {code}")
        return {"code": code}
    
    except Exception as e:
        log("reason_node_error", str(e))
        return {"messages": state.get("messages", [])}
