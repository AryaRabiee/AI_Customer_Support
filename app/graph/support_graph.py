from langgraph.graph import StateGraph, START, END
from graph.state import SupportState
from agents.supervisor import supervisor_node
from agents.rag_agent import rag_node
from agents.chat_agent import chat_node
from agents.db_agent import extract_data

graph = StateGraph(SupportState)

graph.add_node("supervisor", supervisor_node)
graph.add_node("rag", rag_node)
graph.add_node("chat" , chat_node)
graph.add_node("database" , extract_data)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"],
    {
        "rag": "rag",
        "chat":"chat",
        "database":"database"
    }
)
graph.add_edge("rag", END)
graph.add_edge("chat" , END)
graph.add_edge("database" , END)
app = graph.compile()

def run_support_agent(user_message: str):
    print(f"user_message is { user_message}")
    result = app.invoke({
        "user_message": user_message
    })
    print(f"result is {result}")
    return result["response"]

