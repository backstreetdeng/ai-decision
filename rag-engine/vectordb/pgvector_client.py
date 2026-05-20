import json
import psycopg2
from psycopg2.extras import execute_values

from pgvector.psycopg2 import register_vector


class PGVectorDB:

    def __init__(self):

        self.conn = psycopg2.connect(
            host="192.168.3.146",
            port=5432,
            database="vectordb",
            user="vectordb",
            password="vectordb123"
        )

        register_vector(self.conn)

        self.cursor = self.conn.cursor()

        print("PGVector connected")

    def insert_document(
        self,
        file_name,
        source=None,
        brand=None,
        category=None
    ):
        """
        写入 documents 表
        """

        self.cursor.execute(
            """
            INSERT INTO documents
            (
                file_name,
                source,
                brand,
                category
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                file_name,
                source,
                brand,
                category
            )
        )

        document_id = self.cursor.fetchone()[0]

        self.conn.commit()

        return document_id

    def add_chunks(
        self,
        document_id,
        chunks,
        embeddings,
        source=None,
        brand=None,
        car_model=None,
        publish_date=None
    ):
        """
        批量写入 chunks 表，支持 page_number
        chunks 现在每个元素是 dict: {"content": str, "page_number": int}
        embeddings 对应每个 chunk 的向量
        """

        values = [
            (
                document_id,
                chunk["content"],
                embedding,
                idx,
                source,
                brand,
                car_model,
                publish_date,
                chunk.get("page_number"),  # 新增字段
                json.dumps({})             # metadata 保留空结构，未来可扩展
            )
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]

        execute_values(
            self.cursor,
            """
            INSERT INTO chunks
            (
                document_id,
                content,
                embedding,
                chunk_index,
                source,
                brand,
                car_model,
                publish_date,
                page_number,
                metadata
            )
            VALUES %s
            """,
            values
        )

        self.conn.commit()

    def similarity_search(
        self,
        query_embedding,
        top_k=3
    ):
        """
        向量相似度检索
        """

        self.cursor.execute(
            """
            SELECT
                id,
                content,
                metadata,
                page_number,
                embedding <=> %s::vector AS distance
            FROM chunks
            ORDER BY distance
            LIMIT %s
            """,
            (
                query_embedding,
                top_k
            )
        )

        results = self.cursor.fetchall()

        return results