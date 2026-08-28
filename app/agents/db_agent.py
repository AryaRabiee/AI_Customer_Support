from graph.state import SupportState , ExtractData
from langchain_openrouter import ChatOpenRouter
from langchain.messages import HumanMessage , SystemMessage , AIMessage
from utils.prompts import EXTRACT_DATA_PROMPT
import os
import re
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from utils.call_llm import call_llm,call_llm_with_tools
from dotenv import load_dotenv
from tools.database.order_detail import order_detail_tool
from tools.database.order_status import order_status_tool

import logging

logger = logging.getLogger(__name__)
load_dotenv()
api_key = os.getenv("QWEN_GAPGPT_KEY")
base_url=os.getenv("BASE_URL_GAP")

model = ChatOpenAI(
    model="gpt-5.6-luna",
    api_key=api_key,
    base_url=base_url,
    timeout=30,
    max_retries=2
)


def extract_data(state: SupportState):
    logger.info("Start extract_data")
    response = call_llm_with_tools(
        model,
        [
            SystemMessage(content=EXTRACT_DATA_PROMPT),
            *state["messages"]
        ],
        [order_detail_tool,order_status_tool]
    )

    return {
        "response": response.content,
        "messages": [
            AIMessage(content=response.content, tool_calls=response.tool_calls)
        ]
    }