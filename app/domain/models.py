from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship

from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)
    fuel_capacity = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)

    trip_logs = relationship("TripLog", back_populates="vehicle", cascade="all, delete-orphan")


class TripLog(Base):
    __tablename__ = "trip_logs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    distance_km = Column(Float, nullable=False)
    fuel_consumed_liters = Column(Float, nullable=False)
    carbon_emitted_kg = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="trip_logs")
