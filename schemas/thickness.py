from pydantic import BaseModel, Field


class ThicknessRequest(BaseModel):
    pipe_size: str = "6"
    material_type: str = "CS"
    material_grade: str = "A106 Gr.B"
    design_pressure: float = Field(gt=0, description="Design pressure in psig")
    design_temp: float = Field(description="Design temperature in degF")
    ca_inches: float = Field(ge=0, description="Corrosion allowance in inches")
    joint_type: str = "seamless"


class ThicknessResponse(BaseModel):
    design_pressure_psig: float
    pipe_od_in: float
    material_grade: str
    design_temp_f: float
    allowable_stress_psi: float
    joint_efficiency: float
    joint_type: str
    y_factor: float
    corrosion_allowance_in: float
    t_calculated_in: float
    t_min_required_in: float
    mill_tolerance_pct: float
    t_nominal_min_in: float
    t_nominal_min_mm: float
