from app.graph.state import SupportState
from app.services.rag.hybrid_search import hybrid_search_weighted_rrf
from langchain_core.messages import AIMessage
import logging

logger = logging.getLogger(__name__)

def rag_node(state: SupportState):

    chunks = []

    for chunk in hybrid_search_weighted_rrf(
        state["user_message"],
    ):
        if chunk:
            chunks.append(chunk)

    answer = "".join(chunks)


    return {
        "messages": [
            AIMessage(content=answer)
        ],
        "response": answer
    }