from graph.state import SupportState
from db.database import SessionLocal
from db.models import Order , User
from sqlalchemy import select
from langchain_openrouter import ChatOpenRouter
from langchain.messages import HumanMessage , SystemMessage
from utils.prompts import ORDER_DETAIL_PROMPT
import os
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI


api_key = os.getenv("QWEN_GAPGPT_KEY")
base_url=os.getenv("BASE_URL_GAP")

model = ChatOpenAI(
    model="gapgpt-qwen-3.5",
    api_key=api_key,
    base_url=base_url
)
def order_detail_node(state: SupportState):
    order_id = state["order_id"]

    if order_id is None:
        return {
            "response": "لطفاً شماره سفارش خود را وارد کنید."
        }

    db = SessionLocal()

    try:
        order = db.execute(
            select(Order).where(
                Order.order_id == order_id,
                Order.user_id == state["user_id"]
            )
        ).scalar_one_or_none()

        if order is None:
            return {
                "response": "سفارش موردنظر پیدا نشد."
            }

        prompt = ORDER_DETAIL_PROMPT.format(
            user_message=state["user_message"],
            order_data=order.products
        )

        response = model.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=state["user_message"])
        ])

        return {
            "response": response.content
        }

    finally:
        db.close()
        

