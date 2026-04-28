import json
from sqlalchemy.orm import Session

from app.db.models.user_vault import UserVault
from app.db.models.shared_credential import SharedCredential
from app.db.models.shared_credential_access import SharedCredentialAccess
from app.core.encryption import decrypt_text


def domain_matches(saved_domain: str, current_domain: str) -> bool:
    return current_domain == saved_domain or current_domain.endswith("." + saved_domain)


def get_available_vaults_for_user_and_domain(db: Session, user_id: int, domain: str):
    results = []

    # 1. Personal vault
    user_vault = db.query(UserVault).filter(UserVault.user_id == user_id).first()

    if user_vault:
        vault_data = json.loads(decrypt_text(user_vault.vault_data_encrypted))

        for cred in vault_data:
            domains = cred.get("domains", [])
            if any(domain_matches(d, domain) for d in domains):
                results.append({
                    "credential_type": "personal",
                    "credential_id": cred["id"],
                    "label": cred["label"],
                    "username": cred["username"]
                })

    # 2. Shared credentials
    shared_rows = (
        db.query(SharedCredential)
        .join(
            SharedCredentialAccess,
            SharedCredentialAccess.shared_credential_id == SharedCredential.id
        )
        .filter(
            SharedCredentialAccess.user_id == user_id,
            SharedCredential.status == "active"
        )
        .all()
    )

    for shared in shared_rows:
        domains = json.loads(decrypt_text(shared.domains_encrypted))

        if any(domain_matches(d, domain) for d in domains):
            username = decrypt_text(shared.username_encrypted)

            results.append({
                "credential_type": "shared",
                "credential_id": str(shared.id),
                "label": shared.label,
                "username": username
            })

    return results