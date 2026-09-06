from langchain.tools import tool
from app.db.models import Product
from app.utils.logger import logging
from app.db.database import SessionLocal
from sqlalchemy import select

logger = logging.getLogger(__name__)

@tool
def shop_find_product(product_name = None, category_id=None , min_price=None , max_price = None):
    """ this tool find the product with category_id and price from database """
    logger.info("calling tool shop_find_product ")

    if category_id is None:
        return {
            "response": (
                "برای اینکه بهتر راهنمایی‌تون کنم، لطفاً بگید محصول موردنظرتون "
                "در کدوم دسته قرار می‌گیره:\n"
                "1- لباس\n"
                "2- لوازم الکترونیکی\n"
                "3- لوازم خانه"
            )
        }

    if max_price is None:
        return {
            "response":"چه قیمتی مد نظر شماست"
        }

    db = SessionLocal()
    try:
        query = select(Product)

        if product_name:
            query = query.where(
                    Product.name.ilike(f"%{product_name}%")
                )

        if category_id:
            query = query.where(
                Product.category_id == category_id
            )
        if min_price:
            query = query.where(
                Product.price >= min_price
            )
        if max_price:
            query = query.where(
                Product.price <= max_price
            )

        products = db.execute(query).scalars().all()

        return {
            "products": [
                {
                    "product_id": product.product_id,
                    "name": product.name,
                    "category_id": product.category_id,
                    "price": product.price
                }
                for product in products
            ]
        }

    except Exception as e:
        logger.error("ERROR %s" , e)
        raise
    finally:
        db.close()