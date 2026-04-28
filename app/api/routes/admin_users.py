from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.admin_user import CreateUserRequest
from app.services.admin_user_service import create_user
from app.dependencies import get_db, get_admin_user

router = APIRouter()


@router.post("/users")
def create_user_api(
    data: CreateUserRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    return create_user(db, data.name, data.email, data.password, data.role)

