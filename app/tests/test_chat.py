from langchain.messages import HumanMessage ,AIMessage
from unittest.mock import patch , MagicMock
from app.agents.chat_agent import chat_node

def test_chat_node():

    fake_state = {
        "user_id":1,
        "messages":[
            HumanMessage(content="سلام")
        ]

    }

    fake_response = MagicMock()
    fake_response.content = "سلام! چطور می‌تونم کمکتون کنم؟"

    with patch("app.agents.chat_agent.call_llm" , return_value=fake_response):
        result = chat_node(fake_state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)