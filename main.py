from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import  OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from services.embeddings.embedding import generate_embedding
from services.retrieval.retrieval import relevant_doc
from database.database import check_conn, save_embedding
from services.qa.qa import ask_llm
from authentication.auth import get_current_user


app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/")
async def health():
    """Check if API is running"""
    return {"message": "API is running!"}


class UserCreate(BaseModel):  # for type checking
    username: str
    full_name: str
    email: str
    password: str

@app.post("/signup/")
async def signup(user: UserCreate):
    """Register a new user in PostgreSQL"""
    conn = check_conn()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (user.username, user.email))
        existing_user = cur.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already exists")

        hashed_password = pwd_context.hash(user.password)  # Hash the password before storing
        cur.execute(
            "INSERT INTO users (username, full_name, email, hashed_password) VALUES (%s, %s, %s, %s)",
            (user.username, user.full_name, user.email, hashed_password)
        )
        conn.commit()
        conn.close()
        return {"message": "User registered successfully"}
    


from authentication.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

@app.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}


 



@app.post("/store/")
async def generate_embedding_document(file: UploadFile = File(...)):
    """Generate embedding for uploaded file and save to database"""
    try:
        if not file.filename.endswith(".txt"):
            raise HTTPException(status_code=400,detail="onlt text file allowed")
        
        text = (await file.read()).decode("utf-8")  

        filename = file.filename
        embedding = generate_embedding(text)  
        
        # saving in DB
        save_embedding(filename, text, embedding)

        return {"message": f" {filename} stored successfully", "embedding": embedding.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {e}")


@app.get("/documents/")
async def list_documents(current_user: dict = Depends(get_current_user)):
    """List all documents uploaded by the authenticated user"""
    conn = check_conn()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT filename FROM documents")
        files = [row[0] for row in cur.fetchall()]
        conn.close()
        return {"documents": files}
    raise HTTPException(status_code=500, detail="Could not fetch documents")


@app.get("/check-connection/")
async def check_connection():
    """Check if the database connection is active"""
    status = check_conn()
    return {"status": "Connected" if status else "Disconnected"}








@app.get("/ask/")
async def ask_question(query: str, current_user: dict = Depends(get_current_user)):
    try:
        print(f"Query received: {query}")

        # Retreving the most relevant document
        doc = relevant_doc(query) 

        if not doc or not doc.get("content"):  # Check if content exists
            return {"answer": "No relevant documents found."}

        
        doc_content = doc["content"]

       
        ans = ask_llm(query, doc_content)

        print(f"Answer fetched: {ans}")
        return {"answer": ans}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")




