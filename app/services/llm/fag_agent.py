from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_openrouter import ChatOpenRouter
from langchain_chroma import Chroma
from langchain.agents import create_agent
import os
from langchain.messages import HumanMessage , SystemMessage
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()
api_get_embedding = os.getenv("EMBEDDING_API_KEY")
current_dir = Path(__file__).parent

def rag_agent(message: str):
    print("Start Embedding")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_get_embedding,
        base_url="https://openrouter.ai/api/v1"
    )
    print(f"embedding is" , embeddings)
    vectorstore = Chroma(
        persist_directory=current_dir / "chroma_db",
        embedding_function=embeddings
    )
    print("Chroma document count:", vectorstore._collection.count())
    print(f"vectorstore is" , vectorstore)
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )
    print(f"retriever is" , retriever)
    docs = retriever.invoke(message)
    print(f"docs is" , docs)
    print(f"✅ {len(docs)} سند مرتبط پیدا شد")

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    prompt = f"""
تو یک پشتیبان مشتری حرفه‌ای برای شرکت آریا تک هستی.

فقط بر اساس Context زیر پاسخ بده.

Context:
{context}

سؤال مشتری:
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
