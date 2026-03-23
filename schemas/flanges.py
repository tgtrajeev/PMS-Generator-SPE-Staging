from pydantic import BaseModel, Field


class FlangesRequest(BaseModel):
    material_grade: str = "A106 Gr.B"
    material_type: str = "CS"
    design_pressure: float = Field(gt=0)
    design_temp: float


class FlangesResponse(BaseModel):
    flange: dict
    gasket: dict
    bolting: dict
