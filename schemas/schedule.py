from pydantic import BaseModel, Field
from typing import Optional


class ScheduleRequest(BaseModel):
    pipe_size: str = "6"
    min_thickness: float = Field(default=0.1, ge=0)
    material_type: str = "CS"


class ScheduleResponse(BaseModel):
    pipe_size_nps: str
    pipe_od_in: float
    standard: str
    min_required_thickness_in: float
    selected_schedule: str
    selected_wall_thickness_in: float
    selected_wall_thickness_mm: float
    id_in: float
    warning: Optional[str] = None
    all_schedules: dict
