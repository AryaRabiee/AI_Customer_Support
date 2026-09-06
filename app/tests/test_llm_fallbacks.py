from unittest.mock import Mock
from openai import APIError
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage , HumanMessage


def test_fallback_chain():

    primary = RunnableLambda(
        lambda _: (_ for _ in ()).throw(
            APIError(
                message="Primary failed",
                request=None,
                body=None
            )
        )
    )

    fallback1 = RunnableLambda(
        lambda _: AIMessage(content="Fallback 1 response")
    )

    fallback2 = RunnableLambda(
        lambda _: AIMessage(content="Fallback 2 response")
    )

    llm = primary.with_fallbacks(
        fallbacks=[fallback1, fallback2],
        exceptions_to_handle=(APIError,)
    )

    result = llm.invoke(
        [HumanMessage(content="سلام")]
    )

    assert result.content == "Fallback 1 response"