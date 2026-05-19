from retrieval.vector_store import search_documents

def retrieve(
    query: str,
    top_k: int = 10
):

    documents = search_documents(
        query=query,
        top_k=top_k
    )

    return documents