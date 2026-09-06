from langchain.tools import tool
from app.utils.logger import logging
from datetime import datetime , timedelta
logger = logging.getLogger(__name__)
@tool
def check_rule(product_name , category_id , created_at):
    """Check the rules to know that it can refund or not"""
    logger.info("tool called check_rule")
    if product_name is None:
        return{
            "response":"محصول یافت نشد"
        }

    if category_id == 1:
        max_days = 1
    elif category_id == 2:
        max_days = 3
    # elif category_id == 3:
    #     return {
    #         "allowed": False,
    #         "reason": "unreturnable",
    #         "max_days": max_days,
    #         "created_at": created_at,
    #         "now": now,
    #         "elapsed": elapsed,
    #         "product_name": product_name,
    #         "category_id":category_id
    #     }
    else:
        max_days = 5

    now = datetime.now()
    elapsed = now - datetime.fromisoformat(created_at)

    if elapsed > timedelta(days = max_days):
        return {
            "allowed": False,
            "reason": "expired",
            "max_days": max_days,
            "created_at": created_at,
            "now": now,
            "elapsed": elapsed,
            "product_name": product_name,
            "category_id":category_id,
        }

    return {
        "allowed": True,
        "reason": "within_deadline",
        "max_days": max_days,
        "created_at": created_at,
        "now": now,
        "elapsed": elapsed,
        "product_name": product_name,
        "category_id":category_id
    }