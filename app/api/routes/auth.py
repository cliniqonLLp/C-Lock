from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    LogoutRequest
)
from app.services.auth_service import login_user, refresh_session, logout_user

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, data.email, data.password)
    return LoginResponse(**result)


@router.post("/refresh", response_model=RefreshResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    result = refresh_session(db, data.refresh_token)
    return RefreshResponse(**result)


@router.post("/logout")
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    return logout_user(db, data.refresh_token)


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "authenticated": True,
        "email": user.email,
        "name": user.name,
        "role": user.role
    }