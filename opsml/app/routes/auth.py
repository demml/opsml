from typing import Annotated, Union

import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from opsml.app.routes.pydantic_models import (
    SecurityQuestionResponse,
    TempRequest,
    UserExistsResponse,
)
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
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    logger.info("Logging in user: {}", form_data.username)

    # quick exit if auth is disabled
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

    jwt_token = auth_db.create_access_token(user, minutes=30)
    refresh_token = auth_db.create_access_token(user, minutes=60)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return Token(access_token=jwt_token, token_type="bearer")


@router.get("/auth/token/rotate")
async def create_refresh_token(
    request: Request,
    response: Response,
    refresh_token: Annotated[Union[str, None], Cookie()] = None,
) -> bool:
    """Rotates refresh token

    Args:
        request:
            FastAPI request object
        response:
            FastAPI response object
        refresh_token:
            refresh token cookie
    """

    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No refresh token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # check user
        auth_db: ServerAuthRegistry = request.app.state.auth_db
        user = await get_current_user(request, refresh_token)

        # create new access token
        refresh_token = auth_db.create_access_token(user, minutes=60)
        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

        return True

    except Exception as e:
        logger.error("Failed to rotate token: {}", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to rotate token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.get("/auth/token/refresh")
async def get_refresh_from_cookie(
    request: Request,
    response: Response,
    refresh_token: Annotated[Union[str, None], Cookie()] = None,
) -> Token:
    """Generates new access token from refresh token"""

    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_current_user(request, refresh_token)
    logger.info("Refreshing token for user: {}", user.username)

    # create new access token
    auth_db: ServerAuthRegistry = request.app.state.auth_db
    jwt_token = auth_db.create_access_token(user)
    refresh_token = auth_db.create_access_token(user, minutes=60)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return Token(access_token=jwt_token, token_type="bearer")


@router.get("/auth/user", response_model=User)
def get_user(
    request: Request,
    username: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Retrieves user by username"""

    logger.info("Getting user: {}", username)

    # check if user is admin
    if not current_user.scopes.admin:
        # check if user is requesting themselves
        if current_user.username != username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions")

    auth_db: ServerAuthRegistry = request.app.state.auth_db
    user = auth_db.get_user(username)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # remove passwords
    user.password = None
    user.hashed_password = None

    return user


@router.get("/auth/user/exists", response_model=UserExistsResponse)
def user_exists(request: Request, username: str) -> UserExistsResponse:
    """Retrieves user by username"""

    auth_db: ServerAuthRegistry = request.app.state.auth_db

    # try username first
    user = auth_db.get_user(username)

    if user is None:
        # try email
        user = auth_db.get_user_by_email(username)

        if user is None:
            return UserExistsResponse(exists=False, username=username)

    return UserExistsResponse(exists=True, username=user.username)


@router.post("/auth/user", response_model=UserCreated)
def create_user(
    request: Request,
    user: User,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserCreated:
    """Create new user - requires admin permissions"""
    if not current_user.scopes.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions")

    auth_db: ServerAuthRegistry = request.app.state.auth_db

    # check user not exists
    if auth_db.get_user(user.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    # add user
    auth_db.add_user(user)

    # test getting user
    db_user = auth_db.get_user(user.username)

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to create user")

    return UserCreated(created=True)


@router.post("/auth/register", response_model=UserCreated)
def register_user(
    request: Request,
    user: User,
) -> UserCreated:
    """Create new user - for login page"""

    auth_db: ServerAuthRegistry = request.app.state.auth_db

    # check user not exists
    if auth_db.get_user(user.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
            headers={"detail": "User already exists"},
        )

    # add user
    auth_db.add_user(user)

    # test getting user
    db_user = auth_db.get_user(user.username)

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to create user",
            headers={"detail": "Failed to create user"},
        )

    return UserCreated(created=True)


@router.put("/auth/user", response_model=UserUpdated)
def update_user(
    request: Request,
    user: User,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserUpdated:
    """Update user"""
    if not current_user.scopes.admin:
        # check if user is updating themselves
        if current_user.username != user.username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions")

    if current_user.scopes.model_dump() != user.scopes.model_dump() and not current_user.scopes.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions to change scopes")

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


@router.get("/auth/verify")
def check_auth() -> bool:
    return config.opsml_auth


@router.get("/auth/security", response_model=SecurityQuestionResponse)
def secret_question(request: Request, username: str) -> SecurityQuestionResponse:
    """Retrieves user secret question by username

    Args:
        request:
            FastAPI request object
        username:
            username of the user

    """

    auth_db: ServerAuthRegistry = request.app.state.auth_db

    # try username first
    user = auth_db.get_user(username)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return SecurityQuestionResponse(question=user.security_question)


# check security question
@router.post("/auth/temp")
def generate_temp_token(
    request: Request,
    temp_request: TempRequest,
) -> str:
    """Check user security question by username and generate temporary token

    Args:
        request:
            FastAPI request object
        username:
            username of the user
        answer:
            answer to the security question

    """

    auth_db: ServerAuthRegistry = request.app.state.auth_db

    # try username first
    user = auth_db.get_user(temp_request.username)

    if user is None:
        return "User not found"

    if not user.security_answer == temp_request.answer:
        return "Incorrect answer"

    # short lived token for password reset
    return auth_db.create_access_token(user, minutes=5)
