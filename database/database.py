import psycopg2
from psycopg2.extras import Json
import numpy as np

# Database Connection
DATABASE_URL="dbname='QandA' user='postgres' host='localhost' password='password'"




try:
    conn = psycopg2.connect(DATABASE_URL)  # psycopg2 helps in mking connection with DB 
    cur = conn.cursor()  # cursor helps in executing the queries in DB
    print("DB connected.")
except Exception as e:
    print(f" DB connection error: {e}")
    conn = None  




def save_embedding(filename, content, embedding):   # saving data into DB
    """Save filename, content, and embedding into PostgreSQL."""
    try:
        if conn is None:
            raise Exception("Database connection is not established.")

       
        embedding_json = Json(embedding.tolist() if isinstance(embedding, np.ndarray) else embedding)

        cur.execute(
            """
            INSERT INTO documents (filename, content, embedding) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (filename) 
            DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding
            """,
            (filename, content, embedding_json)
        )
        conn.commit()
        print(f"Embedding saved for {filename}")

    except Exception as e:
        conn.rollback()
        print(f" Error saving embedding: {e}")





import psycopg2
from psycopg2.extras import RealDictCursor



def check_conn():
    """Return database connection if successful, else None"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn  #  Return actual connection object
    except Exception as e:
        print(" DB connection failed:", e)
        return None  #  Return `None` instead of `False`
