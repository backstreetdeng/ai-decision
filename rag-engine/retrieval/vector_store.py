import json
import psycopg2
from psycopg2.extras import RealDictCursor

from embedding import embedding_service


DB_CONFIG = {
    "host": "192.168.3.146",
    "port": 5432,
    "database": "vectordb",
    "user": "vectordb",
    "password": "vectordb123"
}


def get_connection():

    return psycopg2.connect(
        **DB_CONFIG,
        cursor_factory=RealDictCursor
    )

def search_documents(
    query: str,
    top_k: int = 10,
    metadata_filter: dict = None
):

    query_embedding = embedding_service.embed_query(query)

    conn = get_connection()

    cur = conn.cursor()

    sql = """
    SELECT
        c.id,
        c.content,
        c.source,
        c.brand,
        c.car_model,
        c.publish_date,
        c.metadata,
        c.page_number,
        d.file_name,

        1 - (c.embedding <=> %s::vector) AS score

    FROM chunks c

    LEFT JOIN documents d
    ON c.document_id = d.id

    ORDER BY c.embedding <=> %s::vector

    LIMIT %s;
    """

    cur.execute(
        sql,
        (
            query_embedding,
            query_embedding,
            top_k
        )
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    documents = []

    for row in rows:

        documents.append({
            "document": row["content"],

            "score": float(row["score"]),

            "metadata": {
                "chunk_id": row["id"],
                "source": row["source"],
                "brand": row["brand"],
                "car_model": row["car_model"],
                "publish_date": str(row["publish_date"]),
                "file_name": row["file_name"],
                "page_number": row["page_number"],
                "metadata": row["metadata"]
            }
        })

    return documents

def insert_chunk(chunks: list):
    """
    批量插入 chunk 到 chunks 表
    chunk 结构示例：
    {
        "document_id": int | None,
        "content": str,
        "embedding": list[float],  # 1024维
        "chunk_index": int,
        "source": str,
        "brand": str | None,
        "car_model": str | None,
        "publish_date": str | None,
        "metadata": dict,
        "page_number": str | None
    }
    """
    conn = get_connection()

    cur = conn.cursor()

    insert_sql = """
        INSERT INTO chunks (
            document_id, content, embedding, chunk_index,
            source, brand, car_model, publish_date, metadata, page_number
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for chunk in chunks:
        cur.execute(
            insert_sql,
            (
                chunk.get("document_id"),
                chunk.get("content"),
                chunk.get("embedding"),
                chunk.get("chunk_index", 0),
                chunk.get("source"),
                chunk.get("brand"),
                chunk.get("car_model"),
                chunk.get("publish_date"),
                json.dumps(chunk.get("metadata", {})),
                chunk.get("page_number")
            )
        )

    conn.commit()
    cur.close()
    conn.close()

def insert_chat_history(chats: list):
    conn = get_connection()

    cur = conn.cursor()

    insert_sql = """
        INSERT INTO chat_history (session_id, role, content)
        VALUES (%s, %s, %s)
    """

    for chat in chats:
        cur.execute(
            insert_sql,
            (
                chat.get("session_id"),
                chat.get("role"),
                chat.get("content")
            )
        )

    conn.commit()
    cur.close()
    conn.close()

