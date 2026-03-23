"""
Validation API router - engineering validation rules.
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/validate")
async def validate_pms(data: dict):
    from src.validation_engine import validate_all
    results = validate_all(data)
    return results
