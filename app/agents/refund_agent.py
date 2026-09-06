from app.graph.state import SupportState , RefundOutput
from app.db.models import Order , Product
from app.db.database import SessionLocal
from sqlalchemy import select
from datetime import datetime
from langchain_openai import ChatOpenAI
from app.utils.prompts import REFUND_AGENT_PROMPT
from langchain.messages import SystemMessage , AIMessage
from app.utils.db_utils import get_data,save_to_expert , check_product_rule
from app.tools.refund.find_product import find_product
from app.tools.refund.check_rule import check_rule
from app.tools.refund.save_refund import save_refund
import os
from app.utils.call_llm import call_llm
from dotenv import load_dotenv
import logging
from app.utils.call_llm import call_llm_with_tools

logger = logging.getLogger(__name__)
load_dotenv()

api_key = os.getenv("GPT_API_KEY")
model = os.getenv("MODEL")
base_url = os.getenv("BASE_URL_GAP")
model = ChatOpenAI(
    model=model,
    api_key=api_key,
    base_url=base_url
)

def refund_agent(state: SupportState):
    logger.info("START FUNC REFUND")
    result = call_llm_with_tools(
        model ,
        [
            SystemMessage(content=REFUND_AGENT_PROMPT),
            *state["messages"]
        ],
        [find_product , check_rule,save_refund]
    )

    return{
        "response":result.content,
        "messages":[
            AIMessage(content=result.content ,tool_calls=result.tool_calls)
        ]
    }