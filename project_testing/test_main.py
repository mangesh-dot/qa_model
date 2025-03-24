import pytest
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app
from database.database import check_conn


# Create a TestClient instance
client = TestClient(app)

# Test data
TEST_USER = {
    "username": "meher",
    "full_name": "meher nisha",
    "email": "meher@gmail.com",
    "password": "password"
}

# Helper function to get a valid token
def get_auth_token():
    # First, sign up the test user
    client.post("/signup/", json=TEST_USER)

    # Then, log in to get the token
    response = client.post("/login/", data={"username": TEST_USER["username"], "password": TEST_USER["password"]})

    return response.json()["access_token"]

# Test cases
def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running!"}

def test_signup():
    """Test the signup endpoint."""
    response = client.post("/signup/", json=TEST_USER)
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

def test_login():
    """Test the login endpoint."""
    # First, sign up the test user
    client.post("/signup/", json=TEST_USER)

    # Then, log in
    response = client.post("/login/", data={"username": TEST_USER["username"], "password": TEST_USER["password"]})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_store_document():
    """Test the document storage endpoint."""
    token = get_auth_token()

    # Create a sample text file
    files = {"file": ("test.txt", "This is a test document.")}

    # Send the request with the token
    response = client.post("/store/", files=files, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "stored successfully" in response.json()["message"]

def test_list_documents():
    """Test the document listing endpoint."""
    token = get_auth_token()

    # Send the request with the token
    response = client.get("/documents/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json()["documents"], list)

def test_ask_question():
    """Test the question-answering endpoint."""
    token = get_auth_token()

    # First, store a document
    files = {"file": ("test.txt", "This is a test document.")}
    client.post("/store/", files=files, headers={"Authorization": f"Bearer {token}"})

    # Then, ask a question
    response = client.get("/ask/", params={"query": "What is this document about?"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "answer" in response.json()

def test_check_connection():
    """Test the database connection check endpoint."""
    response = client.get("/check-connection/")
    assert response.status_code == 200
    assert response.json()["status"] in ["Connected", "Disconnected"]