from retrieval.retriever import retrieve
from rerank.rerank_service import rerank

from prompt.prompt_builder import build_prompt
from llm.answer_generator import generate_answer, generate_answer_stream
from retrieval.vector_store import insert_chunk, insert_chat_history # 用于 chat memory 入库
from embedding.embedding_service import EmbeddingService

embedding_service = EmbeddingService()

def save_chat(session_id: str, role: str, text: str):
    """
    保存用户或系统对话到向量库和chat_history表，实现 Chat Memory
    """
    if not text.strip():
        return  # 空文本不入库
    
    # 向量化文件
    vector = embedding_service.embed_query(text)
    chunk = {
        "document_id": None,
        "content": text,
        "embedding": vector,
        "chunk_index": 0,
        "source": "chat_memory",
        "brand": None,
        "car_model": None,
        "publish_date": None,
        "metadata": {"role": role, "session_id": session_id},
        "page_number": None
    }
    # 保存到 chunk 表
    insert_chunk([chunk])

    # 保存到 chat_history 表
    chat = {
        "session_id": session_id,
        "role": role,
        "content": text
    }
    insert_chat_history([chat])

def retrieve_chat_history(session_id: str, top_k: int = 5):
    """
    从向量库检索该 session 最近对话
    """
    if not session_id:
        return []

    raw_results = retrieve(
        query=session_id,  # 用 session_id 避免空文本
        top_k=top_k,
        metadata_filter={"source": "chat_memory", "session_id": session_id}
    )

    # 只保留 chat_memory 且 session_id 匹配
    filtered = [
        doc for doc in raw_results
        if doc["metadata"].get("source") == "chat_memory"
        and doc["metadata"].get("session_id") == session_id
    ]
    # 返回文本列表
    return [doc["document"] for doc in filtered[:top_k]]

def chat(
        question: str,
        session_id: str = None, 
        top_k: int = 5,
        score_threshold: float = 0, 
        metadata_filter: dict = None,  # {"brand": "Tesla", "car_model": "Model Y"}
        stream: bool = False
    ):
    """
    企业级 RAG Chat
    返回：
    - question: 用户问题
    - answer: LLM 回答 （支持 stream）
    - contexts: top_k 上下文
    - Metadata Filter（单值、多值、模糊匹配）
    - Rerank 保留 metadata + score    
    - citations: 可追踪来源，包含 file_name + page_number + score
    """
    # 0. 保存用户问题到 Chat Memory
    if session_id:
        save_chat(session_id, "user", question)

    # 1. Retrieval
    retrieved_docs = retrieve(question, top_k=15)

    # for d in retrieved_docs:
    #     print(d["document"][:50], d["metadata"])

    # 2. Metadata Filter
    if metadata_filter:
        filtered_docs = []
        for doc in retrieved_docs:
            match = True
            for key, value in metadata_filter.items():
                meta_val = doc["metadata"].get(key)

                if meta_val is None:
                    match = False
                    break

                # 多值匹配
                if isinstance(value, list):
                    if meta_val not in value:
                        match = False
                        break

                # 字符串模糊匹配
                elif isinstance(value, str):
                    if value.lower() not in str(meta_val).lower():
                        match = False
                        break

                # 精确匹配
                else:
                    if meta_val != value:
                        match = False
                        break

            if match:
                filtered_docs.append(doc)

        retrieved_docs = filtered_docs

    # 2.1 Chat Memory 上下文注入    
    if session_id:
        history_contexts = retrieve_chat_history(session_id, top_k=5)
        retrieved_docs.extend([
            {"document": ctx, "metadata": {"source": "chat_memory"}, "score": 0.0}
            for ctx in history_contexts
        ])          

    if not retrieved_docs:
        return {
            "question": question,
            "answer": "没有检索到相关内容",
            "contexts": [],
            "citations": []
        }

    # 3. rerank
    reranked_docs = rerank(query=question, documents=retrieved_docs, top_k=top_k)

    # 4. topk
    # 只保留 score > score_threshold 的 chunk
    top_docs = [
    {
        "document": doc["document"],
        "metadata": doc["metadata"],
        "score": doc["score"]
    }
    for doc in reranked_docs
    if doc["score"] > score_threshold
    ][:top_k]

    # 5. Prompt Assemble
    contexts = [doc["document"] for doc in top_docs]
    prompt = build_prompt(question=question, contexts=contexts)
    
    # 6. LLM Answer
    if stream:
        answer_tokens = []
        for token in generate_answer_stream(prompt):
            print(token, end="", flush=True)  # 实时输出
            answer_tokens.append(token)
        answer = "".join(answer_tokens)
    else:
        answer = generate_answer(prompt)

    # 6.1 保存系统回答到 Chat Memory
    if session_id:
        save_chat(session_id, "assistant", answer)

    # 7. Citation 输出
    citations = []
    for doc in top_docs:
        citations.append({
            "file_name": doc["metadata"]["file_name"],
            "page_number": doc["metadata"].get("page_number"),
            "score": round(doc["score"], 2)
        })

    return {
        "question": question,
        "answer": answer,
        "contexts": contexts,
        "citations": citations
    }

# ============================
# 使用示例
if __name__ == "__main__":
    session_id = "deng"
    result = chat(
        question="Model Y 电池保修多久",
        session_id=session_id,
        metadata_filter={"brand": "Tesla", "car_model": "Model Y"},
        stream=True
    )

    print("\n========== ANSWER ==========\n")
    print(result["answer"])

    print("\n========== CITATIONS ==========\n")
    for c in result["citations"]:
        print(f"{c['file_name']} 第{c['page_number']}页 (score: {c['score']})")