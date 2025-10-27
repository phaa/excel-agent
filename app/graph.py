from langgraph.graph import StateGraph
from app.nodes.execute_node import execute_node
from app.nodes.route_from_start import route_from_start
from app.nodes.start_node import start_node
from app.nodes.reason_node import reason_node
from app.nodes.actions_node import actions_node
from app.nodes.result_node import result_node
from app.state import GraphState
#from app.tools import tool_node

graph = StateGraph(GraphState)
graph.add_node("start", start_node) # Take the user query and decide wether to reason or take actions
graph.add_node("reason", reason_node) # Reason about user intent and generate pandas code
graph.add_node("execute", execute_node) # Execute pandas code node
graph.add_node("action", actions_node) # Generate actions based on user intent
graph.add_node("result", result_node) # Return the result to the user in a friendly format


#graph.add_node("tools", tool_node)

# ---- Conditional Edges ----
graph.add_conditional_edges("start", route_from_start) # decide "reason", "action" or END
graph.add_edge("reason", "execute")
graph.add_edge("execute", "result")
graph.add_edge("action", "result")

# ---- Start ----
graph.set_entry_point("start")

agent = graph.compile()
