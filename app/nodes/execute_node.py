import re
from app.state import GraphState
from app.utils.logger import log


def execute_node(state: GraphState) -> GraphState:
    code = state.get("code", "")
    metadata = state.get("metadata", {})

    #print(metadata["Cert Mileage Forecast - All"].keys())

    if not code:
        log("execute_node", "No code to execute.", level="ERROR")
        return {"messages": []} # Evita quebrar o fluxo
    
    if not metadata: 
        log("execute_node", "No metadata available for execution.", level="ERROR")
        return {"messages": []} # Evita quebrar o fluxo
    
    
    code = re.sub(r"```.*?```", lambda m: m.group(0).replace("```python", "").replace("```", ""), code).strip()

    import pandas as pd
    import numpy as np

    # Define a safe execution environment
    safe_globals = {
        "pd": pd,
        "np": np,
    }
    local_vars = {"metadata": metadata}

    try:
        exec(code, safe_globals, local_vars)
        result = local_vars.get("result", None)

        if isinstance(result, pd.DataFrame):
            result_dict = {
                "columns": list(result.columns),
                "rows": result.head(10).to_dict(orient="records"),
            }
        elif isinstance(result, (dict, list)):
            result_dict = result
        else:
            result_dict = {"result": str(result)}

        log("execute_node", f"Resultado: {result_dict}")

        return {"result": result_dict, "status": "success"}
    
    except Exception as e:
        log("execute_node", f"Error executing code: {e.with_traceback()}", level="ERROR")
        return {"messages": [], "status": "error"} # Evita quebrar o fluxo