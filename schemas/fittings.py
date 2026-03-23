from pydantic import BaseModel
from typing import Any


class FittingsRequest(BaseModel):
    material_grade: str = "A106 Gr.B"
    pipe_size: str = "6"
    schedule: str = "40"
    material_type: str = "CS"


class FittingsResponse(BaseModel):
    pipe: dict
    elbow_90: dict
    elbow_45: dict
    tee_equal: dict
    tee_reducing: dict
    reducer_concentric: dict
    reducer_eccentric: dict
    cap: dict
    branch_connections: dict
    small_bore_fittings: dict | None = None
