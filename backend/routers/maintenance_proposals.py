
from calendar import monthrange
from datetime import date, datetime
from pathlib import Path
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Appliance, Booking, MaintenanceProposal, User


router = APIRouter(
    prefix="/maintenance-proposals",
    tags=["Proactive Maintenance"],
)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def add_months(original_date: date, months: int) -> date:
    """Add calendar months while keeping the day valid."""
    month_index = original_date.month - 1 + months
    year = original_date.year + month_index // 12
    month = month_index % 12 + 1

    day = min(
        original_date.day,
        monthrange(year, month)[1],
    )

    return date(year, month, day)


def load_service_centers() -> list[dict]:
    """Load configured demo service-center data."""
    project_root = Path(__file__).resolve().parents[2]
    centers_path = project_root / "data" / "service_centers.json"

    with centers_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_slot(slot: str) -> tuple[date, datetime | None]:
    """
    Parse a date-prefixed slot such as:
    '2026-11-15 10:00 AM'
    """
    slot_date = date.fromisoformat(slot[:10])
    slot_time = None

    time_text = slot[10:].strip()

    if time_text:
        for time_format in ("%I:%M %p", "%H:%M"):
            try:
                parsed_time = datetime.strptime(
                    time_text,
                    time_format,
                ).time()

                slot_time = datetime.combine(
                    slot_date,
                    parsed_time,
                )
                break
            except ValueError:
                continue

    return slot_date, slot_time


def find_demo_slot(
    appliance: Appliance,
    user: User,
    db: Session,
) -> tuple[dict, date, str] | None:
    """
    Find the earliest future demo slot for the appliance brand
    near the user's saved location.

    Existing confirmed bookings are excluded when their center,
    date, and slot match.
    """
    centers = load_service_centers()
    today = date.today()
    now = datetime.now()

    matching_centers = [
        center
        for center in centers
        if center.get("brand", "").lower() == appliance.brand.lower()
        and (
            user.location.lower()
            in center.get("location", "").lower()
        )
    ]

    matching_centers.sort(
        key=lambda center: center.get(
            "distance_km",
            float("inf"),
        )
    )

    for center in matching_centers:
        center_id = center.get("id", center.get("service_center_id"))

        if center_id is None:
            continue

        slots = center.get("available_slots", [])

        for slot in sorted(slots):
            try:
                slot_date, slot_datetime = parse_slot(slot)
            except (ValueError, TypeError):
                continue

            if slot_date < today:
                continue

            if slot_datetime is not None and slot_datetime <= now:
                continue

            conflict = (
                db.query(Booking)
                .filter(
                    Booking.service_center_id == center_id,
                    Booking.booking_date == slot_date,
                    Booking.booking_slot == slot,
                    Booking.status == "CONFIRMED",
                )
                .first()
            )

            if conflict:
                continue

            return center, slot_date, slot

    return None


def scan_appliance(
    appliance: Appliance,
    user: User,
    db: Session,
) -> dict:
    """Create one pending proposal when maintenance is due."""
    due_date = add_months(
        appliance.last_service_date,
        appliance.maintenance_interval,
    )

    if date.today() < due_date:
        return {
            "appliance_id": appliance.id,
            "result": "NOT_DUE",
            "maintenance_due_date": due_date.isoformat(),
        }

    existing = (
        db.query(MaintenanceProposal)
        .filter(
            MaintenanceProposal.appliance_id == appliance.id,
            MaintenanceProposal.maintenance_due_date == due_date,
        )
        .first()
    )

    if existing:
        return {
            "appliance_id": appliance.id,
            "result": "ALREADY_PROPOSED",
            "proposal_id": existing.id,
            "status": existing.status,
        }

    slot_result = find_demo_slot(appliance, user, db)

    if slot_result is None:
        return {
            "appliance_id": appliance.id,
            "result": "NO_DEMO_SLOT_AVAILABLE",
            "maintenance_due_date": due_date.isoformat(),
        }

    center, proposed_date, proposed_slot = slot_result
    center_id = center.get("id", center.get("service_center_id"))

    proposal = MaintenanceProposal(
        user_id=user.id,
        appliance_id=appliance.id,
        maintenance_due_date=due_date,
        proposed_date=proposed_date,
        proposed_slot=proposed_slot,
        service_center_id=center_id,
        status="PENDING",
    )

    db.add(proposal)

    try:
        db.commit()
        db.refresh(proposal)
    except IntegrityError:
        db.rollback()

        existing = (
            db.query(MaintenanceProposal)
            .filter(
                MaintenanceProposal.appliance_id == appliance.id,
                MaintenanceProposal.maintenance_due_date == due_date,
            )
            .first()
        )

        return {
            "appliance_id": appliance.id,
            "result": "ALREADY_PROPOSED",
            "proposal_id": existing.id if existing else None,
        }

    return {
        "appliance_id": appliance.id,
        "result": "PROPOSAL_CREATED",
        "proposal_id": proposal.id,
        "maintenance_due_date": due_date.isoformat(),
        "proposed_date": proposed_date.isoformat(),
        "proposed_slot": proposed_slot,
        "service_center_id": center_id,
        "service_center_location": center.get("location"),
        "status": proposal.status,
    }


