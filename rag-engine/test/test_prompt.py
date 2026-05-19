from retrieval.retriever import retrieve
from rerank.rerank_service import rerank
from prompt.prompt_builder import build_prompt


query = "Model Y 电池保修多久"


retrieved_docs = retrieve(query)

reranked_docs = rerank(
    query=query,
    documents=retrieved_docs
)

contexts = [
    doc["document"]
    for doc in reranked_docs[:5]
]

prompt = build_prompt(
    question=query,
    contexts=contexts
)

print(prompt)