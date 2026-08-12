from db.models import User , Product , Order , RefundReview
from sqlalchemy import select
from db.database import SessionLocal
from datetime import datetime , timedelta


def get_data(user_id, order_id, product_id):
    db = SessionLocal()

    try:
        result = db.execute(
            select(
                Order.order_id,
                Order.user_id,
                Order.product_id,
                Product.name
            )
            .join(
                Product,
                Order.product_id == Product.product_id
            )
            .where(
                Order.user_id == user_id,
                Order.order_id == order_id,
                Order.product_id == product_id
            )
        ).first()

        if result is None:
            return None

        return {
            "order_id": result.order_id,
            "user_id": result.user_id,
            "product_id": result.product_id,
            "product_name": result.name,
        }

    finally:
        db.close()
def save_to_expert(
    user_id,
    order_id,
    product_id,
    expected_product,
    received_product,
    db_product,
    reason,
    description,
    status
):
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

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def check_product_rule(user_id, order_id):

    db = SessionLocal()

    try:
        result = db.execute(
            select(
                Order.order_id,
                Order.user_id,
                Order.product_id,
                Order.created_at,
                Product.name,
                Product.category_id
            )
            .join(
                Product,
                Order.product_id == Product.product_id
            )
            .where(
                Order.order_id == order_id,
                Order.user_id == user_id
            )
        )

        row = result.first()

        if row is None:
            return {
                "allowed": False,
                "reason": "order_not_found"
            }

        if row.product_id == 1:
            max_days = 2
        elif row.product_id == 3:
            max_days = 1
        else:
            max_days = 5

        now = datetime.now()
        elapsed = now - row.created_at

        if elapsed > timedelta(days=max_days):
            return {
                "allowed": False,
                "reason": "expired",
                "max_days": max_days,
                "created_at": row.created_at,
                "now": now,
                "elapsed": elapsed,
                "product_name": row.name,
                "category_id": row.category_id
            }

        return {
            "allowed": True,
            "reason": "within_deadline",
            "max_days": max_days,
            "created_at": row.created_at,
            "now": now,
            "elapsed": elapsed,
            "product_name": row.name,
            "category_id": row.category_id
        }

    finally:
        db.close()