from pydantic import BaseModel


class FillRequest(BaseModel):
    credential_type: str   # "personal" or "shared"
    credential_id: str
    domain: str


class FillRedeemRequest(BaseModel):
    fill_token: str


class FillResponse(BaseModel):
    success: bool
    fill_token: str | None = None
    message: str


class FillRedeemResponse(BaseModel):
    success: bool
    username: str | None = None
    password: str | None = None
    message: str