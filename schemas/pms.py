from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PMSGenerateResponse(BaseModel):
    success: bool
    filename: Optional[str] = None


class SavedSpecResponse(BaseModel):
    id: int
    project_name: str
    doc_number: str
    revision: str
    spec_code: str
    material_grade: str
    material_type: str
    pipe_size: str
    design_pressure: float
    design_temp: float
    created_at: Optional[str] = None
    excel_filename: Optional[str] = None

    class Config:
        from_attributes = True
