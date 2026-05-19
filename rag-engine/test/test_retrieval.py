from retrieval.retriever import retrieve


query = "Model Y 电池保修多久"

results = retrieve(query, top_k=5)

print("\n========== RETRIEVAL ==========\n")

for idx, item in enumerate(results):

    print(f"\n--- TOP {idx+1} ---")

    print("score:", item["score"])

    print("source:", item["metadata"]["file_name"])

    print("content:")

    print(item["document"][:500])