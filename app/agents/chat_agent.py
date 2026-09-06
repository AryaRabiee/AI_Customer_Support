from langchain_openrouter import ChatOpenRouter
from app.graph.state import SupportState
from langchain.messages import HumanMessage , SystemMessage
from app.utils.prompts import CHAT_PROMPT
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
import os
from app.utils.call_llm import call_llm
from dotenv import load_dotenv
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


