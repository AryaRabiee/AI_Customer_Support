import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.order_info_agent import order_info_agent
from app.tools.database.order_info import get_order_info
from decimal import Decimal



def test_order_info_agent_calls_tool():
    state = {
        "user_id": 1,
        "messages": [
            HumanMessage(
                content="سلام میخوام اطلاعات سفارش شماره 1 رو بدونم"
            )
        ],
    }

    result = order_info_agent(state)

    assert result is not None
    assert "messages" in result
    assert len(result["messages"]) > 0

    message = result["messages"][0]

    assert isinstance(message, AIMessage)
    assert message.tool_calls
    assert message.tool_calls[0]["name"] == "get_order_info"
    assert message.tool_calls[0]["args"]["order_id"] == 1

def test_order_info_agent_does_not_call_tool_for_general_chat():
    state = {
        "user_id": 1,
        "messages": [
            HumanMessage(content="سلام خوبی؟")
        ],
    }

    result = order_info_agent(state)

    assert result is not None
    assert "messages" in result
    assert len(result["messages"]) > 0

    message = result["messages"][0]

    assert not message.tool_calls


def test_tool_with_valid_order():

    result = get_order_info.invoke({"order_id":1, "user_id":1})
    
    assert result["product"] == "T-shirt"
    assert result["status"] == "delivered"
    assert result["price"] == Decimal("1299.99")


@patch("app.tools.database.order_info.SessionLocal")
def test_tool_database_error(mock_session_local):
    mock_db = Mock()

    mock_db.execute.side_effect = Exception("Database connection failed")

    mock_session_local.return_value = mock_db

    result = get_order_info.invoke({"order_id":123, "user_id":1})

    assert result["response"] == "خطایی هنگام دریافت اطلاعات سفارش رخ داد"


@patch("app.tools.database.order_info.SessionLocal")
def test_tool_closes_database(mock_session_local):
    mock_db = Mock()

    mock_session_local.return_value = mock_db

    get_order_info.invoke({
        "order_id":1,
        "user_id":1
    })

    mock_db.close.assert_called_once()