from retrieval.vector_store import search_documents

def retrieve(query: str, top_k: int = 10, metadata_filter: dict = None):
    """
    企业级 Retriever
    返回：
    [
        {
            "document": chunk text,
            "metadata": {
                "file_name": str,
                "page_number": int,
                "source": str,
                "brand": str,
                "car_model": str,
                "publish_date": str
            }
        }
    ]
    """

    # search_documents 返回的每个 item 应该包含:
    # content, metadata (metadata 里可以是 file_name, page_number 等)
    raw_results = search_documents(query=query, top_k=top_k, metadata_filter=metadata_filter)

    # print(f"******result******:{raw_results[:3]}")

    results = []
    for row in raw_results:
        # row 应该包含 'document', 'metadata', 'score'
        results.append({
            "document": row["document"],
            "metadata": {
                "file_name": row["metadata"].get("file_name"),
                "page_number": row["metadata"].get("page_number"),
                "source": row["metadata"].get("source"),
                "brand": row["metadata"].get("brand"),
                "car_model": row["metadata"].get("car_model"),
                "publish_date": row["metadata"].get("publish_date")
            },
            "score": row.get("score", 0)  # 如果需要默认 0
        })

    return results