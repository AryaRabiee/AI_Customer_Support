from sqlalchemy import create_engine
from sqlalchemy.orm import session , sessionmaker , declarative_base
import os

DATABASE_URL = "postgresql://postgres:arya1384@localhost:5432/ai_support_database"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False , autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

