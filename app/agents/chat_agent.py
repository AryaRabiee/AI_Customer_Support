from langchain_openrouter import ChatOpenRouter
from graph.state import SupportState
from langchain.messages import HumanMessage , SystemMessage
from utils.prompts import CHAT_PROMPT
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

import os

api_key = os.getenv("QWEN_GAPGPT_KEY")
base_url=os.getenv("BASE_URL_GAP")

model = ChatOpenAI(
    model="gapgpt-qwen-3.5",
    api_key=api_key,
    base_url=base_url
)


def chat_node(state: SupportState):

    response = model.invoke([
        SystemMessage(content=CHAT_PROMPT),
        *state["messages"]
    ])

    return {
        "response": response.content,
        "messages": [
            AIMessage(content=response.content)
        ]
    }

