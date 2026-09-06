from app.graph.state import SupportState
from app.db.database import SessionLocal
from sqlalchemy import select
from app.db.models import Order , Product
from app.utils.call_llm import call_llm
from langchain.messages import SystemMessage , AIMessage
import logging
from langgraph.prebuilt import InjectedState
from langchain.tools import tool
from typing import Annotated


logger = logging.getLogger(__name__)
@tool
def get_order_info(
    order_id: int,
    user_id: Annotated[int, InjectedState("user_id")]
):
    """Get information about a customer's order by order ID."""

    logger.info("tool called get_order_info")
    
    if order_id is None:
        return {
            "response": "لطفا شماره سفارش خود را وارد کنید"
        }

    db = SessionLocal()

    try:
        result = db.execute(
            select(Order, Product)
            .join(Product, Product.product_id == Order.product_id)
            .where(
                Order.order_id == order_id,
                Order.user_id == user_id
            )
        ).first()

        if result is None:
            return {
                "response": "سفارش شما پیدا نشد"
            }

        order, product = result

        return {
            "product": product.name,
            "status": order.status,
            "price": order.total_price
        }

    except Exception as e:
        logger.error("ERROR IS %s", e)
        return {
            "response": "خطایی هنگام دریافت اطلاعات سفارش رخ داد"
        }

    finally:
        db.close()