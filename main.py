import os, composio, json, api.components.evaluate as evaluate
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from composio_crewai import ComposioToolSet, Action, App
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional, List
from uuid import uuid4
from vercel_kv_sdk import KV
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone

composio.LogLevel.ERROR

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://influ-crew-frontend.vercel.app"],  # Ensure this URL is correct
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Vercel KV setup
kv = KV()

# Security
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Pydantic models
class User(BaseModel):
    username: str
    email: str
    entity_id: str

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class AuthResponse(BaseModel):
    message: str
    auth_url: Optional[str] = None

class SignUpRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AnalysisRequest(BaseModel):
    keyword: str
    channels: int

class AnalysisResponse(BaseModel):
    message: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    user_data = kv.get(f"user:{username}")
    if user_data:
        return UserInDB(**json.loads(user_data))
    
def get_user_by_email(email: str):
    all_users_json = kv.get("all_users")
    if all_users_json:
        all_users = json.loads(all_users_json)
        for username in all_users:
            user_data = kv.get(f"user:{username}")
            if user_data:
                user = UserInDB(**json.loads(user_data))
                if user.email == email:
                    return user
    return None

def get_all_users() -> List[str]:
    all_users_json = kv.get("all_users")
    return json.loads(all_users_json) if all_users_json else []

def add_user_to_all_users(username: str):
    all_users = get_all_users()
    if username not in all_users:
        all_users.append(username)
        kv.set("all_users", json.dumps(all_users))

def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Set expiration time
    to_encode.update({"exp": expire})  # Add expiration to the token payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/signup")
def signup(user_data: SignUpRequest):
    existing_user = get_user(user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    entity_id = str(uuid4())
    hashed_password = get_password_hash(user_data.password)
    user = UserInDB(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        entity_id=entity_id
    )
    
    kv.set(f"user:{user.username}", json.dumps(user.model_dump()))
    add_user_to_all_users(user.username)
    
    return JSONResponse(content={"message": "Registered successfully!"}, status_code=201)

@app.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest):
    user = authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": User(username=user.username, email=user.email, entity_id=user.entity_id)
    }

@app.get("/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/crews")
def get_crews(current_user: User = Depends(get_current_user)):
    return [["Influencer Analysis","Analyzes YouTube influencers based on your companies ICPs", 1], ["Default1", "-", 0],[ "Default2", "-", 0], ["Default3", "-", 0]]

@app.post("/authorize", response_model=AuthResponse)
def authorize_user(current_user: User = Depends(get_current_user)):
    toolset = ComposioToolSet(entity_id=current_user.entity_id)
    entity = toolset.get_entity()
    try:
        connection = entity.get_connection(app=App.GOOGLESHEETS)
        if connection:
            return AuthResponse(message=f"User {current_user.email} is already authenticated with Google Sheets")
    except:
        auth_url = entity.initiate_connection(App.GOOGLESHEETS, redirect_url="")

        return AuthResponse(
            message="Please authenticate Google Sheets in the browser.",
            auth_url=auth_url.redirectUrl
    )

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_influencers(request: AnalysisRequest, current_user: User = Depends(get_current_user)):
    try:
        toolset = ComposioToolSet(entity_id=current_user.entity_id)
        toolset.get_entity().get_connection(app=App.GOOGLESHEETS)
        composio_tools = toolset.get_tools(actions=[Action.GOOGLESHEETS_CREATE_GOOGLE_SHEET1, Action.GOOGLESHEETS_BATCH_UPDATE])

        print("STATE - Received Input")
        result = evaluate.main(request.keyword, request.channels, composio_tools)
        
        return AnalysisResponse(message=str(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")