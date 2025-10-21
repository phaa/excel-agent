from langgraph.graph import END
from app.utils.logger import log
from app.state import GraphState


def route_from_start(state: GraphState):
    """"
    Decide the next node based on the subject identified in the start_node.
    """
    
    if state.get("status") == "error":
        log("route_from_start", "Unable to proceed", level="ERROR")
        return "result"  # If there was an error in start_node, go immediately to result_node

    match state.get("subject"):
        case "edit":
            log("route_from_start", "Selected route: action")
            return "action"
        case "information":
            log("route_from_start", "Selected route: reason")
            return "reason"
        case _:
            return END