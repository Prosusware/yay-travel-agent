import os
from datetime import datetime, timedelta
from typing import Annotated, Optional

import motor.motor_asyncio
from bson import ObjectId
from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic.functional_validators import BeforeValidator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: str = "*"

    class Config:
        env_file = ".env"


settings = Settings()

app = FastAPI()

# Set up CORS middleware
# For production, you should restrict the origins to your frontend's domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
db = client.Prosusware
user_collection = db.get_collection("Users")
conversation_collection = db.get_collection("Conversations")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


PyObjectId = Annotated[str, BeforeValidator(str)]


class UserBase(BaseModel):
    first_name: str = Field(..., alias="FirstName")
    last_name: str = Field(..., alias="LastName")
    email: EmailStr
    phone_number: str = Field(..., alias="phoneNumber")


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: PyObjectId = Field(alias="_id")
    hashed_password: str

    class Config:
        populate_by_name = True


class User(UserBase):
    id: PyObjectId = Field(alias="_id")

    class Config:
        populate_by_name = True


class Conversation(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: str = Field(alias="userID")
    timestamp: datetime

    class Config:
        populate_by_name = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_user(email: str):
    user_data = await user_collection.find_one({"email": email})
    if user_data:
        return UserInDB(**user_data)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await get_user(token_data.email)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate):
    existing_user = await user_collection.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_password = get_password_hash(user_in.password)
    user_data = user_in.model_dump(by_alias=True, exclude={"password"})
    user_data["hashed_password"] = hashed_password

    new_user = await user_collection.insert_one(user_data)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})

    return User(**created_user)


@app.post("/conversations/", response_model=str, status_code=status.HTTP_201_CREATED)
async def create_conversation(current_user: User = Depends(get_current_user)):
    """
    Creates a new conversation for the currently authenticated user and returns its ID.
    """
    conversation_data = {"userID": current_user.id, "timestamp": datetime.utcnow()}
    new_conversation = await conversation_collection.insert_one(conversation_data)
    return str(new_conversation.inserted_id)


@app.get("/conversations/", response_model=list[Conversation])
async def get_user_conversations(current_user: User = Depends(get_current_user)):
    """
    Retrieves all conversations for the currently authenticated user.
    """
    conversations = await conversation_collection.find(
        {"userID": current_user.id}
    ).to_list(length=100)
    return conversations


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/")
def read_root():
    return {"message": "Welcome to YayTravel Backend!"} 