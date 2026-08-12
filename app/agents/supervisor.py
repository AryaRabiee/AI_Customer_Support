from langchain_openrouter import ChatOpenRouter
from graph.state import SupervisorDecision , SupportState
from utils.prompts import SUPERVISOR_PROMPT
import os
from langchain.messages import AIMessage , SystemMessage
from langchain_openai import ChatOpenAI


model = os.getenv("GPT_OSS")
api_key = os.getenv("MODEL_SUPERVISOR_V1")
base_url = os.getenv("BASE_URL_AR_1")


model = ChatOpenAI(
    model=model,
    api_key=api_key,
    base_url=base_url
)

supervisor_model = model.with_structured_output(
    SupervisorDecision
)


def supervisor_node(state: SupportState):

    print("1 - entered supervisor")

    user_id = state["user_id"]

    messages = state["messages"]
    print("MESSAGES", messages)

    print("User ID:", user_id)
    print("2 - calling model")

    result = model.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        *messages
    ])

    print("3 - model responded")
    print("RAW SUPERVISOR RESPONSE:", repr(result.content))

    decision = result.content.strip()

    print("result supervisor_node :", decision)

    if decision not in ["rag", "chat", "database" , "refund"]:
        raise ValueError(f"Invalid supervisor decision: {decision}")
    return {
        "next_agent": decision
    }   