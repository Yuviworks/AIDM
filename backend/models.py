from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class Appliance(Base):
    __tablename__ = "appliances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appliance_type = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    installation_date = Column(Date, nullable=False)
    last_service_date = Column(Date, nullable=False)
    maintenance_interval = Column(Integer, nullable=False)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appliance_id = Column(Integer, ForeignKey("appliances.id"), nullable=False)
    service_center_id = Column(Integer, nullable=False)
    booking_date = Column(Date, nullable=False)
    booking_slot = Column(String, nullable=True)
    status = Column(String, default="CONFIRMED", nullable=False)


class MaintenanceProposal(Base):
    __tablename__ = "maintenance_proposals"
    __table_args__ = (
        UniqueConstraint("appliance_id", "maintenance_due_date", name="uq_proposal_appliance_due_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    appliance_id = Column(Integer, ForeignKey("appliances.id"), nullable=False, index=True)
    service_center_id = Column(Integer, nullable=False)
    maintenance_due_date = Column(Date, nullable=False)
    proposed_date = Column(Date, nullable=False)
    proposed_slot = Column(String, nullable=False)
    status = Column(String, default="PENDING", nullable=False, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)
