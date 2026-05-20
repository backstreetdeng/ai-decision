import os
import logging 

from document_parser.pdf_parser import PDFParser
from chunker.text_chunker import TextChunker

from embedding.embedding_service import (
    EmbeddingService
)

from vectordb.pgvector_client import (
    PGVectorDB
)


class RAGPipeline:

    def __init__(self):
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.parser = PDFParser()

        self.chunker = TextChunker()

        self.embedding_service = EmbeddingService()

        self.vectordb = PGVectorDB()

    def ingest_pdf(
        self,
        file_path: str,
        source: str = None,
        brand: str = None,
        category: str = None,
        car_model: str = None,
        publish_date=None
    ):

        print("1. 开始解析 PDF...")

        text = self.parser.parse(file_path)

        print("2. 开始 Chunk...")

        chunks = self.chunker.split_text(text)

        print(f"Chunk 数量: {len(chunks)}")

        print("3. 开始 Embedding...")

        embeddings = self.embedding_service.embed_documents(
            chunks
        )

        print("4. 写入 documents 表...")

        file_name = os.path.basename(file_path)

        document_id = self.vectordb.insert_document(
            file_name=file_name,
            source=source,
            brand=brand,
            category=category
        )

        print(f"document_id: {document_id}")

        print("5. 写入 chunks 表...")

        self.vectordb.add_chunks(
            document_id=document_id,
            chunks=chunks,
            embeddings=embeddings,
            source=source,
            brand=brand,
            car_model=car_model,
            publish_date=publish_date
        )

        print("知识库写入完成")

    def search(
        self,
        query: str,
        top_k=3
    ):

        print(f"print输出：开始向量检索...{query}")
        # self.logger.info(f"log输出：开始向量检索... {query}")

        query_embedding = (
            self.embedding_service.embed_query(
                query
            )
        )

        results = self.vectordb.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k
        )

        return results