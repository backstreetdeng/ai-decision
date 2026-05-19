from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    MODEL_NAME: str = "BAAI/bge-reranker-v2-m3"

    USE_FP16: bool = True

    BATCH_SIZE: int = 16


settings = Settings()