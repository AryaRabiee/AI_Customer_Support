from langchain.tools import tool
from app.utils.logger import logging
from .hybrid_search_products import hybrid_search_products
import os
from pathlib import Path
from bm25s import BM25
from hazm import Normalizer , word_tokenize
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings , ChatOpenAI
from app.graph.state import SupportState
from langgraph.prebuilt import InjectedState
from typing import Annotated
from dotenv import load_dotenv
current_dir = Path(__file__).parent
CHROMA_DIR = current_dir / "chroma_db"

logger = logging.getLogger(__name__)



@tool
def product_info_search(
    products,
    user_message: Annotated[str, InjectedState("user_message")]
):
    """Give detailed information about the products found for the customer."""

    logger.info("Calling tool products_informations")
    print(products)
    result = hybrid_search_products(
        message=user_message,
        products=products
    )

    return {
        "response": result
    }