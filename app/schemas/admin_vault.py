from pydantic import BaseModel


class CreateVaultItemRequest(BaseModel):
    account_name: str
    login_username: str
    login_password: str
    description: str | None = None
    owner_user_id: int | None = None


class AddVaultDomainRequest(BaseModel):
    vault_item_id: int
    domain: str


class AssignVaultAccessRequest(BaseModel):
    user_id: int
    vault_item_id: int
    access_type: str = "use"