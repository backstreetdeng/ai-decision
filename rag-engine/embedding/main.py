from fastapi import FastAPI

from rag-engine.embedding.routers.embedding_router import (
    router
)

app = FastAPI(
    title="embedding-service"
)

app.include_router(router)