from graph.state import SupportState
from db.database import SessionLocal
from sqlalchemy import select
from db.models import Order ,Product
from utils.call_llm import call_llm
from langchain.tools import tool
from langchain.messages import SystemMessage , AIMessage
import logging
from langgraph.prebuilt import InjectedState
from typing import Annotated


logger = logging.getLogger(__name__)
@tool
def order_detail_tool(order_id: int, user_id : Annotated[int , InjectedState("user_id")]):
    """Get the details of a customer's order."""
    logger.info("tool called order_detail_tool")
    print("order_id " , order_id)
    if order_id is None:
        return{
            "response":"لطفا شماره سفارش خود را وارد کنید"
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
        order , product = result
        print("order is" , order)
        print("product is" , product.name)
        print("status is" , order.status)
        print("price is" , order.total_price)
        if order is None:
            return {
                "response":"سفارش شما پیدا نشد"
            }
        
        return {
            "product":product.name,
            "status":order.status,
            "price":order.total_price
        } 

    except Exception as e:
        logger.error("ERROR IS %s" , e)

    finally:
        db.close()
        
        
        
