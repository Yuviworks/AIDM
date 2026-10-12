from backend.services.maintenance_service import calculate_maintenance
from backend.services.rag_service import generate_rag_answer
from backend.services.service_service import (
    find_service_centers,
    find_nearest_service_center,
    find_available_slot
)
from backend.database import SessionLocal
from backend.models import Booking
from datetime import date


def maintenance_tool(appliance):
    return calculate_maintenance(appliance)


def rag_tool(query: str, model: str):
    return generate_rag_answer(
        query=query,
        model=model
    )

def service_discovery_tool(
    brand: str,
    location: str
):
    return find_service_centers(
        brand=brand,
        location=location
    )


def nearest_service_center_tool(
    brand: str,
    location: str
):
    return find_nearest_service_center(
        brand=brand,
        location=location
    )


def available_slot_tool(
    service_center: dict,
    preferred_date: str
):
    return find_available_slot(
        service_center=service_center,
        preferred_date=preferred_date
    )


def booking_tool(
    user_id: int,
    appliance_id: int,
    service_center_id: int,
    booking_date: str,
    booking_slot: str | None = None
):

    db = SessionLocal()

    try:

        new_booking = Booking(
            user_id=user_id,
            appliance_id=appliance_id,
            service_center_id=service_center_id,
            booking_date=date.fromisoformat(
                booking_date
            ),
            booking_slot=booking_slot,
            status="CONFIRMED"
        )

        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)

        return {
            "booking_id": new_booking.id,
            "booking_date":
                str(new_booking.booking_date),
            "booking_slot":
                new_booking.booking_slot,
            "status":
                new_booking.status
        }

    finally:

        db.close()