# ---------------------------------------------------------
# SCAN DUE MAINTENANCE
# ---------------------------------------------------------

@router.post("/scan")
def scan_due_maintenance(
    user_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    Check due appliances and create pending proposals.

    Optional user_id limits the scan to one user.
    This endpoint does not confirm any booking.
    """
    query = db.query(Appliance)

    if user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        query = query.filter(Appliance.user_id == user_id)

    appliances = query.order_by(Appliance.id.asc()).all()
    results = []

    for appliance in appliances:
        user = db.query(User).filter(
            User.id == appliance.user_id
        ).first()

        if user is None:
            results.append({
                "appliance_id": appliance.id,
                "result": "USER_NOT_FOUND",
            })
            continue

        try:
            result = scan_appliance(appliance, user, db)
            results.append(result)
        except (OSError, ValueError, TypeError) as exc:
            db.rollback()
            results.append({
                "appliance_id": appliance.id,
                "result": "SCAN_ERROR",
                "detail": str(exc),
            })

    return {
        "checked_count": len(appliances),
        "results": results,
    }


# ---------------------------------------------------------
# LIST PROPOSALS FOR A USER
# ---------------------------------------------------------

@router.get("/user/{user_id}")
def get_user_proposals(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    proposals = (
        db.query(MaintenanceProposal)
        .filter(MaintenanceProposal.user_id == user_id)
        .order_by(MaintenanceProposal.id.desc())
        .all()
    )

    return [
        {
            "id": proposal.id,
            "user_id": proposal.user_id,
            "appliance_id": proposal.appliance_id,
            "maintenance_due_date": (
                proposal.maintenance_due_date.isoformat()
            ),
            "proposed_date": (
                proposal.proposed_date.isoformat()
                if proposal.proposed_date else None
            ),
            "proposed_slot": proposal.proposed_slot,
            "service_center_id": proposal.service_center_id,
            "status": proposal.status,
            "created_at": proposal.created_at.isoformat(),
        }
        for proposal in proposals
    ]


# ---------------------------------------------------------
# APPROVE A PROPOSAL
# ---------------------------------------------------------

@router.post("/{proposal_id}/approve")
def approve_proposal(
    proposal_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    proposal = (
        db.query(MaintenanceProposal)
        .filter(
            MaintenanceProposal.id == proposal_id,
            MaintenanceProposal.user_id == user_id,
        )
        .first()
    )

    if proposal is None:
        raise HTTPException(
            status_code=404,
            detail="Maintenance proposal not found",
        )

    if proposal.status != "PENDING":
        raise HTTPException(
            status_code=409,
            detail=f"Proposal cannot be approved from status {proposal.status}",
        )

    if (
        proposal.proposed_date is None
        or proposal.proposed_slot is None
        or proposal.service_center_id is None
    ):
        raise HTTPException(
            status_code=409,
            detail="This proposal does not have a bookable slot",
        )

    if proposal.proposed_date < date.today():
        raise HTTPException(
            status_code=409,
            detail="The proposed appointment date has passed",
        )

    conflict = (
        db.query(Booking)
        .filter(
            Booking.service_center_id == proposal.service_center_id,
            Booking.booking_date == proposal.proposed_date,
            Booking.booking_slot == proposal.proposed_slot,
            Booking.status == "CONFIRMED",
        )
        .first()
    )

    if conflict:
        raise HTTPException(
            status_code=409,
            detail="This demo slot has already been booked. Please run a new scan.",
        )

    booking = Booking(
        user_id=proposal.user_id,
        appliance_id=proposal.appliance_id,
        service_center_id=proposal.service_center_id,
        booking_date=proposal.proposed_date,
        booking_slot=proposal.proposed_slot,
        status="CONFIRMED",
    )

    proposal.status = "APPROVED"

    db.add(booking)

    try:
        db.commit()
        db.refresh(booking)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="The booking could not be saved because of a data conflict",
        )

    return {
        "message": "Proposal approved and demo booking created",
        "proposal_id": proposal.id,
        "proposal_status": proposal.status,
        "booking_id": booking.id,
        "booking_date": booking.booking_date.isoformat(),
        "booking_slot": booking.booking_slot,
        "service_center_id": booking.service_center_id,
        "booking_status": booking.status,
    }


# ---------------------------------------------------------
# DECLINE A PROPOSAL
# ---------------------------------------------------------

@router.post("/{proposal_id}/decline")
def decline_proposal(
    proposal_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    proposal = (
        db.query(MaintenanceProposal)
        .filter(
            MaintenanceProposal.id == proposal_id,
            MaintenanceProposal.user_id == user_id,
        )
        .first()
    )

    if proposal is None:
        raise HTTPException(
            status_code=404,
            detail="Maintenance proposal not found",
        )

    if proposal.status != "PENDING":
        raise HTTPException(
            status_code=409,
            detail=f"Proposal cannot be declined from status {proposal.status}",
        )

    proposal.status = "DECLINED"
    db.commit()

    return {
        "message": "Maintenance proposal declined",
        "proposal_id": proposal.id,
        "status": proposal.status,
        "booking_created": False,
    }
