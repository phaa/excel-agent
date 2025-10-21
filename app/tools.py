from datetime import datetime
from langchain_core.tools import tool
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain.agents import ToolNode

from app.llm import load_llm

@tool
def get_datetime_now():
    """"
    Get current date and time when needed. 

    Returns:
        The current date and time in the format yyyy-mm-dd hh:mm:ss
    """
    current_datetime = datetime.now()
    return current_datetime


@tool
def run_pandas_code(code: str, df: dict):
    """
    Execute pandas code on a given DataFrame.

    Parameters:
        code (str): The pandas code to execute.
        df (dict): The DataFrame in dictionary format.

    Returns:
        dict: The resulting DataFrame after executing the code.
    """
    try:
        import pandas as pd
        import numpy as np

        # Convert the input dictionary to a pandas DataFrame
        dataframe = pd.DataFrame(df)

        # Define a safe execution environment
        safe_globals = {
            "pd": pd,
            "np": np,
            "dataframe": dataframe
        }

        # Execute the provided pandas code
        exec(code, safe_globals)

        # Retrieve the modified DataFrame
        result_df = safe_globals.get("dataframe", dataframe)

        # Convert the resulting DataFrame back to a dictionary
        return result_df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

tools = [
	get_datetime_now,
    run_pandas_code,
]

tool_node = ToolNode(tools)