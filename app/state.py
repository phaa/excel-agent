from langgraph.graph import StateGraph, MessagesState
from typing import Any, Dict, List, Optional, TypedDict
import pandas as pd


class GraphState(MessagesState, total=False):
    """
    Estado do agente LangGraph + Excel (versão 1.0 alpha compatível).
    Combina o controle de mensagens do MessagesState com campos customizados.
    """
    
    file_path: str
    metadata: Optional[Dict[str, Dict[str, Any]]]
    
    # Start node
    subject: Optional[str] # assunto principal (informação ou edição)

    # Actions node
    actions: Optional[List[Dict[str, Any]]]

    # Reason node
    code: Optional[str]

    # Result node
    status: Optional[str]
    status_msg: Optional[str]
