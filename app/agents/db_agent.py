from graph.state import SupportState , ExtractData
from langchain_openrouter import ChatOpenRouter
from langchain.messages import HumanMessage , SystemMessage
from utils.prompts import EXTRACT_DATA_PROMPT
import os
import re

api_key = os.getenv("EMBEDDING_API_KEY")

model = ChatOpenRouter(
    model="openai/gpt-oss-20b:free",
    api_key=api_key,
    temperature=0.5
)

output_model = model.with_structured_output(ExtractData)

def extract_data(state: SupportState):
    print("start func extract_data")

    messages = state["messages"]

    result = model.invoke([
        SystemMessage(content=EXTRACT_DATA_PROMPT),
        *messages
    ])

    content = result.content
    print(f"content is {content}")

    intent_match = re.search(
        r'intent\s*=\s*"([^"]+)"',
        content
    )

    order_id_match = re.search(
        r'order_id\s*=\s*(\d+|null)',
        content
    )

    intent = intent_match.group(1) if intent_match else None

    order_id = (
        int(order_id_match.group(1))
        if order_id_match and order_id_match.group(1) != "null"
        else None
    )

    print("intent:", intent)
    print("order_id:", order_id)

    return {
        "intent": intent,
        "order_id": order_id
    }