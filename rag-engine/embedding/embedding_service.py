from ollama import Client
from typing import List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


logger = logging.getLogger(__name__)


class EmbeddingService:

    def __init__(
        self,
        host: str = "http://192.168.3.146:11434",
        model_name: str = "quentinz/bge-large-zh-v1.5"
    ):

        self.client = Client(host=host)

        self.model_name = model_name

        logger.info(f"Embedding model: {model_name}")
        logger.info(f"Ollama host: {host}")

    def embed_query(
        self,
        text: str
    ) -> List[float]:

        try:

            response = self.client.embed(
                model=self.model_name,
                input=text
            )

            return response["embeddings"][0]

        except Exception as e:

            logger.exception("Embedding query failed")

            raise RuntimeError(
                f"Embedding query failed: {e}"
            )

    def embed_documents(
        self,
        texts: List[str],
        max_workers: int = 10
    ) -> List[List[float]]:

        embeddings = [None] * len(texts)

        failed_count = 0

        def embed_single(idx: int, text: str):

            try:

                vector = self.embed_query(text)

                return idx, vector

            except Exception as e:

                logger.error(
                    f"Embedding failed at index {idx}: {e}"
                )

                return idx, None

        with ThreadPoolExecutor(
            max_workers=max_workers
        ) as executor:

            futures = [
                executor.submit(embed_single, i, text)
                for i, text in enumerate(texts)
            ]

            for future in as_completed(futures):

                idx, vector = future.result()

                embeddings[idx] = vector

                if vector is None:
                    failed_count += 1

        logger.info(
            f"Embedding completed. "
            f"total={len(texts)}, "
            f"failed={failed_count}"
        )

        return embeddings