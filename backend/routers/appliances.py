from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Appliance, User, Booking
from ..schemas import ApplianceCreate, ApplianceResponse


router = APIRouter(
    prefix="/appliances",
    tags=["Appliances"]
)


# =========================================================
# REGISTER NEW APPLIANCE
# =========================================================

@router.post("/", response_model=ApplianceResponse)
def create_appliance(
    appliance: ApplianceCreate,
    db: Session = Depends(get_db)
):

    # Check whether the user exists
    user = db.query(User).filter(
        User.id == appliance.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # IMPORTANT:
    # Do NOT check whether the user already has an appliance.
    # A user can now register multiple appliances.

    new_appliance = Appliance(
        user_id=appliance.user_id,
        appliance_type=appliance.appliance_type,
        brand=appliance.brand,
        model=appliance.model,
        installation_date=appliance.installation_date,
        last_service_date=appliance.last_service_date,
        maintenance_interval=appliance.maintenance_interval
    )

    db.add(new_appliance)
    db.commit()
    db.refresh(new_appliance)

    return new_appliance


# =========================================================
# GET ALL APPLIANCES FOR A USER
# =========================================================

@router.get(
    "/user/{user_id}",
    response_model=list[ApplianceResponse]
)
def get_user_appliances(
    user_id: int,
    db: Session = Depends(get_db)
):

    appliances = db.query(Appliance).filter(
        Appliance.user_id == user_id
    ).order_by(
        Appliance.id.asc()
    ).all()

    return appliances


# =========================================================
# GET ONE APPLIANCE
# =========================================================

@router.get(
    "/{appliance_id}",
    response_model=ApplianceResponse
)
def get_appliance(
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

    return appliance


@router.delete("/{appliance_id}")
def delete_appliance(
    appliance_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    appliance = db.query(Appliance).filter(
        Appliance.id == appliance_id,
        Appliance.user_id == user_id
    ).first()

    if not appliance:
        raise HTTPException(
            status_code=404,
            detail="Appliance not found or does not belong to this user"
        )

    # Delete associated booking history first
    db.query(Booking).filter(
        Booking.appliance_id == appliance_id,
        Booking.user_id == user_id
    ).delete(
        synchronize_session=False
    )

    # Delete appliance
    db.delete(appliance)
    db.commit()

    return {
        "message": "Appliance removed successfully",
        "appliance_id": appliance_id
    }