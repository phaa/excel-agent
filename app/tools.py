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

tools = [
	get_datetime_now,
]

tool_node = ToolNode(tools)