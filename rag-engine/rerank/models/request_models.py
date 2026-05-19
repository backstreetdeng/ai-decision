from pydantic import BaseModel
from typing import List


class RerankRequest(BaseModel):

    query: str

    documents: List[str]

    top_k: int = 5