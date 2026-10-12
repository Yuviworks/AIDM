
from datetime import date

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    UniqueConstraint,
)

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    location = Column(String, nullable=False, default="Pune")


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

    status = Column(String, default="CONFIRMED")


class MaintenanceProposal(Base):
    __tablename__ = "maintenance_proposals"

    __table_args__ = (
        UniqueConstraint(
            "appliance_id",
            "maintenance_due_date",
            name="uq_appliance_maintenance_due_date",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appliance_id = Column(
        Integer,
        ForeignKey("appliances.id"),
        nullable=False,
    )

    maintenance_due_date = Column(Date, nullable=False)
    proposed_date = Column(Date, nullable=True)
    proposed_slot = Column(String, nullable=True)
    service_center_id = Column(Integer, nullable=True)

    status = Column(String, nullable=False, default="PENDING")
    created_at = Column(Date, nullable=False, default=date.today)
