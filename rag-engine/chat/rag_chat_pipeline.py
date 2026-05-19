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
    top_docs = reranked_docs[:5]

    contexts = [
        doc["document"]
        for doc in top_docs
    ]

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
        "contexts": contexts
    }