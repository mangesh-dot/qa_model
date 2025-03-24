Q&A Project with FastAPI

This project is a FastAPI-based application that allows users to:
Upload documents.
Generate embeddings for the documents.
Perform retrieval-augmented generation (RAG) for question-answering.
Authenticate users and manage document access.

Features

User Authentication: Sign up, log in, and manage user sessions using JWT tokens.
Document Upload: Upload text documents and generate embeddings using a pre-trained model.
Question-Answering: Ask questions and get answers based on the uploaded documents.
Document Selection: Specify which documents should be considered for question-answering.

Technologies Used

Backend: FastAPI
Database: PostgreSQL
Embedding Model: Hugging Face Transformers (`all-MiniLM-L6-v2`)
Answering Model: Hugging Face Transformers (`bert-large-uncased-whole-word-masking-finetuned-squad`)
Vector Search: FAISS (Facebook AI Similarity Search)
Authentication: JWT (JSON Web Tokens)

Project Structure

Q&A_Project/
project_testing/
init.py
test_main.py
main.py
database/
init.py
database.py
services/
embeddings/
init.py
embedding.py
qa/
init.py
qa.py
retrieval/
init.py
retrieval.py
authentication/
init.py
auth.py
.env
requirements.txt
README.md




