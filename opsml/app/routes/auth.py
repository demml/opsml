from typing import Annotated

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


class UserCreated(BaseModel):
    created: bool = False


class UserUpdated(BaseModel):
    updated: bool = False


class UserDeleted(BaseModel):
    deleted: bool = False


router = APIRouter()


async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    auth_db: ServerAuthRegistry = request.app.state.auth_db

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

    except jwt.exceptions.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token_expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    except jwt.exceptions.DecodeError as exc:
        raise credentials_exception from exc

    user = auth_db.get_user(token_data.username)
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

    # quick exit if auth is disabled
    if not config.opsml_auth:
        return Token(access_token="", token_type="bearer")

    auth_db: ServerAuthRegistry = request.app.state.auth_db
    user = auth_db.get_user(form_data.username)

    if user is None:
        logger.info("User does not exist: {}", form_data.username)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    assert user is not None

    # check if password is correct
    authenicated = auth_db.authenticate_user(user, form_data.password)

    if not authenicated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("User authenticated: {}", form_data.username)
    return Token(access_token=auth_db.create_access_token(user), token_type="bearer")


@router.get("/auth/user", response_model=User)
def get_user(
    request: Request,
    username: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Retrieves user by username"""
    if not current_user.scopes.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    auth_db: ServerAuthRegistry = request.app.state.auth_db
    user = auth_db.get_user(username)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.post("/auth/user", response_model=UserCreated)
def create_user(
    request: Request,
    user: User,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserCreated:
    """Create new user"""
    if not current_user.scopes.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    auth_db: ServerAuthRegistry = request.app.state.auth_db

    # check user not exists
    if auth_db.get_user(user.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    # add user
    auth_db.add_user(user)

    # test getting user
    user = auth_db.get_user(user.username)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to create user")

    return UserCreated(created=True)


@router.put("/auth/user", response_model=UserUpdated)
def update_user(
    request: Request,
    user: User,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserUpdated:
    """Update user"""
    if not current_user.scopes.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    auth_db: ServerAuthRegistry = request.app.state.auth_db
    updated = auth_db.update_user(user)

    return UserUpdated(updated=updated)


@router.delete("/auth/user", response_model=UserDeleted)
def delete_user(
    request: Request,
    username: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserDeleted:
    """Delete user"""
    if not current_user.scopes.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    auth_db: ServerAuthRegistry = request.app.state.auth_db
    user = auth_db.get_user(username)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    deleted = auth_db.delete_user(user)
    return UserDeleted(deleted=deleted)
