from langchain_openrouter import ChatOpenRouter
from graph.state import SupportState
from langchain.messages import HumanMessage , SystemMessage
from utils.prompts import CHAT_PROMPT
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from exceptions.llm import LLMError , LLMTimeoutError
from openai import APIConnectionError ,APITimeoutError
import os
from utils.call_llm import call_llm
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv("QWEN_GAPGPT_KEY")
base_url=os.getenv("BASE_URL_GAP")

model = ChatOpenAI(
    model="gapgpt-qwen-3.5",
    api_key=api_key,
    base_url=base_url,
    timeout=30,
    max_retries=1
)
def chat_node(state: SupportState):
    print("user chat node",state["user_id"])
    response = call_llm(
        model,
        [
            SystemMessage(content=CHAT_PROMPT),
            *state["messages"]
        ]
    )

    return {
        "response": response.content,
        "messages": [
            AIMessage(content=response.content)
        ]
    }

