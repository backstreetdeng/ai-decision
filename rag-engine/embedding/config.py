from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    MODEL_NAME: str = "BAAI/bge-large-zh-v1.5"

    USE_FP16: bool = True

    MAX_LENGTH: int = 512

    BATCH_SIZE: int = 8


settings = Settings()