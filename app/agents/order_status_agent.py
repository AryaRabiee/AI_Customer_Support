from graph.state import SupportState
from db.database import SessionLocal
from db.models import Order , User
from sqlalchemy import select
from langchain_openrouter import ChatOpenRouter
from langchain.messages import HumanMessage , SystemMessage
from utils.prompts import ORDER_STATUS_PROMPT
import os


api_key = os.getenv("EMBEDDING_API_KEY")

model = ChatOpenRouter(
    model="openai/gpt-oss-20b:free",
    api_key="***REMOVED***",
    temperature=0.5
)


def order_status_node(state:SupportState):
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

        prompt = ORDER_STATUS_PROMPT.format(
            user_message = state["user_message"],
            order_data = order.status
        )
        response = model.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=state["user_message"])
        ])

        return{
            "response":response.content
        }

    finally:
        db.close()

    
    
