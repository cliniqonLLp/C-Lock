import json
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.models.fill_token import FillToken
from app.db.models.user_vault import UserVault
from app.db.models.shared_credential import SharedCredential
from app.db.models.shared_credential_access import SharedCredentialAccess
from app.services.audit_service import log_event
from app.core.encryption import decrypt_text


def create_fill_request(
    db: Session,
    user_id: int,
    credential_type: str,
    credential_id: str,
    domain: str
):
    username = None
    password = None

    if credential_type == "personal":
        vault = db.query(UserVault).filter(UserVault.user_id == user_id).first()

        if not vault:
            log_event(
                db,
                user_id=user_id,
                action="FILL_REQUEST_FAILED",
                resource_type=credential_type,
                resource_id=credential_id,
                event_data={"domain": domain, "reason": "No vault"}
            )
            return {"success": False, "message": "No vault"}

        vault_data = json.loads(decrypt_text(vault.vault_data_encrypted))

        cred = next((c for c in vault_data if c["id"] == credential_id), None)

        if not cred:
            log_event(
                db,
                user_id=user_id,
                action="FILL_REQUEST_FAILED",
                resource_type=credential_type,
                resource_id=credential_id,
                event_data={"domain": domain, "reason": "Credential not found"}
            )
            return {"success": False, "message": "Credential not found"}

        if domain not in cred.get("domains", []):
            log_event(
                db,
                user_id=user_id,
                action="FILL_REQUEST_FAILED",
                resource_type=credential_type,
                resource_id=credential_id,
                event_data={"domain": domain, "reason": "Domain mismatch"}
            )
            return {"success": False, "message": "Domain mismatch"}

        username = cred["username"]
        password = cred["password"]

    elif credential_type == "shared":
        shared = db.query(SharedCredential).filter(
            SharedCredential.id == int(credential_id),
            SharedCredential.status == "active"
        ).first()

        if not shared:
            log_event(
                db,
                user_id=user_id,
                action="FILL_REQUEST_FAILED",
                resource_type=credential_type,
                resource_id=credential_id,
                event_data={"domain": domain, "reason": "Shared credential not found"}
            )
            return {"success": False, "message": "Shared credential not found"}

        access = db.query(SharedCredentialAccess).filter(
            SharedCredentialAccess.user_id == user_id,
            SharedCredentialAccess.shared_credential_id == shared.id
        ).first()

        if not access:
            log_event(
                db,
                user_id=user_id,
                action="FILL_REQUEST_FAILED",
                resource_type=credential_type,
                resource_id=credential_id,
                event_data={"domain": domain, "reason": "Access denied"}
            )
            return {"success": False, "message": "Access denied"}

        domains = json.loads(decrypt_text(shared.domains_encrypted))

        if domain not in domains:
            log_event(
                db,
                user_id=user_id,
                action="FILL_REQUEST_FAILED",
                resource_type=credential_type,
                resource_id=credential_id,
                event_data={"domain": domain, "reason": "Domain mismatch"}
            )
            return {"success": False, "message": "Domain mismatch"}

        username = decrypt_text(shared.username_encrypted)
        password = decrypt_text(shared.password_encrypted)

    else:
        log_event(
            db,
            user_id=user_id,
            action="FILL_REQUEST_FAILED",
            resource_type=credential_type,
            resource_id=credential_id,
            event_data={"domain": domain, "reason": "Invalid credential type"}
        )
        return {"success": False, "message": "Invalid credential type"}

    token = secrets.token_urlsafe(32)

    fill = FillToken(
        token=token,
        username=username,
        password=password,
        expires_at=datetime.utcnow() + timedelta(seconds=20),
        is_used=False
    )

    db.add(fill)

    log_event(
        db,
        user_id=user_id,
        action="FILL_REQUEST",
        resource_type=credential_type,
        resource_id=credential_id,
        event_data={
            "domain": domain,
            "username": username
        }
    )

    db.commit()

    return {
        "success": True,
        "fill_token": token,
        "message": "Fill token created"
    }


def redeem_fill_token(db: Session, token: str):
    fill = db.query(FillToken).filter(FillToken.token == token).first()

    if not fill:
        log_event(
            db,
            user_id=None,
            action="FILL_REDEEM_FAILED",
            resource_type="fill_token",
            resource_id=None,
            event_data={"reason": "Invalid token"}
        )
        return {"success": False, "message": "Invalid token"}

    if fill.is_used:
        log_event(
            db,
            user_id=None,
            action="FILL_REDEEM_FAILED",
            resource_type="fill_token",
            resource_id=str(fill.id),
            event_data={"reason": "Already used"}
        )
        return {"success": False, "message": "Already used"}

    if fill.expires_at < datetime.utcnow():
        log_event(
            db,
            user_id=None,
            action="FILL_REDEEM_FAILED",
            resource_type="fill_token",
            resource_id=str(fill.id),
            event_data={"reason": "Expired"}
        )
        return {"success": False, "message": "Expired"}

    fill.is_used = True

    log_event(
        db,
        user_id=None,
        action="FILL_REDEEM",
        resource_type="fill_token",
        resource_id=str(fill.id),
        event_data={
            "username": fill.username
        }
    )

    db.commit()

    return {
        "success": True,
        "username": fill.username,
        "password": fill.password,
        "message": "Credential redeemed"
    }