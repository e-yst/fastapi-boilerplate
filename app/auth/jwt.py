from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.auth.crud.refresh_token import RefreshTokenCRUD, get_refresh_token_crud
from app.auth.crud.user import UsersCRUD, get_users_crud
from app.auth.models.refresh_token import RefreshToken, RefreshTokenBase
from app.auth.models.user import User
from app.auth.security import verify_password
from app.core.config import settings

ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
UsersCrudDep = Annotated[UsersCRUD, Depends(get_users_crud)]
RefreshTokenCrudDep = Annotated[RefreshTokenCRUD, Depends(get_refresh_token_crud)]


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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await users_crud.get(username=username)
    if user is None:
        raise credentials_exception
    return user


def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def validate_refresh_token(
    refresh_token: str, refresh_token_crud: RefreshTokenCrudDep
):
    token = await refresh_token_crud.get(token_value=refresh_token, is_revoked=False)
    if token.is_expired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    return token


async def revoke_refresh_token(
    token: RefreshToken, refresh_token_crud: RefreshTokenCrudDep
):
    return await refresh_token_crud.revoke_token(token.id)


async def create_refresh_token(
    user: Annotated[User, Depends(get_current_user)],
    refresh_token_crud: RefreshTokenCrudDep,
):
    token_data = RefreshTokenBase(user_id=user.id)
    refresh_token: RefreshToken = await refresh_token_crud.create(token_data)
    return refresh_token.token_value
