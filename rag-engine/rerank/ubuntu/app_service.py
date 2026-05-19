from fastapi import FastAPI
from pydantic import BaseModel
from FlagEmbedding import FlagReranker

import logging


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


app = FastAPI()


# 模型只加载一次
logger.info("Loading reranker model...")

reranker = FlagReranker(
    "BAAI/bge-reranker-v2-m3",
    use_fp16=True,
    local_files_only=True
)

logger.info("Reranker loaded.")


class RerankRequest(BaseModel):

    query: str

    documents: list[str]

    top_k: int = 5


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post("/rerank")
def rerank(req: RerankRequest):

    pairs = [
        [req.query, doc]
        for doc in req.documents
    ]

    scores = reranker.compute_score(
        pairs,
        batch_size=16
    )

    results = []

    for doc, score in zip(req.documents, scores):

        results.append({
            "document": doc,
            "score": float(score)
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "results": results[:req.top_k]
    }