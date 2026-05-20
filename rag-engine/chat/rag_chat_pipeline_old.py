from retrieval.retriever import retrieve
from rerank.rerank_service import rerank

from prompt.prompt_builder import build_prompt
from llm.answer_generator import generate_answer


def chat(question: str):

    # 1. retrieval
    retrieved_docs = retrieve(question)

    # 2. rerank
    reranked_docs = rerank(
        query=question,
        documents=retrieved_docs
    )

    # 3. topk
    # top_docs = reranked_docs[:5]
    # 优化
    top_docs = [
    doc
    for doc in reranked_docs
    if doc["score"] > 0
    ][:5]

    contexts = [
        doc["document"]
        for doc in top_docs
    ]

    # citation sources
    citations = []
    for doc in top_docs:

        # 注掉 chunk_id 企业不关注
        # citations.append({
        #     "file_name": doc["metadata"]["file_name"],
        #     "chunk_id": doc["metadata"]["chunk_id"],
        #     "score": doc["score"]
        # })
        citations.append({
            "file_name": doc["metadata"]["file_name"],
            "score": round(doc["score"], 2)
        })

    # 4. prompt
    prompt = build_prompt(
        question=question,
        contexts=contexts
    )

    # 5. llm
    answer = generate_answer(prompt)

    return {
        "question": question,
        "answer": answer,
        "contexts": contexts,
        "citations": citations
    }