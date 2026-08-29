from graph.state import SupportState , RefundOutput
from db.models import Order , Product
from db.database import SessionLocal
from sqlalchemy import select
from datetime import datetime
from langchain_openai import ChatOpenAI
from utils.prompts import REFUND_AGENT_PROMPT
from langchain.messages import SystemMessage , AIMessage
from utils.db_utils import get_data,save_to_expert , check_product_rule
from tools.refund.find_product import find_product
from tools.refund.check_rule import check_rule
from tools.refund.save_refund import save_refund
import os
from utils.call_llm import call_llm
from dotenv import load_dotenv
import logging
from utils.call_llm import call_llm_with_tools

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


model_with_output = model.with_structured_output(RefundOutput)

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