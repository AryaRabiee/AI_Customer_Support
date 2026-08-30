from langgraph.graph import StateGraph, START, END
from graph.state import SupportState
from agents.supervisor import supervisor_node
from agents.rag_agent import rag_node
from agents.chat_agent import chat_node
from agents.db_agent import extract_data
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from agents.refund_agent import refund_agent
from exceptions.llm import LLMError , LLMTimeoutError
from langgraph.prebuilt import ToolNode ,tools_condition
from tools.database.order_detail import order_detail_tool
from tools.database.order_status import order_status_tool
from tools.refund.find_product import find_product
from tools.refund.check_rule import check_rule
from tools.refund.save_refund import save_refund
from tools.shop.find_product import shop_find_product
from tools.shop.products_informations import product_info_search
from agents.shop_agent import shop_agent
from tools.shop.search_product import search_product


import logging

logger = logging.getLogger(__name__)

tools = [
    order_detail_tool,
    order_status_tool
 ]
refund_tools = [
    find_product,
    check_rule,
    save_refund
]

shop_tools = [
    shop_find_product,
    product_info_search,
    search_product
]

graph = StateGraph(SupportState)
memory = InMemorySaver()
tool_node = ToolNode(tools)
tool_refunds = ToolNode(refund_tools)
shop_tools = ToolNode(shop_tools)

graph.add_node("supervisor", supervisor_node)
graph.add_node("rag", rag_node)
graph.add_node("chat", chat_node)
graph.add_node("database", extract_data)
graph.add_node("shop" ,shop_agent)
graph.add_node("tools", tool_node)
graph.add_node("refund", refund_agent)
graph.add_node("tool_refund" , tool_refunds)
graph.add_node("tool_shop" ,shop_tools )

graph.add_edge(START, "supervisor")


graph.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"],
    {
        "rag": "rag",
        "chat": "chat",
        "database": "database",
        "refund":"refund",
        "shop":"shop"
    }
)


graph.add_conditional_edges(
    "database",
    tools_condition,
    {
        "tools": "tools",
        END: END
    }
)
graph.add_edge("tools","database")

graph.add_conditional_edges(
    "refund",
    tools_condition,
    {
        "tools": "tool_refund",
        END: END
    }
)
graph.add_edge("tool_refund","refund")
graph.add_conditional_edges(
    "shop",
    tools_condition,
    {
        "tools": "tool_shop",
        END: END
    }
)
graph.add_edge("tool_shop","shop")
graph.add_edge("rag", END)
graph.add_edge("chat", END)
graph.add_edge("refund", END)

app = graph.compile(
    checkpointer=memory
)
def run_support_agent(user_message: str,user_id: int , thread_id):

    try:
        result = app.invoke(
            {
                "user_message": user_message,
                "user_id": user_id,
                "messages": [
                    HumanMessage(content=user_message)
                ]
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )
        print("RESULT IS" , result)
        logger.info(
            "Agent result | intent=%s | next_agent=%s | order_id=%s | response=%s",
            result.get("intent"),
            result.get("next_agent"),
            result.get("order_id"),
            result.get("response"),
        )
        return result["response"]
    
    
    except Exception as e:
        logger.exception("Support agent failed %s" , e)
        raise