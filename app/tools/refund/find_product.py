from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from typing import Annotated
from langgraph.prebuilt import InjectedState
from app.db.database import SessionLocal
from sqlalchemy import select
from app.db.models import Product , Order , Category
from langchain.tools import tool
from app.utils.logger import logging
logger = logging.getLogger(__name__)
load_dotenv()
model_name = os.getenv("MODEL")
api_key = os.getenv("GPT_API_KEY")
base_url = os.getenv("BASE_URL_GAP")

model = ChatOpenAI(
    model = model_name,
    api_key=api_key,
    base_url=base_url
)

@tool
def find_product(order_id , product_id , user_id : Annotated[int , InjectedState("user_id")]):
    """Find the product from database by order_id and product_id"""
    logger.info("tool called find_product")
    if order_id is None:
        return{
            "response":"لطفا شماره سفارش خود را وارد کنید"
        }

    if product_id is None:
        return{
            "response":"لطفا شماره محصول خود را وارد کنید"
        }
    db = SessionLocal()
    result = db.execute(
        select(Order, Product , Category)
        .join(Product, Product.product_id == Order.product_id)
        .join(Category , Category.category_id == Product.category_id)
        .where(
            Order.order_id == order_id,
            Order.user_id == user_id,
            Product.product_id == product_id
        )
    ).first()
    if result is None:
        return {
            "response": "محصولی با چنین شماره‌ای پیدا نشد"
        }
    order , product , category = result
    if order is None:
        return {
            "response":"سفارش شما پیدا نشد"
        }
    if product is None:
        return {
            "response":"محصلی با چنین شمارهای پیدا نشد شما پیدا نشد"
        }
    print("order is" , order)
    print("created_at" , order.created_at)
    print("product is" , product.name)
    print("category is" , category.category_id)

    return {
        "product":product.name,
        "category":category.category_id,
        "created_at":order.created_at
    }