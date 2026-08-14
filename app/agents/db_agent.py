from graph.state import SupportState , ExtractData
from langchain_openrouter import ChatOpenRouter
from langchain.messages import HumanMessage , SystemMessage
from utils.prompts import EXTRACT_DATA_PROMPT
import os
import re
from langchain_openai import ChatOpenAI
from utils.call_llm import call_llm

api_key = os.getenv("QWEN_GAPGPT_KEY")
base_url=os.getenv("BASE_URL_GAP")

model = ChatOpenAI(
    model="gapgpt-qwen-3.5",
    api_key=api_key,
    base_url=base_url,
    timeout=30,
    max_retries=2
)

output_model = model.with_structured_output(ExtractData)

def extract_data(state: SupportState):
    print("start func extract_data")


    messages = state["messages"]
    result = call_llm(model,
                        
        [
        SystemMessage(content=EXTRACT_DATA_PROMPT),
        *messages
        ]
                        )

    content = result.content or ""
    print(f"content is {content}")

    intent_match = re.search(r'intent\s*=\s*"([^"]+)"', content)
    intent = intent_match.group(1) if intent_match else None

    order_id = None
    order_id_match = re.search(r'order_id\s*=\s*(\d+|null)', content)
    if order_id_match and order_id_match.group(1) != "null":
        try:
            order_id = int(order_id_match.group(1))
        except ValueError:
            order_id = None   

    print("intent:", intent)
    print("order_id:", order_id)

    return {
        "intent": intent,
        "order_id": order_id
    }

