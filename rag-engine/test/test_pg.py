import psycopg2

from pgvector.psycopg2 import register_vector


conn = psycopg2.connect(
    host="192.168.3.146",
    port=5432,
    database="vectordb",
    user="vectordb",
    password="vectordb123"
)

register_vector(conn)

print("pgvector ok")