from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: str | None = None
    refresh_token: str | None = None
    name: str | None = None
    email: str | None = None
    role: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    success: bool
    message: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None


class LogoutRequest(BaseModel):
    refresh_token: str