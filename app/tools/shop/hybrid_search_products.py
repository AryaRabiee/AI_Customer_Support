from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings , ChatOpenAI
from langchain_openrouter import ChatOpenRouter
from langchain_chroma import Chroma
from langchain.agents import create_agent
import os
from langchain.messages import HumanMessage , SystemMessage
from dotenv import load_dotenv
from pathlib import Path
from rank_bm25 import BM25Okapi
from bm25s import BM25
from hazm import Normalizer , word_tokenize
from sentence_transformers import CrossEncoder
import logging
logger = logging.getLogger(__name__)
load_dotenv()
api_get_embedding = os.getenv("EMBEDDING_KEY")
api_key = os.getenv("QWEN_GAPGPT_KEY")
base_url = os.getenv("BASE_URL_GAP")
current_dir = Path(__file__).parent
CHROMA_DIR = current_dir / "chroma_db"

SEMANTIC_K = 10
BM25_K = 10
ALPHA = 0.6
RRF_K = 10


embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=api_get_embedding,
    base_url=base_url
)

vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings
)


all_docs = vectorstore.get()

corpus = all_docs["documents"]

logger.info(
    "Product corpus loaded | documents=%s",
    len(corpus)
)




normalizer = Normalizer()

normalized_corpus = [
    normalizer.normalize(doc)
    for doc in corpus
]

tokenized_corpus = [
    word_tokenize(doc)
    for doc in normalized_corpus
]

bm25 = BM25()

bm25.index(tokenized_corpus)

logger.info("Product BM25 index is ready")


# -----------------------------
# RRF
# -----------------------------

def rrf_score(rank: int, rrf_k: int = RRF_K):
    return 1.0 / (rrf_k + rank)




def hybrid_search_products(
    message: str,
    products: list,
    k: int = 5,
    alpha: float = ALPHA
):

    logger.info(
        "Starting product hybrid search | candidates=%s",
        len(products)
    )

    candidate_names = {
        product["name"]
        for product in products
    }

    logger.info(
        "Candidate products: %s",
        candidate_names
    )


    candidate_docs = []

    for doc in corpus:

        if any(
            product_name in doc
            for product_name in candidate_names
        ):
            candidate_docs.append(doc)

    logger.info(
        "Candidate documents found: %s",
        len(candidate_docs)
    )


    if not candidate_docs:
        return []



    semantic_retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": SEMANTIC_K
        }
    )

    semantic_docs = semantic_retriever.invoke(message)


    semantic_results = [
        doc.page_content
        for doc in semantic_docs
        if any(
            product_name in doc.page_content
            for product_name in candidate_names
        )
    ]

    logger.info(
        "Semantic retrieval completed | documents=%s",
        len(semantic_results)
    )

    normalized_query = normalizer.normalize(message)

    tokenized_query = word_tokenize(normalized_query)

    results, scores = bm25.retrieve(
        [tokenized_query],
        k=min(BM25_K, len(corpus))
    )

    keyword_indices = results[0]

    keyword_results = [
        corpus[index]
        for index in keyword_indices
        if corpus[index] in candidate_docs
    ]

    logger.info(
        "BM25 retrieval completed | documents=%s",
        len(keyword_results)
    )


    rrf_scores = {}


    for rank, doc in enumerate(
        semantic_results,
        start=1
    ):

        score = alpha * rrf_score(rank)

        rrf_scores[doc] = (
            rrf_scores.get(doc, 0) + score
        )


    for rank, doc in enumerate(
        keyword_results,
        start=1
    ):

        score = (1 - alpha) * rrf_score(rank)

        rrf_scores[doc] = (
            rrf_scores.get(doc, 0) + score
        )

    ranked_docs = sorted(
        rrf_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )


    for rank, (doc, score) in enumerate(
        ranked_docs,
        start=1
    ):

        logger.info(
            "PRODUCT RRF | rank=%d | score=%.6f | doc=%s",
            rank,
            score,
            doc[:100].replace("\n", " ")
        )


    final_results = ranked_docs[:k]


    logger.info(
        "Final product results: %s",
        len(final_results)
    )


    context = "\n\n".join(
        f"[{i + 1}] {doc}"
        for i, (doc, score)
        in enumerate(final_results)
    )


    prompt = f"""
تو یک دستیار حرفه‌ای فروش برای یک فروشگاه آنلاین هستی.

وظیفه تو این است که بر اساس محصولات موجود در Context
به درخواست کاربر پاسخ بدهی.

قوانین:

- فقط از اطلاعات موجود در Context استفاده کن.
- اطلاعاتی که در Context وجود ندارد را حدس نزن.
- محصولی خارج از Context پیشنهاد نده.
- اگر هیچ محصول مناسبی در Context وجود ندارد، صادقانه بگو
  که محصول مناسبی پیدا نشد.
- پاسخ را کوتاه، طبیعی و به زبان فارسی بده.
- اگر چند محصول مناسب وجود دارد، آنها را به کاربر معرفی کن.
- قیمت یا مشخصات محصول را فقط در صورتی بیان کن که در Context وجود داشته باشد.

Context:

{context}

درخواست کاربر:

{message}

پاسخ:
"""


    model = ChatOpenAI(
        model="gemma-3-27b-it",
        api_key=api_key,
        base_url=base_url
    )


    response = ""

    for chunk in model.stream(prompt):

        if chunk.content:
            response += chunk.content


    return response