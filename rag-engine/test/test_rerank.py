from retrieval.retriever import retrieve
from rerank.rerank_service import rerank


query = "Model Y 电池保修多久"


retrieved_docs = retrieve(query, top_k=10)

print("\n========== BEFORE RERANK ==========\n")

for idx, item in enumerate(retrieved_docs):

    print(f"TOP {idx+1}")
    print(item["document"][:200])
    print()


reranked_docs = rerank(
    query=query,
    documents=retrieved_docs,
    top_k=5
)

print("\n========== AFTER RERANK ==========\n")

for idx, item in enumerate(reranked_docs):

    print(f"TOP {idx+1}")
    print("score:", item["score"])
    print(item["document"][:200])
    print()