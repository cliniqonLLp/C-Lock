from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_admin_user
from app.schemas.admin_vault import (
    CreateVaultItemRequest,
    AddVaultDomainRequest,
    AssignVaultAccessRequest
)
from app.services.admin_vault_service import (
    create_vault_item,
    add_vault_domain,
    assign_vault_access
)

router = APIRouter()


@router.post("/vault-items")
def create_vault_item_api(
    data: CreateVaultItemRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    return create_vault_item(
        db,
        data.account_name,
        data.login_username,
        data.login_password,
        data.description,
        data.owner_user_id
    )


@router.post("/vault-domains")
def add_vault_domain_api(
    data: AddVaultDomainRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    return add_vault_domain(db, data.vault_item_id, data.domain)


@router.post("/vault-access")
def assign_vault_access_api(
    data: AssignVaultAccessRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    return assign_vault_access(db, data.user_id, data.vault_item_id, data.access_type)