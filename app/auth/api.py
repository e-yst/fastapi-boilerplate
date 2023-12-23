from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.jwt import (
    RefreshTokenCrudDep,
    UsersCrudDep,
    authenticate_user,
    create_jwt_token,
    create_refresh_token,
    get_current_user,
    revoke_refresh_token,
    validate_refresh_token,
)
from app.auth.models.jwt import Token, TokenData
from app.auth.models.refresh_token import RefreshToken, RefreshTokenCreate
from app.auth.models.user import User, UserCreate, UserRead
from app.core.config import settings

router = APIRouter()
GetCurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register_user(auth_data: UserCreate, users_crud: UsersCrudDep):
    user = await users_crud.create(auth_data)
    return user


@router.get("/users/me", response_model=UserRead)
async def get_my_account(user: GetCurrentUserDep):
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    users_crud: UsersCrudDep,
    refresh_token_crud: RefreshTokenCrudDep,
):
    user: User = await authenticate_user(
        form_data.username, form_data.password, users_crud=users_crud
    )
    token_data = TokenData(sub=user.username)
    access_token = create_jwt_token(
        data=token_data.model_dump(),
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_SECS),
    )
    refresh_token = await refresh_token_crud.get_valid_token(user.id)
    if refresh_token is None:
        refresh_token = await create_refresh_token(user, refresh_token_crud)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.put("/token", response_model=Token)
async def refresh_token(
    incoming_token: RefreshTokenCreate,
    user: GetCurrentUserDep,
    refresh_token_crud: RefreshTokenCrudDep,
):
    token = await validate_refresh_token(
        incoming_token.refresh_token, refresh_token_crud
    )
    await revoke_refresh_token(token, refresh_token_crud)

    new_refresh_token = await create_refresh_token(user, refresh_token_crud)
    access_token_data = TokenData(sub=user.username)
    access_token = create_jwt_token(
        data=access_token_data.model_dump(),
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_SECS),
    )
    return {"access_token": access_token, "refresh_token": new_refresh_token}
