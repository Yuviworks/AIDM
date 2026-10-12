from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Appliance
from ..services.maintenance_service import calculate_maintenance


router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"]
)


@router.get("/{appliance_id}")
def check_maintenance(
    appliance_id: int,
    db: Session = Depends(get_db)
):

    appliance = db.query(Appliance).filter(
        Appliance.id == appliance_id
    ).first()

    if not appliance:
        raise HTTPException(
            status_code=404,
            detail="Appliance not found"
        )

    return calculate_maintenance(appliance)