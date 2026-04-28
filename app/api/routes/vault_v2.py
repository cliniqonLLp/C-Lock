from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json
import uuid

from app.dependencies import get_db, get_current_user
from app.db.models.user_vault import UserVault
from app.core.encryption import encrypt_text, decrypt_text
from app.db.models.shared_credential import SharedCredential
from app.db.models.shared_credential_access import SharedCredentialAccess
from app.dependencies import get_admin_user


router = APIRouter()

@router.post("/vault/add")
def add_personal_credential(
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    vault = db.query(UserVault).filter(UserVault.user_id == user.id).first()

    if vault:
        vault_data = json.loads(decrypt_text(vault.vault_data_encrypted))
    else:
        vault_data = []

    new_cred = {
        "id": str(uuid.uuid4()),
        "label": data["label"],
        "domains": data["domains"],
        "username": data["username"],
        "password": data["password"]
    }

    vault_data.append(new_cred)

    encrypted = encrypt_text(json.dumps(vault_data))

    if vault:
        vault.vault_data_encrypted = encrypted
    else:
        vault = UserVault(
            user_id=user.id,
            vault_data_encrypted=encrypted
        )
        db.add(vault)

    db.commit()

    return {"success": True, "message": "Credential added"}

@router.post("/admin/shared-credentials/create")
def create_shared_credential(
    data: dict,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    cred = SharedCredential(
        label=data["label"],
        domains_encrypted=encrypt_text(json.dumps(data["domains"])),
        username_encrypted=encrypt_text(data["username"]),
        password_encrypted=encrypt_text(data["password"]),
        created_by_user_id=admin.id
    )

    db.add(cred)
    db.commit()

    return {"success": True, "id": cred.id}

@router.post("/admin/shared-credentials/assign")
def assign_shared_credential(
    data: dict,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    access = SharedCredentialAccess(
        shared_credential_id=data["credential_id"],
        user_id=data["user_id"],
        access_type="use"
    )

    db.add(access)
    db.commit()

    return {"success": True}