from pydantic import BaseModel
from typing import Optional


class ValidationResult(BaseModel):
    rule: str
    valid: bool
    message: str
    severity: str = "error"  # error, warning, info
