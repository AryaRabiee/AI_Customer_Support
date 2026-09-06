from langchain.messages import AIMessage , HumanMessage
from app.agents.refund_agent import refund_agent
from app.tools.refund.check_rule import check_rule
from app.tools.refund.find_product import find_product
from app.tools.refund.save_refund import save_refund
from unittest.mock import Mock , patch
import pytest


def test_agent_calls():

    state = {
        "user_id": 1,
        "messages": [
            HumanMessage(
                content="سلام میخوام سفارش شماره 1 با شماره محصول 1 رو مرجوع کنم"
            )
        ],
    }

    result = refund_agent(state)


    assert result is not None
    assert "messages" in result
    assert len(result["messages"]) > 0

    message = result["messages"][0]

    assert isinstance(message, AIMessage)
    
def test_valid_find_product():
    result = find_product.invoke({
        "order_id": 1,
        "product_id": 1,
        "user_id": 1
    })

    assert result["product"] == "T-shirt"
    assert result["category"] == 1
    assert result["created_at"] is not None

def test_find_product_not_found():
    result = find_product.invoke({
        "order_id": 1,
        "product_id": 999,
        "user_id": 1
    })

    assert result["response"] == "محصولی با چنین شماره‌ای پیدا نشد"

def test_check_rule_expired():
    result = check_rule.invoke({
        "product_name": "T-shirt",
        "category_id": 1,
        "created_at": "2026-08-01T15:53:57"
    })

    assert result["allowed"] is False
    assert result["reason"] == "expired"
    assert result["max_days"] == 1


def test_check_rule_product_not_found():
    result = check_rule.invoke({
        "product_name": None,
        "category_id": 1,
        "created_at": "2026-09-06T15:53:57"
    })

    assert result["response"] == "محصول یافت نشد"


def test_check_rule_within_deadline():
    result = check_rule.invoke({
        "product_name": "towel",
        "category_id": 3,
        "created_at": "2026-09-06T00:00:00"
    })

    assert result["allowed"] is True
    assert result["reason"] == "within_deadline"
    assert result["max_days"] == 5


def test_save_refund_missing_fields():

    result = save_refund.invoke({
        "user_id": 1,
        "order_id": 1,
        "product_id": 1,
        "expected_product": None,
        "received_product": "T-shirt",
        "db_product": "T-shirt",
        "reason": "wrong_product",
        "description": "محصول اشتباه ارسال شده",
        "status": "pending",
    })

    assert "محصول مورد انتظار" in result["response"]


@patch("app.tools.refund.save_refund.SessionLocal")
def test_save_refund_database_error(mock_session_local):

    mock_db = Mock()
    mock_db.commit.side_effect = Exception("Database error")

    mock_session_local.return_value = mock_db

    with pytest.raises(Exception):
        save_refund.invoke({
            "user_id": 1,
            "order_id": 1,
            "product_id": 1,
            "expected_product": "T-shirt",
            "received_product": "T-shirt",
            "db_product": "T-shirt",
            "reason": "wrong_product",
            "description": "محصول اشتباه ارسال شده",
            "status": "pending",
        })

    mock_db.rollback.assert_called_once()
    mock_db.close.assert_called_once()