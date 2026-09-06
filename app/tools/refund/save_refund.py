from langchain.tools import tool
from langgraph.prebuilt import InjectedState
from typing import Annotated
from app.db.database import SessionLocal
from app.db.models import RefundReview
from app.utils.logger import logging

logger = logging.getLogger(__name__)

@tool
def save_refund(user_id :Annotated[int , InjectedState("user_id")],
                order_id,
                product_id,
                expected_product,
                received_product,
                db_product,
                reason,
                description,
                status,
                ):
    """Save a completed refund request with all collected information to the database."""
    logger.info("tool called save_refund")
    required_fields = {
        "شماره سفارش": order_id,
        "شماره محصول": product_id,
        "محصول مورد انتظار": expected_product,
        "محصول دریافت‌شده": received_product,
        "محصول موجود در دیتابیس": db_product,
        "دلیل مرجوعی": reason,
        "توضیحات مشکل": description,
        "وضعیت": status,
    }

    missing_fields = [
        field_name
        for field_name , value in required_fields.items()
        if value is None
    ]

    if missing_fields:
        return{
            "response":(
                "برای ثبت درخواست مرجوعی، لطفاً اطلاعات زیر را وارد کنید: "
                + "، ".join(missing_fields)
            )
        }

    db = SessionLocal()

    try:
        expert_request = RefundReview(
            user_id=user_id,
            order_id=order_id,
            product_id=product_id,
            expected_product=expected_product,
            received_product=received_product,
            db_product=db_product,
            reason=reason,
            description=description,
            status=status
        )
        db.add(expert_request)
        db.commit()
        db.refresh(expert_request)

        return expert_request.review_id

    except Exception as e:
        db.rollback()
        logger.error("ERROE FROM SAVE_REFUND %s" , e)
        raise
    finally:
        db.close()

    