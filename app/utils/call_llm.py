from exceptions.llm import LLMError , LLMTimeoutError
from openai import APIConnectionError ,APITimeoutError,RateLimitError,APIError
from tenacity import retry , retry_if_exception_type , stop_after_attempt , wait_exponential_jitter
from langchain_openai import ChatOpenAI


fall_back1 = ChatOpenAI(
    model="",
    api_key="",
    base_url="",
    timeout=30,
    max_retries=1
)

fall_back2 = ChatOpenAI(
    model="",
    api_key="",
    base_url="",
    timeout=30,
    max_retries=1
)

def call_llm(model, messages):
    llm = model.with_fallbacks(
        fallbacks=[fall_back1, fall_back2],
        exceptions_to_handle=(
            TimeoutError,
            APITimeoutError,
            APIConnectionError,
            RateLimitError,
            APIError,
        ),
    )

    try:
        return llm.invoke(messages)

    except Exception:
        print("All LLM providers failed")
        raise
        
