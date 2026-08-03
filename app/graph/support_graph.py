from langgraph.graph import StateGraph, START, END
from graph.state import SupportState
from agents.supervisor import supervisor_node
from agents.rag_agent import rag_node
from agents.chat_agent import chat_node
from agents.db_agent import extract_data
from agents.order_status_agent import order_status_node
from agents.order_detail import order_detail_node
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver



graph = StateGraph(SupportState)

graph.add_node("supervisor", supervisor_node)
graph.add_node("rag", rag_node)
graph.add_node("chat", chat_node)
graph.add_node("database", extract_data)
graph.add_node("order_status", order_status_node)
graph.add_node("order_details", order_detail_node)


graph.add_edge(START, "supervisor")


graph.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"],
    {
        "rag": "rag",
        "chat": "chat",
        "database": "database"
    }
)


graph.add_conditional_edges(
    "database",
    lambda state: state["intent"],
    {
        "order_status": "order_status",
        "order_details": "order_details"
    }
)


graph.add_edge("rag", END)
graph.add_edge("chat", END)
graph.add_edge("order_status", END)
graph.add_edge("order_details", END)


app = graph.compile()


def run_support_agent(user_message: str,user_id: int):
    
    result = app.invoke({
        "user_message": user_message,
        "user_id": user_id
    })

    print("result:", result)

    return result["response"]
