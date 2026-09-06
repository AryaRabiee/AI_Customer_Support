from app.graph.state import SupportState
from app.utils.logger import logging
from app.utils.call_llm import call_llm_with_tools
import os
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage , AIMessage
from app.utils.prompts import SHOP_AGENT_PRONPT
from app.tools.shop.find_product import shop_find_product
from app.tools.shop.products_informations import product_info_search
from app.tools.shop.search_product import search_product
logger = logging.getLogger(__name__)

api_key = os.getenv("GPT_API_KEY")
model = os.getenv("MODEL")
base_url = os.getenv("BASE_URL_GAP")
model = ChatOpenAI(
    model=model,
    api_key=api_key,
    base_url=base_url
)

def shop_agent(state:SupportState):
    logger.info("START FUNC SHOP AGENT")

    result = call_llm_with_tools(
        model,
        [
            SystemMessage(content=SHOP_AGENT_PRONPT),
            *state["messages"]

        ],
        [shop_find_product,product_info_search,search_product]

    )
    return {
        "response":result.content,
        "messages":[
            AIMessage(content=result.content , tool_calls = result.tool_calls)
        ]
    }