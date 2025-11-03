import re
from app.state import GraphState
from app.utils.logger import log
import pandas as pd
import numpy as np


class ExecutorAgent:
    def __init__(self):
        self.safe_globals = {
            "pd": pd,
            "np": np,
        }

    def clean_code(self, code: str) -> str:
        return re.sub(r"```.*?```", lambda m: m.group(0).replace("```python", "").replace("```", ""), code).strip()

    def execute(self, code: str, metadata: dict):
        local_vars = {"metadata": metadata}
        exec(code, self.safe_globals, local_vars)
        return local_vars.get("result", None)

    def format_result(self, result):
        if isinstance(result, pd.DataFrame):
            return {
                "columns": list(result.columns),
                "rows": result.head(10).to_dict(orient="records"),
            }
        elif isinstance(result, (dict, list)):
            return result
        return {"result": str(result)}


def execute_node(state: GraphState) -> GraphState:
    code = state.get("code", "")
    metadata = state.get("metadata", {})

    if not code:
        log("execute_node", "No code to execute.", level="ERROR")
        return {"messages": []}
    
    if not metadata: 
        log("execute_node", "No metadata available for execution.", level="ERROR")
        return {"messages": []}
    
    executor = ExecutorAgent()
    try:
        clean_code = executor.clean_code(code)
        result = executor.execute(clean_code, metadata)
        result_dict = executor.format_result(result)
        log("execute_node", f"Resultado: {result_dict}")


        return {"result": result_dict, "status": "success"}
    
    except Exception as e:
        log("execute_node", f"Error executing code: {e.with_traceback()}", level="ERROR")
        return {"messages": [], "status": "error"} # Evita quebrar o fluxo