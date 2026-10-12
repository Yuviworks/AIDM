from datetime import date, datetime, timedelta
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Appliance, Booking, MaintenanceProposal
from ..services.maintenance_service import calculate_maintenance
from ..services.service_service import find_nearest_service_center, load_service_centers

router = APIRouter(prefix="/maintenance-proposals", tags=["Proactive Maintenance"])


def _proposal_payload(proposal, db):
    appliance = db.query(Appliance).filter(Appliance.id == proposal.appliance_id).first()
    center = next((item for item in load_service_centers() if item.get("id") == proposal.service_center_id), None)
    return {
        "id": proposal.id,
        "user_id": proposal.user_id,
        "appliance_id": proposal.appliance_id,
        "appliance_model": appliance.model if appliance else "KENT purifier",
        "maintenance_due_date": proposal.maintenance_due_date.isoformat(),
        "proposed_date": proposal.proposed_date.isoformat(),
        "proposed_slot": proposal.proposed_slot,
        "service_center_id": proposal.service_center_id,
        "service_center_name": center.get("name") if center else "Demo service center",
        "service_center_location": center.get("location") if center else "",
        "status": proposal.status,
        "booking_id": proposal.booking_id,
        "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
    }


def generate_due_proposals(db: Session):
    reminder_days = max(0, int(os.getenv("MAINTENANCE_REMINDER_DAYS", "7")))
    today = date.today()
    horizon = today + timedelta(days=reminder_days)
    appliances = db.query(Appliance).all()
    created = 0

    for appliance in appliances:
        due_date = calculate_maintenance(appliance)["next_maintenance_date"]
        if due_date > horizon:
            continue
        existing = db.query(MaintenanceProposal).filter(
            MaintenanceProposal.appliance_id == appliance.id,
            MaintenanceProposal.maintenance_due_date == due_date,
        ).first()
        if existing:
            continue
        confirmed_booking = db.query(Booking).filter(
            Booking.appliance_id == appliance.id,
            Booking.booking_date >= today,
            Booking.status == "CONFIRMED",
        ).first()
        if confirmed_booking:
            continue
        center = find_nearest_service_center(appliance.brand, "Pune")
        if not center:
            continue
        future_slots = []
        for raw_slot in center.get("available_slots", []):
            try:
                slot_date = datetime.strptime(raw_slot, "%Y-%m-%d %I:%M %p").date()
            except ValueError:
                continue
            if slot_date >= today:
                future_slots.append((slot_date, raw_slot))
        if not future_slots:
            continue
        proposed_date, proposed_slot = min(
            future_slots, key=lambda item: (abs((item[0] - due_date).days), item[0])
        )
        db.add(MaintenanceProposal(
            user_id=appliance.user_id,
            appliance_id=appliance.id,
            service_center_id=center["id"],
            maintenance_due_date=due_date,
            proposed_date=proposed_date,
            proposed_slot=proposed_slot,
            status="PENDING",
        ))
        created += 1

    if created:
        db.commit()
    return {"created": created, "checked": len(appliances), "reminder_window_days": reminder_days}


@router.post("/scan")
def scan_maintenance_proposals(db: Session = Depends(get_db)):
    """Manually trigger a scan for local development and demonstrations."""
    return generate_due_proposals(db)


@router.get("/user/{user_id}")
def get_user_proposals(
    user_id: int,
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(MaintenanceProposal).filter(MaintenanceProposal.user_id == user_id)
    if status:
        query = query.filter(MaintenanceProposal.status == status.upper())
    return [_proposal_payload(item, db) for item in query.order_by(MaintenanceProposal.created_at.desc()).all()]


@router.post("/{proposal_id}/respond")
def respond_to_proposal(
    proposal_id: int,
    user_id: int,
    decision: str = Query(description="confirm or decline"),
    db: Session = Depends(get_db),
):
    proposal = db.query(MaintenanceProposal).filter(
        MaintenanceProposal.id == proposal_id,
        MaintenanceProposal.user_id == user_id,
    ).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Maintenance proposal not found")
    if proposal.status != "PENDING":
        raise HTTPException(status_code=409, detail=f"Proposal is already {proposal.status.lower()}")
    normalized = decision.strip().lower()
    if normalized not in {"confirm", "decline"}:
        raise HTTPException(status_code=422, detail="Decision must be confirm or decline")

    if normalized == "decline":
        proposal.status = "DECLINED"
        proposal.responded_at = datetime.utcnow()
        db.commit()
        return {"message": "Proposal declined; no appointment was booked.", "proposal": _proposal_payload(proposal, db)}

    center = next((item for item in load_service_centers() if item.get("id") == proposal.service_center_id), None)
    if not center or proposal.proposed_slot not in center.get("available_slots", []):
        raise HTTPException(status_code=409, detail="Suggested demo slot is no longer listed as available.")
    slot_date = datetime.strptime(proposal.proposed_slot, "%Y-%m-%d %I:%M %p").date()
    if slot_date < date.today():
        raise HTTPException(status_code=409, detail="Suggested slot has passed. Request a new proposal.")

    booking = Booking(
        user_id=proposal.user_id,
        appliance_id=proposal.appliance_id,
        service_center_id=proposal.service_center_id,
        booking_date=slot_date,
        booking_slot=proposal.proposed_slot,
        status="CONFIRMED",
    )
    db.add(booking)
    db.flush()
    proposal.status = "CONFIRMED"
    proposal.booking_id = booking.id
    proposal.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(proposal)
    return {
        "message": "Appointment recorded as confirmed in AIDM.",
        "booking_id": booking.id,
        "provider_notice": "Demo only: no external service provider was contacted.",
        "proposal": _proposal_payload(proposal, db),
    }
