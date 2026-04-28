import json
from sqlalchemy.orm import Session
from app.db.models.audit_log import AuditLog


def log_event(
    db: Session,
    user_id: int | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    event_data: dict | None = None,
    ip_address: str | None = None
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        event_data=json.dumps(event_data or {}),
        ip_address=ip_address
    )

    db.add(log)
    db.commit()