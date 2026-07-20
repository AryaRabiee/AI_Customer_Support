import requests
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

api_get_embedding = os.getenv("EMBEDDING_API_KEY")
URL = os.getenv("EMBEDDING_URL")

def get_embedding(text):
    url = URL
    headers = {
        "Authorization": f"Bearer {api_get_embedding}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/text-embedding-3-small",
        "input": [text]

    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"response is {response}")
        response.raise_for_status()
        
        response_json = response.json()
        return response_json["data"][0]["embedding"]
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        raise
    
