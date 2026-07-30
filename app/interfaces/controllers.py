from datetime import datetime
from typing import List, Optional
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.repositories import get_vehicle, list_vehicles
from app.use_cases.fleet_services import (
    get_fleet_total_emissions,
    record_trip_and_calculate_emissions,
    register_vehicle,
)

router = APIRouter(prefix="/api", tags=["fleet"])
api_router = router


# --- Pydantic Schemas ---

class VehicleCreate(BaseModel):
    name: str = Field(..., example="Tesla Model Y")
    vehicle_type: str = Field(..., example="EV")
    fuel_capacity: float = Field(..., example=75.0)
    is_active: bool = Field(True, example=True)


class VehicleResponse(BaseModel):
    id: int
    name: str
    vehicle_type: str
    fuel_capacity: float
    is_active: bool

    class Config:
        from_attributes = True


class TripCreate(BaseModel):
    vehicle_id: int = Field(..., example=1)
    distance_km: float = Field(..., example=120.5)
    fuel_consumed_liters: float = Field(..., example=15.0)
    timestamp: Optional[datetime] = None


class TripResponse(BaseModel):
    id: int
    vehicle_id: int
    distance_km: float
    fuel_consumed_liters: float
    carbon_emitted_kg: float
    timestamp: datetime

    class Config:
        from_attributes = True


class EmissionsSummaryResponse(BaseModel):
    total_carbon_emitted_kg: float
    unit: str = "kg CO2"
    vehicle_id: Optional[int] = None


# --- API Routes ---

@router.post("/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle_endpoint(vehicle_in: VehicleCreate, db: Session = Depends(get_db)):
    return register_vehicle(
        db=db,
        name=vehicle_in.name,
        vehicle_type=vehicle_in.vehicle_type,
        fuel_capacity=vehicle_in.fuel_capacity,
        is_active=vehicle_in.is_active,
    )


@router.get("/vehicles", response_model=List[VehicleResponse])
def get_vehicles_endpoint(db: Session = Depends(get_db)):
    return list_vehicles(db=db)


@router.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip_endpoint(trip_in: TripCreate, db: Session = Depends(get_db)):
    vehicle = get_vehicle(db, trip_in.vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with id {trip_in.vehicle_id} not found",
        )
    return record_trip_and_calculate_emissions(
        db=db,
        vehicle_id=trip_in.vehicle_id,
        distance_km=trip_in.distance_km,
        fuel_consumed_liters=trip_in.fuel_consumed_liters,
        timestamp=trip_in.timestamp,
    )


@router.get("/trips", response_model=List[TripResponse])
def get_trips_endpoint(vehicle_id: Optional[int] = None, db: Session = Depends(get_db)):
    from app.domain.models import TripLog
    query = db.query(TripLog)
    if vehicle_id:
        query = query.filter(TripLog.vehicle_id == vehicle_id)
    return query.order_by(TripLog.timestamp.desc()).all()


@router.get("/analytics/emissions", response_model=EmissionsSummaryResponse)
def get_emissions_summary_endpoint(
    vehicle_id: Optional[int] = None, db: Session = Depends(get_db)
):
    total = get_fleet_total_emissions(db=db, vehicle_id=vehicle_id)
    return EmissionsSummaryResponse(
        total_carbon_emitted_kg=total,
        unit="kg CO2",
        vehicle_id=vehicle_id,
    )
