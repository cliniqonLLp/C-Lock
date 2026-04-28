from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.fill import FillRequest, FillResponse, FillRedeemRequest, FillRedeemResponse
from app.services.fill_service import create_fill_request, redeem_fill_token

router = APIRouter()


@router.post("/request", response_model=FillResponse)
def fill_request(
    data: FillRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    result = create_fill_request(
        db,
        user.id,
        data.credential_type,
        data.credential_id,
        data.domain
    )
    return FillResponse(**result)


@router.post("/redeem", response_model=FillRedeemResponse)
def redeem_fill(
    data: FillRedeemRequest,
    db: Session = Depends(get_db)
):
    result = redeem_fill_token(db, data.fill_token)
    return FillRedeemResponse(**result)