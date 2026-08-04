from langchain_openrouter import ChatOpenRouter
from graph.state import SupportState
from langchain.messages import HumanMessage , SystemMessage
from utils.prompts import CHAT_PROMPT
from langchain_core.messages import AIMessage

import os

api_key = os.getenv("EMBEDDING_API_KEY")

model = ChatOpenRouter(
    model="openai/gpt-oss-20b:free",
    api_key=api_key,
    temperature=0.5
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

