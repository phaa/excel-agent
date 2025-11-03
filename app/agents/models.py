# app/agents/models.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal, List

ActionName = Literal[
    "add_row", "update_cell", "delete_row",
    "update_column", "add_column", "delete_column", "read"
]

class Action(BaseModel):
    action: ActionName
    sheet: str = Field(..., description="Nome da planilha (sheet).")
    # Campos opcionais que dependem do tipo de ação
    row: Optional[int] = None
    col: Optional[str] = None
    column: Optional[str] = None
    column_name: Optional[str] = None
    values: Optional[Dict[str, Any]] = None
    condition: Optional[str] = None
    new_value: Optional[Any] = None
    # extras permitidos (por segurança, Pydantic rejeita campos indevidos)
    class Config:
        extra = "forbid"

class ActionsList(BaseModel):
    actions: List[Action]
