from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import bcrypt
from opsml.helpers.logging import ArtifactLogger
from opsml.settings.config import config
from opsml.types import RegistryType
from typing import Annotated, Union
from opsml.registry.sql.base.server import ServerAuthRegistry
from datetime import datetime, timedelta, timezone

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


# def verify_password(plain_password, hashed_password):
# return pwd_context.verify(plain_password, hashed_password)

# only set auth routes if auth is enabled

if config.opsml_auth:
    router = APIRouter()

    @router.post("/token", response_model=Token)
    async def login_for_access_token(request: Request, username: str, password: str):
        pass

    @app.post("/token")
    async def login_for_access_token(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> Token:
        db: ServerAuthRegistry = request.app.state.auth_db

        user = db.get_user(form_data.username)

        if user is None:
            # reroute to login/register page
            pass

        # check if password is correct
        authenicated = db.authenticate_user(user, form_data.password)

        if not authenicated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return Token(access_token=access_token, token_type="bearer")

# def get_password_hash(password):
# return pwd_context.hash(password)


# def authenticate_user(fake_db, username: str, password: str):
#    user = get_user(fake_db, username)
#    if not user:
#        return False
#    if not verify_password(password, user.hashed_password):
#        return False
#    return user
