from fastapi import APIRouter, HTTPException

from rag-engine.embedding.models.request_models import (
    EmbeddingRequest
)

from rag-engine.embedding.services.embedding_service import (
    embedding_service
)

from rag-engine.embedding.utils.logger import logger


router = APIRouter()


@router.get("/health")
def health():

    return {
        "status": "ok"
    }


@router.post("/embed")
def embed(req: EmbeddingRequest):

    try:

        logger.info(
            f"Embedding request: {len(req.texts)} texts"
        )

        embeddings = embedding_service.embed(
            req.texts
        )

        return {
            "count": len(embeddings),
            "embeddings": embeddings.tolist()
        }

    except Exception as e:

        logger.exception("Embedding failed")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )