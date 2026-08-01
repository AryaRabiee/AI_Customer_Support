from graph.state import SupportState , ExtractData
from langchain_openrouter import ChatOpenRouter
from langchain.messages import HumanMessage , SystemMessage
from utils.prompts import EXTRACT_DATA_PROMPT
import os

api_key = os.getenv("EMBEDDING_API_KEY")

model = ChatOpenRouter(
    model="openai/gpt-oss-20b:free",
    api_key=api_key,
    temperature=0.5
)

output_model = model.with_structured_output(ExtractData)

def extract_data(state : SupportState):
    print("start func extract_data ")
    user_message = state["user_message"]

    result = model.invoke([
        SystemMessage(content = EXTRACT_DATA_PROMPT),
        HumanMessage(content = user_message)
    ])
    print(f"result extract_model is {result.content}")
    return {    
        "response": result.content
    }