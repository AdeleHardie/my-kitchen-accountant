"""Dependencies to handle authentication and authorization."""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
import jwt
from jwt.exceptions import InvalidTokenError
from psycopg2.extensions import connection as Connection
from pydantic import BaseModel
from pwdlib import PasswordHash
from time import time
from typing import Annotated, Dict

# --- Internal imports ---
from core.config import settings
from db.connection import get_db_connection


ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")
router = APIRouter(
    prefix="/users"
)

class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str | None:
        authorization = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise self.make_not_authenticated_error()
            else:
                return None
        return param
    
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl=f"{settings.API_PREFIX}/users/login")

# region Models

class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    id: str
    username: str
    first_name: str
    disabled: bool = False


class UserFull(User):
    hashed_password: str


# region Helpers

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

# region Handle user

def get_user(username: str):
    db_connection = get_db_connection()
    with db_connection.cursor() as cursor:
        cursor.execute("""
        SELECT user_id, username, first_name, password_hash FROM users WHERE username=%s
        """,
        (username,)
        )
        result = cursor.fetchone()
        if not result:
            raise HTTPException(400, f"User {username} does not exist.")
        print(result)
        return UserFull(id=str(result[0]), username=result[1], first_name=result[2], hashed_password=result[3])

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# region Handle tokens

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(401, "Could not get username from token")
    except InvalidTokenError:
        raise HTTPException(401, "Failed to decode token")
    user = get_user(username=username)
    if user is None:
        raise HTTPException(401, "User not found")
    return user


# region Routers

@router.post("/login")
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Dict:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = jwt.encode({"sub": user.username, "iat": str(time()).split(".")[0]}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    response.set_cookie(
        key="access_token",
        value=f"bearer {access_token}",
        httponly=True,
        samesite="lax",
    )

    return {"message": "log in successful"}

@router.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
