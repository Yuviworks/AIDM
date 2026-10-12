from sqlalchemy import Column, Integer, String, Date, ForeignKey
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

    status = Column(String, default="CONFIRMED")