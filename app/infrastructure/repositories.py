from typing import List, Optional
# pyrefly: ignore [missing-import]
from sqlalchemy import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.domain.models import TripLog, Vehicle


def add_vehicle(
    db: Session,
    vehicle: Optional[Vehicle] = None,
    name: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    fuel_capacity: Optional[float] = None,
    is_active: bool = True,
) -> Vehicle:
    if vehicle is None:
        vehicle = Vehicle(
            name=name,
            vehicle_type=vehicle_type,
            fuel_capacity=fuel_capacity,
            is_active=is_active,
        )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def get_vehicle(db: Session, vehicle_id: int) -> Optional[Vehicle]:
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def list_vehicles(db: Session, skip: int = 0, limit: int = 100) -> List[Vehicle]:
    return db.query(Vehicle).offset(skip).limit(limit).all()


def get_vehicles(db: Session, skip: int = 0, limit: int = 100) -> List[Vehicle]:
    return list_vehicles(db, skip=skip, limit=limit)


def log_trip(
    db: Session,
    trip_log: Optional[TripLog] = None,
    vehicle_id: Optional[int] = None,
    distance_km: Optional[float] = None,
    fuel_consumed_liters: Optional[float] = None,
    carbon_emitted_kg: Optional[float] = None,
    timestamp=None,
) -> TripLog:
    if trip_log is None:
        kwargs = {}
        if vehicle_id is not None:
            kwargs["vehicle_id"] = vehicle_id
        if distance_km is not None:
            kwargs["distance_km"] = distance_km
        if fuel_consumed_liters is not None:
            kwargs["fuel_consumed_liters"] = fuel_consumed_liters
        if carbon_emitted_kg is not None:
            kwargs["carbon_emitted_kg"] = carbon_emitted_kg
        if timestamp is not None:
            kwargs["timestamp"] = timestamp
        trip_log = TripLog(**kwargs)
    db.add(trip_log)
    db.commit()
    db.refresh(trip_log)
    return trip_log


def add_trip_log(db: Session, **kwargs) -> TripLog:
    return log_trip(db, **kwargs)


def calculate_total_carbon_footprint(db: Session, vehicle_id: Optional[int] = None) -> float:
    query = db.query(func.sum(TripLog.carbon_emitted_kg))
    if vehicle_id is not None:
        query = query.filter(TripLog.vehicle_id == vehicle_id)
    total = query.scalar()
    return float(total) if total is not None else 0.0


def get_total_carbon_footprint(db: Session, vehicle_id: Optional[int] = None) -> float:
    return calculate_total_carbon_footprint(db, vehicle_id=vehicle_id)


class VehicleRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, name: str, vehicle_type: str, fuel_capacity: float, is_active: bool = True) -> Vehicle:
        return add_vehicle(self.db, name=name, vehicle_type=vehicle_type, fuel_capacity=fuel_capacity, is_active=is_active)

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        return get_vehicle(self.db, vehicle_id)

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        return list_vehicles(self.db, skip=skip, limit=limit)


class TripLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_trip(self, vehicle_id: int, distance_km: float, fuel_consumed_liters: float, carbon_emitted_kg: float, timestamp=None) -> TripLog:
        return log_trip(
            self.db,
            vehicle_id=vehicle_id,
            distance_km=distance_km,
            fuel_consumed_liters=fuel_consumed_liters,
            carbon_emitted_kg=carbon_emitted_kg,
            timestamp=timestamp,
        )

    def get_total_carbon(self, vehicle_id: Optional[int] = None) -> float:
        return calculate_total_carbon_footprint(self.db, vehicle_id=vehicle_id)
