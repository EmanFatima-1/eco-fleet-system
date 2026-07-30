from datetime import datetime
from typing import List, Optional
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.domain.models import TripLog, Vehicle
from app.infrastructure.repositories import (
    add_vehicle,
    calculate_total_carbon_footprint,
    get_vehicle,
    get_vehicles,
    list_vehicles,
    log_trip,
)


def calculate_carbon_emissions(vehicle_type: str, fuel_consumed_liters: float) -> float:
    if not vehicle_type:
        return 0.0

    v_type = vehicle_type.strip().lower()
    if "ev" in v_type or "electric" in v_type:
        factor = 0.0
    elif "diesel" in v_type:
        factor = 2.68
    elif "hybrid" in v_type:
        factor = 1.5
    elif "petrol" in v_type or "gas" in v_type:
        factor = 2.31
    else:
        # Default emission factor per liter if unspecified (e.g. 2.5 kg/L)
        factor = 2.5

    return round(fuel_consumed_liters * factor, 4)


def register_vehicle(
    db: Session,
    name: str,
    vehicle_type: str,
    fuel_capacity: float,
    is_active: bool = True,
) -> Vehicle:
    return add_vehicle(
        db=db,
        name=name,
        vehicle_type=vehicle_type,
        fuel_capacity=fuel_capacity,
        is_active=is_active,
    )


def record_trip_and_calculate_emissions(
    db: Session,
    vehicle_id: int,
    distance_km: float,
    fuel_consumed_liters: float,
    vehicle_type: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> TripLog:
    if not vehicle_type:
        vehicle = get_vehicle(db, vehicle_id)
        if vehicle:
            vehicle_type = vehicle.vehicle_type
        else:
            vehicle_type = "default"

    carbon_emitted_kg = calculate_carbon_emissions(vehicle_type, fuel_consumed_liters)

    return log_trip(
        db=db,
        vehicle_id=vehicle_id,
        distance_km=distance_km,
        fuel_consumed_liters=fuel_consumed_liters,
        carbon_emitted_kg=carbon_emitted_kg,
        timestamp=timestamp or datetime.utcnow(),
    )


def get_fleet_total_emissions(db: Session, vehicle_id: Optional[int] = None) -> float:
    return calculate_total_carbon_footprint(db, vehicle_id=vehicle_id)


class FleetService:
    def __init__(self, db: Session):
        self.db = db

    def register_vehicle(
        self,
        name: str,
        vehicle_type: str,
        fuel_capacity: float,
        is_active: bool = True,
    ) -> Vehicle:
        return register_vehicle(
            self.db,
            name=name,
            vehicle_type=vehicle_type,
            fuel_capacity=fuel_capacity,
            is_active=is_active,
        )

    def record_trip_and_calculate_emissions(
        self,
        vehicle_id: int,
        distance_km: float,
        fuel_consumed_liters: float,
        vehicle_type: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> TripLog:
        return record_trip_and_calculate_emissions(
            self.db,
            vehicle_id=vehicle_id,
            distance_km=distance_km,
            fuel_consumed_liters=fuel_consumed_liters,
            vehicle_type=vehicle_type,
            timestamp=timestamp,
        )

    def get_total_carbon_footprint(self, vehicle_id: Optional[int] = None) -> float:
        return get_fleet_total_emissions(self.db, vehicle_id=vehicle_id)
