import faiss
import numpy as np
from database.database import conn, cur  # Ensure both conn and cur are imported
from services.embeddings.embedding import generate_embedding  # Ensure this exists

import faiss
import numpy as np
from database.database import conn, cur  # Ensure database connection is imported
from services.embeddings.embedding import generate_embedding  # Ensure embedding function exists

def relevant_doc(query):
    """Retrieve the most relevant document using FAISS similarity search."""
    cur.execute("SELECT filename, content, embedding FROM documents") 
    rows = cur.fetchall()

    if not rows:
        return None  # No documents found

    embeddings = np.array([np.array(row[2], dtype=np.float32) for row in rows])  # Use  index for retriving embeddings

    # Creating FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    
    query_embedding = generate_embedding(query).reshape(1, -1)  # Generating query embedding

   
    _, idx = index.search(query_embedding, k=1)                  # Searching for best match

    best_match = rows[idx[0][0]]

    return {"filename": best_match[0], "content": best_match[1]}  # dictionary is returned


