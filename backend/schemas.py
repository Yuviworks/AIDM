
from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr


# ============================================================
# USER
# ============================================================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    location: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    location: str

    class Config:
        from_attributes = True


# ============================================================
# APPLIANCE
# ============================================================

class ApplianceCreate(BaseModel):
    user_id: int

    appliance_type: Literal[
        "Water Purifier"
    ]

    brand: Literal[
        "KENT"
    ]

    model: Literal[
        "KENT Elegant",
        "KENT Grand",
        "KENT Sterling Star"
    ]

    installation_date: date
    last_service_date: date
    maintenance_interval: int


class ApplianceResponse(BaseModel):
    id: int
    user_id: int
    appliance_type: str
    brand: str
    model: str
    installation_date: date
    last_service_date: date
    maintenance_interval: int

    class Config:
        from_attributes = True


# ============================================================
# RAG
# ============================================================

class RAGQuery(BaseModel):
    query: str
    model: str


# ============================================================
# BOOKING
# ============================================================

class BookingCreate(BaseModel):
    user_id: int
    appliance_id: int
    service_center_id: int
    booking_date: date
    booking_slot: str | None = None


class BookingResponse(BaseModel):
    id: int
    user_id: int
    appliance_id: int
    service_center_id: int
    booking_date: date
    booking_slot: str | None
    status: str

    class Config:
        from_attributes = True
