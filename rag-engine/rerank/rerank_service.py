import requests


RERANK_URL = "http://192.168.3.146:8082/rerank"


def rerank(
    query: str,
    documents: list[dict],
    top_k: int = 5
):

    doc_texts = [
        doc["document"]
        for doc in documents
    ]

    payload = {
        "query": query,
        "documents": doc_texts,
        "top_k": top_k
    }

    response = requests.post(
        RERANK_URL,
        json=payload,
        timeout=300
    )

    response.raise_for_status()

    rerank_results = response.json()

    reranked_docs = []

    for item in rerank_results["results"]:

        for original_doc in documents:

            if original_doc["document"] == item["document"]:

                reranked_docs.append({

                    "document": original_doc["document"],

                    "score": item["score"],

                    "metadata": original_doc["metadata"]

                })

                break

    return reranked_docs