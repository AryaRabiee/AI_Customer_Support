from langchain_openrouter import ChatOpenRouter
from graph.state import SupportState
from langchain.messages import HumanMessage , SystemMessage
from utils.prompts import CHAT_PROMPT
from langchain_core.messages import AIMessage

import os

api_key = os.getenv("EMBEDDING_API_KEY")

model = ChatOpenRouter(
    model="openai/gpt-oss-20b:free",
    api_key="***REMOVED***",
    temperature=0.5
)



def chat_node(state: SupportState):

    message = state["user_message"]

    response = model.invoke([
        SystemMessage(content=CHAT_PROMPT),
        HumanMessage(content=message)
    ])

    return {
        "response": response.content
    }

