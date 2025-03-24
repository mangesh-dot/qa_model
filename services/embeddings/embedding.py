from sentence_transformers import SentenceTransformer
import numpy as np
from database.database import save_embedding  


model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text, filename=None):
    embedding = np.array(model.encode(text)) 
    if filename:  # Only save if filename is provided done this ensure query is not saved
        save_embedding(filename, embedding.tolist())  
    return embedding