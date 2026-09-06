from langchain.messages import AIMessage , HumanMessage
from app.agents.shop_agent import shop_agent
from app.tools.shop.find_product import shop_find_product
from app.tools.shop.search_product import search_product
from unittest.mock import Mock , patch
import pytest
from decimal import Decimal


def test_agent_calls_shop_find_product():
    state = {
        "user_id": 1,
        "messages": [
            HumanMessage(
                content="سلام یه کیبورد میخواستم"
            )
        ],
    }

    result = shop_agent(state)

    assert result is not None
    assert "messages" in result
    assert len(result["messages"]) > 0

    message = result["messages"][0]

    assert isinstance(message, AIMessage)
    assert message.tool_calls
    assert message.tool_calls[0]["name"] == "shop_find_product"

def test_agent_calls_shop_find_product_with_no_price():

    state = {
        "user_id": 1,
        "messages": [
            HumanMessage(content="سلام یه کیبورد میخواستم")
        ],
    }

    result = shop_agent(state)

    message = result["messages"][0]

    assert isinstance(message, AIMessage)
    assert message.tool_calls
    assert message.tool_calls[0]["name"] == "shop_find_product"

    args = message.tool_calls[0]["args"]

    assert args["max_price"] is None

def test_find_product_with_filters():

    result = shop_find_product.invoke({
        "product_name": None,
        "category_id": 2,
        "min_price": None,
        "max_price": 90
    })

    assert result["products"]

    product = result["products"][0]

    assert product["product_id"] == 5
    assert product["name"] == "Anker USB-C Charger"
    assert product["category_id"] == 2
    assert product["price"] == Decimal("89.90")

def test_find_product_without_category():

    result = shop_find_product.invoke({
        "product_name": "charger",
        "category_id": None,
        "min_price": None,
        "max_price": 90
    })

    assert "response" in result
    assert "کدوم دسته" in result["response"]

def test_find_product_without_max_price():

    result = shop_find_product.invoke({
        "product_name": "charger",
        "category_id": 2,
        "min_price": None,
        "max_price": None
    })

    assert result["response"] == "چه قیمتی مد نظر شماست"

def test_find_product_by_name():

    result = shop_find_product.invoke({
        "product_name": "Anker",
        "category_id": 2,
        "min_price": None,
        "max_price": 100
    })

    assert result["products"]

    product = result["products"][0]

    assert "Anker" in product["name"]


def test_find_product_with_min_price():

    result = shop_find_product.invoke({
        "product_name": None,
        "category_id": 2,
        "min_price": 80,
        "max_price": 100
    })

    assert result["products"]

    for product in result["products"]:
        assert product["price"] >= 80
        assert product["price"] <= 100


def test_find_product_no_results():

    result = shop_find_product.invoke({
        "product_name": "NonExistingProduct",
        "category_id": 2,
        "min_price": None,
        "max_price": 90
    })

    assert result["products"] == []


@patch("app.tools.shop.find_product.SessionLocal")
def test_find_product_database_error(mock_session_local):

    mock_db = Mock()
    mock_db.execute.side_effect = Exception("Database error")

    mock_session_local.return_value = mock_db

    with pytest.raises(Exception, match="Database error"):
        shop_find_product.invoke({
            "product_name": "Anker",
            "category_id": 2,
            "min_price": None,
            "max_price": 100
        })

@patch("app.tools.shop.find_product.SessionLocal")
def test_find_product_closes_database(mock_session_local):

    mock_db = Mock()
    mock_session_local.return_value = mock_db

    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    shop_find_product.invoke({
        "product_name": "Anker",
        "category_id": 2,
        "min_price": None,
        "max_price": 100
    })

    mock_db.close.assert_called_once()

@patch("app.tools.shop.search_product.requests.post")
def test_search_product_success(mock_post):

    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {
                "title": "Anker Keyboard",
                "content": "A mechanical keyboard..."
            }
        ]
    }

    mock_post.return_value = mock_response

    result = search_product.invoke({
        "product": "keyboard"
    })

    assert "response" in result
    assert result["response"]["results"][0]["title"] == "Anker Keyboard"

    mock_post.assert_called_once()