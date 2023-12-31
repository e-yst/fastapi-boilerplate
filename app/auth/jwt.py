from datetime import datetime, timedelta
from typing import Annotated, Literal
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.auth.crud.user import UsersCrudDep
from app.auth.models.jwt import Token, TokenData
from app.auth.models.user import UserRead
from app.auth.security import verify_password
from app.core.config import settings

ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def authenticate_user(username: str, password: str, *, users_crud: UsersCrudDep):
    user = await users_crud.get(username=username)
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], *, users_crud: UsersCrudDep
):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.args[0],
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await users_crud.get(id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_admin_user(user: Annotated[UserRead, Depends(get_current_user)]):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_jwt_token(
    user_id: str | UUID,
    tkn_type: Literal["access", "refresh"],
    expires_delta: timedelta,
):
    expire = datetime.utcnow() + expires_delta
    to_encode = TokenData(sub=user_id, exp=expire, typ=tkn_type)
    encoded_jwt = jwt.encode(
        to_encode.model_dump(),
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def validate_refresh_token(token: str):
    payload = TokenData(
        **jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
    )
    if payload.typ != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not a refresh token",
        )
    if payload.is_expired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    return payload


def create_token_set(user_id: str | UUID) -> Token:
    return Token(
        access_token=create_jwt_token(
            user_id=user_id,
            tkn_type="access",
            expires_delta=timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRE_SECS),
        ),
        refresh_token=create_jwt_token(
            user_id=user_id,
            tkn_type="refresh",
            expires_delta=timedelta(seconds=settings.JWT_ACCESS_TOKEN_EXPIRE_SECS),
        ),
    )
