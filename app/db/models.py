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
        
class Order(Base):

    __tablename__ = "orders"

    order_id = Column(Integer,primary_key=True)
        
        

    user_id = Column(Integer,ForeignKey("users.user_id"))
        
    
    status = Column(String(50),nullable=False)
        
        
    total_price = Column(Numeric(12, 2),nullable=False)
        


    shipping_address = Column(Text)
        

    created_at = Column(DateTime,server_default=func.now())
        
        
class Ticket(Base):

    __tablename__ = "tickets"

    ticked_id = Column(Integer,primary_key=True)
        


    user_id = Column(Integer,ForeignKey("users.user_id"))
        
        

    order_id = Column(Integer,ForeignKey("orders.order_id"))
        
        


    subject = Column(String(255),nullable=False)
        
        


    description = Column(Text,nullable=False)
        
        


    status = Column(String(50),nullable=False,default="open")
        
        
        


    created_at = Column(DateTime,server_default=func.now())
        
        
