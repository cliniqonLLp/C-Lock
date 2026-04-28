from pydantic import BaseModel


class VaultMatchRequest(BaseModel):
    domain: str


class VaultChoice(BaseModel):
    credential_type: str
    credential_id: str
    label: str
    username: str


class VaultMatchResponse(BaseModel):
    matches: list[VaultChoice]