from pydantic import BaseModel
from typing import Optional


class ValvesRequest(BaseModel):
    material_type: str = "CS"
    flange_class: int = 150
    pipe_size: str = "6"
    spec_code: str = "A1"
    line_number: str = ""


class ValvesResponse(BaseModel):
    valves: dict
    end_connection: str
    pressure_class: int
