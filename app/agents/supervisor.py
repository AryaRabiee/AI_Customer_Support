from langchain_openrouter import ChatOpenRouter
from app.graph.state import SupervisorDecision , SupportState
from app.utils.prompts import SUPERVISOR_PROMPT
import os
from langchain.messages import AIMessage , SystemMessage
from langchain_openai import ChatOpenAI
from app.exceptions.llm import InvalidDecisionError
from app.utils.call_llm import call_llm
import logging

logger = logging.getLogger(__name__)

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
    logger.info("STATE IS %s" , state)
    logger.info("1 - entered supervisor")

    user_id = state["user_id"]

    messages = state["messages"]
    logger.info("MESSAGE %s" , messages)

    logger.info("USER_ID IS %s" , user_id)
    logger.info("2 - calling model")

    result = call_llm(model,
    [
        SystemMessage(content=SUPERVISOR_PROMPT),
        *messages
    ])

    logger.info("3 - model responded")
    logger.info("RAW SUPERVISOR RESPONSE %s", repr(result.content))

    decision = result.content.strip()

    logger.info("result supervisor_node %s:", decision)

    if decision not in ["rag", "chat", "database", "refund"]:
        logger.error(
            "Invalid supervisor decision: %s",
            decision
        )
        raise InvalidDecisionError(
            f"Invalid supervisor decision: {decision}"
        )
    return {
        "next_agent": decision
    }   


    
