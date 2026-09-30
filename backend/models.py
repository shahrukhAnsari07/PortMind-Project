from typing import List, Optional
from pydantic import BaseModel, Field

class Resources(BaseModel):
    vessels: int = Field(4, ge=1, le=30)
    berths: int = Field(2, ge=1, le=10)
    cranes: Optional[int] = Field(None, ge=1, le=20)
    trucks: int = Field(12, ge=1, le=100)
    yards: int = Field(4, ge=1, le=30)

class Vessel(BaseModel):
    name: str
    arrival_time: float = Field(0, ge=0)
    service_time: float = Field(120, gt=0)
    containers: int = Field(500, gt=0)
    priority: int = Field(2, ge=1, le=3)

class Scenario(BaseModel):
    resources: Resources = Resources()
    vessels: Optional[List[Vessel]] = None
    delayed_vessel: Optional[str] = None
    delay_minutes: float = Field(0, ge=0, le=1440)
    failed_crane: Optional[int] = Field(None, ge=1, le=20)
    closed_berth: Optional[int] = Field(None, ge=1, le=10)
    weather: str = "Normal"
    truck_shortage: int = Field(0, ge=0, le=100)
    blocked_yard: Optional[int] = Field(None, ge=1, le=30)
    yard_reduction_pct: float = Field(0, ge=0, le=100)
    objective: List[str] = ["waiting", "crane", "yard", "priority"]

class AIScenario(BaseModel):
    message: str
    state: Optional[dict] = None
