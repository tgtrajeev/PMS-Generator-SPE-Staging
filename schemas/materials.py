from pydantic import BaseModel
from typing import Optional


class MaterialResponse(BaseModel):
    id: int
    grade: str
    description: str
    type: str
    spec: str
    smts: int
    smys: int


class CorrosionAllowanceResponse(BaseModel):
    non_corrosive: float
    mildly_corrosive: float
    corrosive: float
