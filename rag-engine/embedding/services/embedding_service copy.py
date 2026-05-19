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
        """
        Ollama Embedding Service

        Args:
            host: Ollama 服务地址
            model_name: embedding 模型名
        """

        self.client = Client(host=host)
        self.model_name = model_name

        logger.info(f"Embedding model connected: {model_name}")
        logger.info(f"Ollama host: {host}")

    def embed_query(self, text: str) -> List[float]:
        """
        单条文本向量化
        """

        try:

            response = self.client.embeddings(
                model=self.model_name,
                prompt=text
            )

            return response["embedding"]

        except Exception as e:

            logger.error(f"Embedding query failed: {e}")

            raise

    def embed_documents(
        self,
        texts: List[str],
        max_workers: int = 10
    ) -> List[List[float]]:
        """
        批量文本向量化（并发）

        Args:
            texts: 文本列表
            max_workers: 最大并发数，默认10
        """

        embeddings = [None] * len(texts)
        failed_count = [0]

        def embed_single(args):
            idx, text = args
            try:
                return idx, self.embed_query(text)
            except Exception as e:
                logger.error(f"Embedding failed at index {idx}: {e}")
                failed_count[0] += 1
                return idx, None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(embed_single, (i, text)): i
                for i, text in enumerate(texts)
            }

            for future in as_completed(futures):
                idx, vector = future.result()
                if vector is not None:
                    embeddings[idx] = vector

        if failed_count[0] > 0:
            logger.warning(f"{failed_count[0]} chunks failed to embed")

        return embeddings