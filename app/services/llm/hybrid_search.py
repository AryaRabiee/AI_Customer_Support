from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
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
load_dotenv()
api_get_embedding = os.getenv("EMBEDDING_API_KEY")
current_dir = Path(__file__).parent
CHROMA_DIR = current_dir / "chroma_db"

SEMANTIC_K = 10
BM25_K = 10
ALPHA = 0.6
RRF_K = 10

# reranker = CrossEncoder(
#     "BAAI/bge-reranker-v2-m3",
# )


embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=api_get_embedding,
    base_url="https://openrouter.ai/api/v1"
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

print(f"✅ Corpus loaded: {len(corpus)} documents")

normalizer = Normalizer()

normalized_corpus = [
    normalizer.normalize(doc)
    for doc in corpus
]


tokenized_corpus = [
    word_tokenize(doc)
    for doc in normalized_corpus
]


print(f"✅ Corpus tokenized: {len(tokenized_corpus)} documents")
    
bm25 = BM25()

bm25.index(
    tokenized_corpus
)


print("✅ BM25S index is ready")
    

def rrf_score(rank: int,rrf_k: int = RRF_K):
    
    return 1.0 / (rrf_k + rank)

def hybrid_search_weighted_rrf(message: str,k: int = 5,alpha: float = ALPHA):

    semantic_docs = semantic_retriever.invoke(message)
        
    print(f"✅ Semantic results:{len(semantic_docs)}")

    normalized_query = normalizer.normalize(message)
    tokenized_query = word_tokenize(normalized_query)
        

    print(f"✅ Tokenized query:{tokenized_query}")


    results, scores = bm25.retrieve(
        [tokenized_query],
        k=BM25_K
    )
    print(f"resultss {results}")
    print(f"scores {scores}")
    keyword_indices = results[0]


    keyword_results = [
        corpus[index]
        for index in keyword_indices
    ]


    print(f"✅ BM25S results:{len(keyword_results)}")
        

    rrf_scores = {}


    for rank, doc in enumerate(semantic_docs,start=1):
        

        key = doc.page_content


        semantic_rrf = (alpha*rrf_score(rank))

        rrf_scores[key] = (rrf_scores.get(key,0)+semantic_rrf)



    for rank, text in enumerate(keyword_results,start=1):

        key = text


        bm25_rrf = ((1 - alpha)*rrf_score(rank))

        rrf_scores[key] = (rrf_scores.get(key,0)+bm25_rrf)

    ranked_docs = sorted(rrf_scores.items(),key=lambda item: item[1],reverse=True)
    # candidate_docs = ranked_docs[:10]
    # documents = [
    #     doc
    #     for doc, rrf_score in candidate_docs
    # ]

    # pairs = [
    #     (message, doc)
    #     for doc in documents
    # ]
    # rerank_scores = reranker.predict(pairs)
    # reranked_docs = list(
    #     zip(documents, rerank_scores)
    # )
    # reranked_docs.sort(
    #     key=lambda x: x[1],
    #     reverse=True
    # )
    # print(f"RRF Candidates: {len(candidate_docs)}")

    # print(f"RRF Score first is {rrf_scores}")
    final_results = ranked_docs[:5]
    print(f"✅ Final RRF results:{len(final_results)}documents")
    print(f"✅ RRF Scores:{final_results}documents") 


    context = "\n\n".join(
        f"[{i+1}] {doc}"
        for i, (doc, score) in enumerate(final_results)
    )




    prompt = f"""
تو یک پشتیبان مشتری حرفه‌ای برای شرکت آریا تک هستی.

Context:
{context}

سؤال:
{message}

اگر پاسخ سؤال در Context وجود ندارد، بگو:

«متأسفانه اطلاعات کافی برای پاسخ به این سؤال ندارم.»

پاسخ کوتاه و دقیق:
"""

    model = ChatOpenRouter(
        model="openai/gpt-oss-20b",
        api_key=api_get_embedding
    )

    for chunk in model.stream(prompt):
        if chunk.content:

            yield chunk.content