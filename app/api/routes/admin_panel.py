import json
import uuid

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_admin_user
from app.db.models.user import User
from app.db.models.user_vault import UserVault
from app.db.models.shared_credential import SharedCredential
from app.db.models.shared_credential_access import SharedCredentialAccess
from app.db.models.audit_log import AuditLog
from app.core.security import hash_password
from app.core.encryption import encrypt_text, decrypt_text
from app.services.auth_service import login_user
from app.services.audit_service import log_event

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin-login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/login.html",
        {"request": request}
    )


@router.post("/admin-login")
def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    result = login_user(db, email, password)

    if not result["success"]:
        return templates.TemplateResponse(
            request,
            "admin/login.html",
            {"request": request, "error": "Invalid credentials"}
        )

    response = RedirectResponse("/admin-panel", status_code=303)
    response.set_cookie(
        key="session_token",
        value=result["access_token"],
        httponly=True
    )

    return response


@router.get("/admin-panel", response_class=HTMLResponse)
def dashboard(
    request: Request,
    admin=Depends(get_admin_user)
):
    return templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        {"request": request}
    )


@router.get("/admin-panel/users", response_class=HTMLResponse)
def users_page(
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    users = db.query(User).all()
    return templates.TemplateResponse(
        request,
        "admin/users.html",
        {"request": request, "users": users}
    )


@router.post("/admin-panel/users/create")
def create_user_from_panel(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    existing = db.query(User).filter(User.email == email).first()

    if existing:
        return RedirectResponse("/admin-panel/users", status_code=303)

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    log_event(
        db,
        user_id=admin.id,
        action="ADMIN_CREATE_USER",
        resource_type="user",
        resource_id=str(user.id),
        event_data={
            "email": email,
            "role": role
        }
    )

    return RedirectResponse("/admin-panel/users", status_code=303)


@router.get("/admin-panel/personal-vaults", response_class=HTMLResponse)
def personal_vaults_page(
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    users = db.query(User).all()

    return templates.TemplateResponse(
        request,
        "admin/personal_vaults.html",
        {
            "request": request,
            "users": users
        }
    )


@router.post("/admin-panel/personal-vaults/add")
def admin_add_personal_credential(
    user_id: int = Form(...),
    label: str = Form(...),
    domains: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    vault = db.query(UserVault).filter(UserVault.user_id == user_id).first()

    if vault:
        vault_data = json.loads(decrypt_text(vault.vault_data_encrypted))
    else:
        vault_data = []

    domain_list = [
        d.strip().replace("https://", "").replace("http://", "").rstrip("/")
        for d in domains.split(",")
        if d.strip()
    ]

    new_credential = {
        "id": str(uuid.uuid4()),
        "label": label,
        "domains": domain_list,
        "username": username,
        "password": password
    }

    vault_data.append(new_credential)
    encrypted = encrypt_text(json.dumps(vault_data))

    if vault:
        vault.vault_data_encrypted = encrypted
    else:
        vault = UserVault(
            user_id=user_id,
            vault_data_encrypted=encrypted
        )
        db.add(vault)

    db.commit()

    log_event(
        db,
        user_id=admin.id,
        action="ADMIN_ADD_PERSONAL_CREDENTIAL",
        resource_type="user_vault",
        resource_id=str(user_id),
        event_data={
            "target_user_id": user_id,
            "label": label,
            "domains": domain_list,
            "username": username
        }
    )

    return RedirectResponse("/admin-panel/personal-vaults", status_code=303)


@router.get("/admin-panel/shared-credentials", response_class=HTMLResponse)
def shared_credentials_page(
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    users = db.query(User).all()
    shared_credentials = db.query(SharedCredential).all()

    return templates.TemplateResponse(
        request,
        "admin/shared_credentials.html",
        {
            "request": request,
            "users": users,
            "shared_credentials": shared_credentials
        }
    )


@router.post("/admin-panel/shared-credentials/create")
def admin_create_shared_credential(
    label: str = Form(...),
    domains: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    domain_list = [
        d.strip().replace("https://", "").replace("http://", "").rstrip("/")
        for d in domains.split(",")
        if d.strip()
    ]

    shared = SharedCredential(
        label=label,
        domains_encrypted=encrypt_text(json.dumps(domain_list)),
        username_encrypted=encrypt_text(username),
        password_encrypted=encrypt_text(password),
        created_by_user_id=admin.id,
        status="active"
    )

    db.add(shared)
    db.commit()
    db.refresh(shared)

    log_event(
        db,
        user_id=admin.id,
        action="ADMIN_CREATE_SHARED_CREDENTIAL",
        resource_type="shared_credential",
        resource_id=str(shared.id),
        event_data={
            "label": label,
            "domains": domain_list,
            "username": username
        }
    )

    return RedirectResponse("/admin-panel/shared-credentials", status_code=303)


@router.post("/admin-panel/shared-credentials/assign")
def admin_assign_shared_credential(
    shared_credential_id: int = Form(...),
    user_id: int = Form(...),
    access_type: str = Form("use"),
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    existing = (
        db.query(SharedCredentialAccess)
        .filter(
            SharedCredentialAccess.shared_credential_id == shared_credential_id,
            SharedCredentialAccess.user_id == user_id
        )
        .first()
    )

    if existing:
        resource_id = str(existing.id)
    else:
        access = SharedCredentialAccess(
            shared_credential_id=shared_credential_id,
            user_id=user_id,
            access_type=access_type
        )

        db.add(access)
        db.commit()
        db.refresh(access)
        resource_id = str(access.id)

    log_event(
        db,
        user_id=admin.id,
        action="ADMIN_ASSIGN_SHARED_CREDENTIAL",
        resource_type="shared_credential_access",
        resource_id=resource_id,
        event_data={
            "shared_credential_id": shared_credential_id,
            "target_user_id": user_id,
            "access_type": access_type
        }
    )

    return RedirectResponse("/admin-panel/shared-credentials", status_code=303)


@router.get("/admin-panel/audit-logs", response_class=HTMLResponse)
def audit_logs_page(
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(200)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "admin/audit_logs.html",
        {
            "request": request,
            "logs": logs
        }
    )

from app.db.session import SessionLocal
from app.db.models.user import User
from app.core.security import hash_password
from fastapi import APIRouter



@router.post("/init-admin")
def init_admin():
    db = SessionLocal()

    existing = db.query(User).filter(User.email == "admin@cliniqon.com").first()
    if existing:
        return {"message": "Admin already exists"}

    admin = User(
        name="Admin",
        email="admin@cliniqon.com",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    db.close()

    return {"message": "Admin created"}