"""
Components API router - fittings, flanges, valves assignment.
"""

import io
from contextlib import redirect_stdout

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.fittings_module import assign_fittings
from src.flanges_module import select_flanges_gaskets_bolting
from src.valve_module import select_valves

router = APIRouter()


class FittingsRequest(BaseModel):
    material_grade: str = "A106 Gr.B"
    pipe_size: str = "6"
    schedule: str = "40"
    material_type: str = "CS"


class FlangesRequest(BaseModel):
    material_grade: str = "A106 Gr.B"
    material_type: str = "CS"
    design_pressure: float = Field(gt=0)
    design_temp: float = 300


class ValvesRequest(BaseModel):
    material_type: str = "CS"
    flange_class: int = 150
    pipe_size: str = "6"
    spec_code: str = "A1"
    line_number: str = ""


@router.post("/assign_fittings")
async def api_assign_fittings(req: FittingsRequest):
    f = io.StringIO()
    with redirect_stdout(f):
        result = assign_fittings(
            material_grade=req.material_grade,
            pipe_size_nps=req.pipe_size,
            schedule=req.schedule,
            material_type=req.material_type,
        )
    return result


@router.post("/select_flanges")
async def api_select_flanges(req: FlangesRequest):
    f = io.StringIO()
    with redirect_stdout(f):
        result = select_flanges_gaskets_bolting(
            material_grade=req.material_grade,
            material_type=req.material_type,
            design_pressure_psig=req.design_pressure,
            design_temp_f=req.design_temp,
        )
    return result


@router.post("/select_valves")
async def api_select_valves(req: ValvesRequest):
    f = io.StringIO()
    with redirect_stdout(f):
        result = select_valves(
            material_type=req.material_type,
            flange_class=req.flange_class,
            pipe_size_nps=req.pipe_size,
            spec_code=req.spec_code,
            line_number=req.line_number,
        )
    return result
