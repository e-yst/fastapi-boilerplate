from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.crud.user import UsersCrudDep
from app.auth.jwt import (
    authenticate_user,
    create_token_set,
    get_admin_user,
    get_current_user,
    validate_refresh_token,
)
from app.auth.models.jwt import RefreshTokenReq, Token
from app.auth.models.user import User, UserCreate, UserDetailResp, UserPatch, UserRead
from app.core.models import DetailResp

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
):
    user = await authenticate_user(
        form_data.username,
        form_data.password,
        users_crud=users_crud,
    )
    return create_token_set(user.id)


@router.put("/token", response_model=Token)
async def refresh_token(incoming_token: RefreshTokenReq, user: GetCurrentUserDep):
    decoded_token = validate_refresh_token(incoming_token.refresh_token)
    if decoded_token.sub != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return create_token_set(user.id)


@router.delete("/users/{target_user_id}", response_model=DetailResp)
async def delete_user(
    target_user_id: UUID,
    user: Annotated[User, Depends(get_admin_user)],
    users_crud: UsersCrudDep,
):
    if target_user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't delete yourself",
        )
    await users_crud.delete(target_user_id)
    return {"detail": f"User {target_user_id} deleted"}


@router.patch("/users", response_model=UserDetailResp)
async def update_user(
    user: GetCurrentUserDep, user_patch: UserPatch, users_crud: UsersCrudDep
):
    if not user.is_admin and (user_patch.is_admin or user_patch.is_active):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't update this user",
        )
    user = await users_crud.update(user.id, user_patch)
    return {"detail": f"User {user.email} updated", "user": user}
