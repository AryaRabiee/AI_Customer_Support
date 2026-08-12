from sqlalchemy import Column, Integer, String, Boolean, DateTime , ForeignKey , Text , Numeric
from sqlalchemy.sql import func

from db.database import Base


class User(Base):

    __tablename__ = "users"

    user_id = Column(Integer,primary_key=True)
        
    name = Column(String(100),nullable=False)

    email = Column(String(255),unique=True,nullable=False)


    password = Column(String(255),nullable=False)
        
        
    is_admin = Column(Boolean,default=False)
        
        

    created_at = Column(DateTime,server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False
    )

    returnable = Column(
        Boolean,
        default=True,
        nullable=False
    )

class Product(Base):
    __tablename__ = "products"

    product_id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.category_id"),
        nullable=False
    )

    price = Column(
        Numeric(12, 2),
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )
        
class Order(Base):
    __tablename__ = "orders"

    order_id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id"),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    total_price = Column(
        Numeric(12, 2),
        nullable=False
    )

    shipping_address = Column(
        Text
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )
        
        
class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.order_id"),
        nullable=True
    )

    subject = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="open"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )
class RefundReview(Base):
    __tablename__ = "refund_reviews"

    review_id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.order_id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.product_id"),
        nullable=False
    )

    expected_product = Column(
        String(255),
        nullable=True
    )

    received_product = Column(
        String(255),
        nullable=True
    )

    db_product = Column(
        String(255),
        nullable=False
    )

    reason = Column(
        String(50),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="pending"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )
        
