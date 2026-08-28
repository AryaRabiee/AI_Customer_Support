from exceptions.llm import LLMError , LLMTimeoutError
from openai import APIConnectionError ,APITimeoutError,RateLimitError,APIError
from tenacity import retry , retry_if_exception_type , stop_after_attempt , wait_exponential_jitter
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)
load_dotenv()
api_key = os.getenv("QWEN_GAPGPT_KEY")
base_url=os.getenv("BASE_URL_GAP")
fall_back1 = ChatOpenAI(
    model="gpt-5-nano",
    api_key=api_key,
    base_url=base_url,
    timeout=30,
    max_retries=1
)

fall_back2 = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=api_key,
    base_url=base_url,
    timeout=30,
    max_retries=1
)

def _build_llm(model):
    return model.with_fallbacks(
        fallbacks=[fall_back1, fall_back2],
        exceptions_to_handle=(
            TimeoutError,
            APITimeoutError,
            APIConnectionError,
            RateLimitError,
            APIError,
        ),
    )


def call_llm(model, messages):
    logger.info("Calling primary model: %s", getattr(model, "model_name", "unknown"))
    llm = _build_llm(model)
    try:
        return llm.invoke(messages)
    except Exception:
        logger.exception("All LLM providers failed")
        raise

def call_llm_with_tools(model, messages, tools):
    logger.info("Calling primary model: %s", getattr(model, "model_name", "unknown"))
    llm = _build_llm(model).bind_tools(tools)
    try:
        return llm.invoke(messages)
    except Exception:
        logger.exception("All LLM providers failed")
        raise