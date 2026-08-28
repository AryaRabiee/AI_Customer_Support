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

semantic_retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": SEMANTIC_K
    }
)

all_docs = vectorstore.get()

corpus = all_docs["documents"]
logger.info("Corpus loaded %s" ,{len(corpus)} )

normalizer = Normalizer()

normalized_corpus = [
    normalizer.normalize(doc)
    for doc in corpus
]

tokenized_corpus = [
    word_tokenize(doc)
    for doc in normalized_corpus
]
logger.info("Corpus tokenized: %s" ,len(tokenized_corpus) )

bm25 = BM25()

bm25.index(
    tokenized_corpus
)
logger.info(" BM25S index is ready")

def rrf_score(rank: int, rrf_k: int = 60):
    return 1.0 / (rrf_k + rank)


def hybrid_search_weighted_rrf(
    message: str,
    k: int = 5,
    alpha: float = 0.7
):


    semantic_docs = semantic_retriever.invoke(message)
    
    logger.info(
    "Semantic retrieval completed | documents=%s",
    len(semantic_docs)
)



    normalized_query = normalizer.normalize(message)

    tokenized_query = word_tokenize(normalized_query)

    logger.info(
    "BM25 tokenized query: %s",
    tokenized_query
)

    results, scores = bm25.retrieve(
        [tokenized_query],
        k=BM25_K
     )

    keyword_indices = results[0]

    keyword_results = [
        corpus[index]
        for index in keyword_indices
    ]

    logger.info(
    "BM25 retrieval completed | documents=%s",
    len(keyword_results)
)



    rrf_scores = {}

    for rank, doc in enumerate(semantic_docs, start=1):

        key = doc.page_content

        semantic_rrf = alpha * rrf_score(rank)

        rrf_scores[key] = (
            rrf_scores.get(key, 0) + semantic_rrf
        )


    for rank, text in enumerate(keyword_results, start=1):

        key = text

        bm25_rrf = (1 - alpha) * rrf_score(rank)

        rrf_scores[key] = (
            rrf_scores.get(key, 0) + bm25_rrf
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
            "RRF FINAL CANDIDATE | rank=%d | score=%.6f | doc=%s",
            rank,
            score,
            doc[:100].replace("\n", " ")
        )
    final_results = ranked_docs[:k]
    logger.info(
        "RAG retrieval completed | documents=%s",
        len(final_results)
    )
    
    logger.info(
        "RRF scores: %s",
        final_results
    )



    context = "\n\n".join(
        f"[{i+1}] {doc}"
        for i, (doc, score) in enumerate(final_results)
    )


    prompt = f"""
تو یک پشتیبان مشتری حرفه‌ای برای شرکت آریا تک هستی.

وظیفه تو این است که بر اساس Context به سؤال کاربر پاسخ بدهی.

قوانین:
- فقط بر اساس اطلاعات موجود در Context پاسخ بده.
- اطلاعاتی که در Context وجود ندارد را حدس نزن.
- اگر پاسخ سؤال در Context وجود ندارد، دقیقاً بگو:

- پاسخ کوتاه، دقیق و طبیعی باشد.
- به زبان فارسی پاسخ بده.

Context:
{context}

سؤال کاربر:
{message}

پاسخ:
"""


    model = ChatOpenAI(
        model = "gemma-3-27b-it",
        api_key=api_key,
        base_url=base_url
    )

    for chunk in model.stream(prompt):

        if chunk.content:
            yield chunk.content


