from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from database.database import check_conn
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to the console
        logging.FileHandler("app.log")  # Log to a file
    ]
)

# Create a logger instance
logger = logging.getLogger(__name__)

# adding Secret Key for JWT
SECRET_KEY = "avc5vg7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

# Password Hashing for security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_user(username: str):
    conn = check_conn()
    if conn:
        try:
            cur = conn.cursor()
            logger.debug(f"Checking for username: '{username}'")

            cur.execute("SELECT id, username, full_name, email, hashed_password FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
            logger.debug(f"Fetched row: {row}")

            if row is None:
                logger.warning(f"No user found for username: {username}")
                return None

            # Access columns by name 
            return {
                "id": row["id"],
                "username": row["username"],
                "full_name": row["full_name"],
                "email": row["email"],
                "hashed_password": row["hashed_password"]
            }
        except Exception as e:
            logger.error(f"Error fetching user: {str(e)}")  
            return None
        finally:
            conn.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        logger.warning(f"Authentication failed for username: {username}")
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user = get_user(username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return {"username": user["username"], "full_name": user["full_name"], "email": user["email"]}
    
    except JWTError as e:
        logger.error(f"JWT Error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired")