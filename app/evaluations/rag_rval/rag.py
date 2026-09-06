from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings , ChatOpenAI
import os
from dotenv import load_dotenv
from pathlib import Path
from bm25s import BM25
import json
from app.services.rag.hybrid_search import hybrid_search_weighted_rrf
from hazm import Normalizer , word_tokenize
from app.services.rag.hybrid_search import rrf_score , semantic_retriever , normalizer , bm25 , corpus

import logging
logger = logging.getLogger(__name__)
load_dotenv()
base_url = os.getenv("BASE_URL_GAP")
api_key = os.getenv("GPT_API_KEY")
current_dir = Path(__file__).parent
CHROMA_DIR = current_dir / "chroma_db"

SEMANTIC_K = 10
BM25_K = 10
ALPHA = 0.6
RRF_K = 10



embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=api_key,
    base_url=base_url
)

def extract_chunk(
    message: str,
    k: int = 5,
    alpha: float = ALPHA
):


    semantic_docs = semantic_retriever.invoke(message)


    normalized_query = normalizer.normalize(message)
    tokenized_query = word_tokenize(normalized_query)

    results, scores = bm25.retrieve(
        [tokenized_query],
        k=BM25_K
    )

    keyword_indices = results[0]


    rrf_scores = {}

    for rank, doc in enumerate(
        semantic_docs,
        start=1
    ):
        chunk_index = corpus.index(doc.page_content)

        semantic_rrf = (
            alpha * rrf_score(rank)
        )

        rrf_scores[chunk_index] = (
            rrf_scores.get(chunk_index, 0)
            + semantic_rrf
        )

    for rank, chunk_index in enumerate(
        keyword_indices,
        start=1
    ):
        bm25_rrf = (
            (1 - alpha)
            * rrf_score(rank)
        )

        rrf_scores[chunk_index] = (
            rrf_scores.get(chunk_index, 0)
            + bm25_rrf
        )



    ranked_chunks = sorted(
        rrf_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )


    final_results = ranked_chunks[:k]


    chunk_indices = [
        chunk_index
        for chunk_index, score in final_results
    ]

    return chunk_indices

with open(f"{current_dir}/dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

with open("result_generation.txt", "w", encoding="utf-8") as result_file:

    for question in dataset:

        response = hybrid_search_weighted_rrf(
            question["question"]
        )

        result_file.write(
            f"Question: {question['question']}\n"
        )

        result_file.write(
            f"Retrieved answer: {response}\n\n"
        )
