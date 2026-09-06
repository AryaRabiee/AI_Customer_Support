from langchain.tools import tool
from app.utils.logger import logging
import requests
import os

api_key = os.getenv("t_search")
logger = logging.getLogger(__name__)

@tool
def search_product(product):
    """ this tool is going to search about the product from internt """
    logger.info("tool calling search_product")
    response = requests.post(
        "https://api.avalai.ir/v1/search/tavily-search",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"query":f"اطلاعاتی درباره {product}", "max_results": 5 , "country":"iran"},
    )
    result = response.json()

    return {
        "response":result
    }