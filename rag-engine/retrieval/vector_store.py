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
    top_k: int = 10
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