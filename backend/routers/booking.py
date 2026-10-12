from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, User, Appliance
from ..schemas import BookingCreate, BookingResponse


router = APIRouter(
    prefix="/booking",
    tags=["Booking"]
)


@router.post("/", response_model=BookingResponse)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db)
):

    # Check user
    user = db.query(User).filter(
        User.id == booking.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check appliance
    appliance = db.query(Appliance).filter(
        Appliance.id == booking.appliance_id
    ).first()

    if not appliance:
        raise HTTPException(
            status_code=404,
            detail="Appliance not found"
        )

    # Create booking
    new_booking = Booking(
        user_id=booking.user_id,
        appliance_id=booking.appliance_id,
        service_center_id=booking.service_center_id,
        booking_date=booking.booking_date,
        status="CONFIRMED"
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking

@router.get("/user/{user_id}", response_model=list[BookingResponse])
def get_user_bookings(
    user_id: int,
    db: Session = Depends(get_db)
):

    bookings = db.query(Booking).filter(
        Booking.user_id == user_id
    ).order_by(
        Booking.id.desc()
    ).all()

    return bookings