from sqlalchemy.orm import Session

from app.db.models.vault_item import VaultItem
from app.db.models.vault_domain import VaultDomain
from app.db.models.user_vault_access import UserVaultAccess
from app.core.encryption import encrypt_text


def create_vault_item(
    db: Session,
    account_name: str,
    login_username: str,
    login_password: str,
    description: str | None,
    owner_user_id: int | None
):
    encrypted_password = encrypt_text(login_password)

    item = VaultItem(
        account_name=account_name,
        login_username=login_username,
        login_password_encrypted=encrypted_password,
        description=description,
        owner_user_id=owner_user_id,
        status="active"
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "success": True,
        "message": "Vault item created",
        "vault_item_id": item.id
    }


def add_vault_domain(db: Session, vault_item_id: int, domain: str):
    domain_row = VaultDomain(
        vault_item_id=vault_item_id,
        domain=domain
    )

    db.add(domain_row)
    db.commit()

    return {
        "success": True,
        "message": "Domain added to vault item"
    }


def assign_vault_access(db: Session, user_id: int, vault_item_id: int, access_type: str):
    access = UserVaultAccess(
        user_id=user_id,
        vault_item_id=vault_item_id,
        access_type=access_type
    )

    db.add(access)
    db.commit()

    return {
        "success": True,
        "message": "Vault access assigned"
    }