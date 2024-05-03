from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

router = APIRouter()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    is_active: bool = False


class UserInDB(User):
    hashed_password: str


# def verify_password(plain_password, hashed_password):
# return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password):
# return pwd_context.hash(password)


# def authenticate_user(fake_db, username: str, password: str):
#    user = get_user(fake_db, username)
#    if not user:
#        return False
#    if not verify_password(password, user.hashed_password):
#        return False
#    return user
