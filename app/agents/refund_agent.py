from graph.state import SupportState , RefundOutput
from db.models import Order , Product
from db.database import SessionLocal
from sqlalchemy import select
from datetime import datetime
from langchain_openai import ChatOpenAI
from utils.prompts import REFUND_AGENT_PROMPT
from langchain.messages import SystemMessage , AIMessage
from utils.db_utils import get_data,save_to_expert , check_product_rule
import os


api_key = os.getenv("GPT_API_KEY")
model = os.getenv("MODEL_REFUND")
base_url = os.getenv("BASE_URL_GAP")
model = ChatOpenAI(
    model=model,
    api_key=api_key,
    base_url=base_url
)


model_with_output = model.with_structured_output(RefundOutput)

def refund_agent(state: SupportState):
    print("START FUNC REFUND")


    result = model_with_output.invoke([
        SystemMessage(content=REFUND_AGENT_PROMPT),
        *state["messages"]
    ])

    action = result.action
    reason = result.reason
    order_id = result.order_id
    product_id = result.product_id
    expected_product = result.expected_product
    received_product = result.received_product
    description = result.description
    response = result.message

    print("RESULT IS:", result)
    print("reason:", reason)
    print("order_id:", order_id)
    print("product_id:", product_id)
    print("expected_product:", expected_product)
    print("received_product:", received_product)


    if reason is None:
        return {
            "refund_action": "ASK_REASON",
            "response": response,
            "messages": AIMessage(content=response),
        }

    if order_id is None:
        return {
            "reason": reason,
            "refund_action": "ASK_INFORMATION",
            "response": response,
            "messages": AIMessage(content=response),
        }

    if product_id is None:
        return {
            "reason": reason,
            "order_id": order_id,
            "refund_action": "ASK_INFORMATION",
            "response": response,
            "messages": AIMessage(content=response),
        }



    if reason == "wrong_product":

        if expected_product is None or received_product is None:
            return {
                "order_id": order_id,
                "product_id": product_id,
                "expected_product": expected_product,
                "received_product": received_product,
                "reason": reason,
                "description": description,
                "refund_action": "ASK_INFORMATION",
                "response": response,
                "messages": AIMessage(content=response),
            }

        print("REASON: wrong_product - All information collected")


        order_data = get_data(
            state["user_id"],
            order_id,
            product_id
        )

        if order_data is None:

            message = (
                "شماره سفارش یا شماره محصول با اطلاعات ثبت‌شده "
                "مطابقت ندارد. لطفاً اطلاعات صحیح را وارد کنید."
            )

            return {
                "order_id": order_id,
                "product_id": product_id,
                "expected_product": expected_product,
                "received_product": received_product,
                "reason": reason,
                "description": description,
                "refund_action": "ASK_INFORMATION",
                "response": message,
                "messages": AIMessage(content=message),
            }



        db_product_name = order_data["product_name"]

        print("DB PRODUCT NAME:", db_product_name)
        print("USER RECEIVED PRODUCT:", received_product)

        products_match = (
            db_product_name.strip().lower()
            == received_product.strip().lower()
        )

        print("PRODUCTS MATCH:", products_match)


        if products_match:

            message = (
                "محصولی که دریافت کرده‌اید با اطلاعات ثبت‌شده "
                "در سفارش شما مطابقت دارد. "
                "بنابراین مغایرتی بین محصول ثبت‌شده و محصول دریافتی "
                "مشاهده نشد."
            )

            return {
                "order_id": order_id,
                "product_id": product_id,
                "expected_product": expected_product,
                "received_product": received_product,
                "reason": reason,
                "description": description,
                "refund_action": "FINAL",
                "response": message,
                "need_check": False,
                "messages": AIMessage(content=message),
            }



        print("NEED_CHECK = TRUE - Sending to expert")

        save_to_expert(
            state["user_id"],
            order_id,
            product_id,
            expected_product,
            received_product,
            db_product_name,
            reason,
            description,
            "pending"
        )

        message = (
            "اطلاعات شما ثبت شد. "
            "درخواست شما برای بررسی دقیق‌تر به تیم پشتیبانی ارسال شد. "
            "نتیجه بررسی به شما اطلاع داده خواهد شد."
        )

        return {
            "order_id": order_id,
            "product_id": product_id,
            "expected_product": expected_product,
            "received_product": received_product,
            "reason": reason,
            "description": description,
            "refund_action": "FINAL",
            "response": message,
            "need_check": True,
            "messages": AIMessage(content=message),
        }


    if reason == "changed_mind":

        print("REASON: changed_mind Started")

        rule_result = check_product_rule(
            state["user_id"],
            order_id
        )
        product = get_data(
                        state["user_id"],
                        order_id,
                        product_id
                    )
        
        db_product_name = product["product_name"]
        if rule_result["allowed"]:
            save_to_expert(
                state["user_id"],
                order_id,
                product_id,
                expected_product,
                received_product,
                db_product_name,
                reason,
                description,
                "accept"
            )
            message = "درخواست شما ثبت شده و در حالت تایید شده قرار گرفته نتیجه نهایی آن طی ساعات آینده به شما اعلام میشود"
        else:
            if rule_result["reason"] == "expired":

                message = (
                    f"برای مرجوع کردن این کالا حداکثر "
                    f"{rule_result['max_days']} روز فرصت داشتید. "
                    f"مهلت مرجوعی این کالا به پایان رسیده است؛ "
                    f"در نتیجه درخواست شما تأیید نشد."
                )

                save_to_expert(
                    state["user_id"],
                    order_id,
                    product_id,
                    expected_product,
                    received_product,
                    db_product_name,
                    reason,
                    description,
                    "reject"
                )
        return {
            "order_id": order_id,
            "product_id": product_id,
            "reason": reason,
            "description": description,
            "refund_action": "FINAL",
            "response": message,
            "messages": AIMessage(content=message),
        }

    if reason == "not_as_described":

        if description is None or not description.strip():
            return {
                "order_id": order_id,
                "product_id": product_id,
                "reason": reason,
                "description": description,
                "refund_action": "ASK_INFORMATION",
                "response": response,
                "messages": AIMessage(content=response),
            }

        print("REASON: not_as_described - All information collected")

        order_data = get_data(
            state["user_id"],
            order_id,
            product_id
        )

        if order_data is None:

            message = (
                "شماره سفارش یا شماره محصول با اطلاعات ثبت‌شده "
                "مطابقت ندارد. لطفاً اطلاعات صحیح را وارد کنید."
            )

            return {
                "order_id": order_id,
                "product_id": product_id,
                "reason": reason,
                "description": description,
                "refund_action": "ASK_INFORMATION",
                "response": message,
                "messages": AIMessage(content=message),
            }

        db_product_name = order_data["product_name"]

        print("DB PRODUCT NAME:", db_product_name)
        print("USER DESCRIPTION:", description)



        save_to_expert(
            state["user_id"],
            order_id,
            product_id,
            None,               # expected_product
            None,               # received_product
            db_product_name,    # محصول ثبت‌شده در DB
            reason,
            description,        # شرح دقیق مغایرت
            "pending"
        )

        message = (
            "اطلاعات شما ثبت شد. "
            "درخواست شما برای بررسی مغایرت مشخصات محصول "
            "به تیم پشتیبانی ارسال شد. "
            "نتیجه بررسی به شما اطلاع داده خواهد شد."
        )

        return {
            "order_id": order_id,
            "product_id": product_id,
            "expected_product": None,
            "received_product": None,
            "reason": reason,
            "description": description,
            "refund_action": "FINAL",
            "response": message,
            "need_check": True,
            "messages": AIMessage(content=message),
        }

    if reason == "other":

        print("REASON: other")

        if description is None or not description.strip():

            return {
                "order_id": order_id,
                "product_id": product_id,
                "reason": reason,
                "description": description,
                "refund_action": "ASK_INFORMATION",
                "response": response,
                "messages": AIMessage(content=response),
            }

        order_data = get_data(
            state["user_id"],
            order_id,
            product_id
        )

        if order_data is None:

            message = (
                "شماره سفارش یا شماره محصول با اطلاعات ثبت‌شده "
                "مطابقت ندارد. لطفاً اطلاعات صحیح را وارد کنید."
            )

            return {
                "order_id": order_id,
                "product_id": product_id,
                "reason": reason,
                "description": description,
                "refund_action": "ASK_INFORMATION",
                "response": message,
                "messages": AIMessage(content=message),
            }

        db_product_name = order_data["product_name"]

        save_to_expert(
            state["user_id"],
            order_id,
            product_id,
            None,               
            None,               
            db_product_name,
            reason,
            description,
            "pending"
        )

        message = (
            "اطلاعات شما ثبت شد. "
            "درخواست شما برای بررسی دقیق‌تر به تیم پشتیبانی ارسال شد. "
            "نتیجه بررسی به شما اطلاع داده خواهد شد."
        )

        return {
            "order_id": order_id,
            "product_id": product_id,
            "expected_product": None,
            "received_product": None,
            "reason": reason,
            "description": description,
            "refund_action": "FINAL",
            "response": message,
            "need_check": True,
            "messages": AIMessage(content=message),
        }


    return {
        "order_id": order_id,
        "product_id": product_id,
        "reason": reason,
        "description": description,
        "refund_action": action,
        "response": response,
        "messages": AIMessage(content=response),
    }

