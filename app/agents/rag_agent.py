from graph.state import SupportState
from services.rag.hybrid_search import hybrid_search_weighted_rrf


def rag_node(state: SupportState):

    chunks = []

    for chunk in hybrid_search_weighted_rrf(
        state["user_message"]
    ):
        if chunk:
            chunks.append(chunk)

    answer = "".join(chunks)

    print("RAG ANSWER:", answer)

    return {
        "response": answer
    }