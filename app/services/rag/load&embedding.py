from langchain_community.document_loaders import TextLoader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import os
from langchain_chroma import Chroma
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()
api_get_embedding = os.getenv("EMBEDDING_KEY")
base_url = os.getenv("BASE_URL_GAP")
current_dir = Path(__file__).parent
file_path = current_dir / "docs.txt"
def embedding_docs(file):

    
    loader = TextLoader(str(file), encoding="utf-8")
    text = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        separators=["\n# ", "\n\n", "\n"],
        chunk_size=950,
        chunk_overlap=100,
        keep_separator=True
    )
    docs = splitter.split_documents(text)
    logger.info(
    "Chunking completed | chunks=%s",
    len(docs)
)
    
    for i, doc in enumerate(docs[:5]):
        lines = doc.page_content.split('\n')
        header = lines[0] if lines[0].startswith('#') else lines[0][:50]
        print(f"  {i}: {len(doc.page_content):4d} chars | {header}")
    print()
    
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_get_embedding,
        base_url=base_url
    )
    
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("Finished succesfully")
    return vector_store, docs


docs = embedding_docs(file_path)