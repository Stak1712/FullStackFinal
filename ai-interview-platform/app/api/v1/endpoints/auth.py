from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_auth_service
from app.auth.dependencies import get_current_user
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenResponse, UserPublic
from app.services.auth_service import AuthService


router = APIRouter()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(payload: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        user = auth_service.register(payload)
        return UserPublic.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    tokens = auth_service.login(payload)
    return TokenResponse.model_validate(tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(payload: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)):
    tokens = auth_service.refresh(payload.refresh_token)
    return TokenResponse.model_validate(tokens)


@router.get("/me", response_model=UserPublic)
async def me(user=Depends(get_current_user)):
    return UserPublic.model_validate(user)


@router.post("/logout")
async def logout(payload: LogoutRequest, auth_service: AuthService = Depends(get_auth_service)):
    auth_service.logout(payload.refresh_token)
    return {"ok": True}
