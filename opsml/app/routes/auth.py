from typing import Annotated, Any, Optional, Sequence

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.base.server import ServerAuthRegistry
from opsml.settings.config import config
from opsml.types.extra import User

logger = ArtifactLogger.get_logger()

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/opsml/auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


# only set auth routes if auth is enabled

router = APIRouter()


async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    db: ServerAuthRegistry = request.app.state.auth_db

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            config.opsml_jwt_secret,
            algorithms=[config.opsml_jwt_algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except jwt.exceptions.ExpiredSignatureError:
        # pass to login
        raise credentials_exception

    except jwt.exceptions.DecodeError:
        raise credentials_exception

    user = db.get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/auth/token")
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    logger.info("Logging in user: {}", form_data.username)

    db: ServerAuthRegistry = request.app.state.auth_db
    user = db.get_user(form_data.username)

    if user is None:
        logger.info("User does not exist: {}", form_data.username)
        # reroute to login/register page
        pass

    assert user is not None

    # check if password is correct
    authenicated = db.authenticate_user(user, form_data.password)

    if not authenicated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("User authenticated: {}", form_data.username)
    return Token(
        access_token=db.create_access_token(user),
        token_type="bearer",
    )


security_dep: Optional[Sequence[Any]] = [Depends(get_current_active_user)] if config.opsml_auth else None
