from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.vault import VaultMatchRequest, VaultMatchResponse, VaultChoice
from app.services.vault_service import get_available_vaults_for_user_and_domain

router = APIRouter()


@router.post("/match", response_model=VaultMatchResponse)
def match(
    data: VaultMatchRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    matches = get_available_vaults_for_user_and_domain(db, user.id, data.domain)
    return VaultMatchResponse(matches=[VaultChoice(**item) for item in matches])