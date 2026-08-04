from langchain_openrouter import ChatOpenRouter
from graph.state import SupervisorDecision , SupportState
from utils.prompts import SUPERVISOR_PROMPT
import os


api_key = os.getenv("EMBEDDING_API_KEY")

model = ChatOpenRouter(
    model="openai/gpt-oss-20b:free",
    api_key=api_key,
    temperature=0
)


supervisor_model = model.with_structured_output(
    SupervisorDecision
)


def supervisor_node(state: SupportState):

    print("1 - entered supervisor")

    user_id = state["user_id"]

    print("User ID:", user_id)
    print("2 - calling model")

    result = model.invoke([
        {
            "role": "system",
            "content": SUPERVISOR_PROMPT
        },
        {
            "role": "user",
            "content": state["user_message"]
        }
    ])

    print("3 - model responded")
    print("result supervisor_node :", result.content.strip())

    return {
        "next_agent": result.content.strip()
    }   