"""
Saved Specifications CRUD API router.
"""

import os
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import SavedSpec

router = APIRouter()

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")


def _spec_to_dict(s, include_pms_data=True):
    """Convert a SavedSpec ORM object to a dict for JSON response."""
    pms_data = {}
    if include_pms_data and s.pms_data_json:
        try:
            pms_data = json.loads(s.pms_data_json) if isinstance(s.pms_data_json, str) else s.pms_data_json
        except (json.JSONDecodeError, TypeError):
            pass

    # Check if the Excel file still exists on disk
    file_exists = False
    if s.excel_filename:
        file_exists = os.path.exists(os.path.join(OUTPUT_DIR, s.excel_filename))

    return {
        "id":                   s.id,
        "project_name":         s.project_name,
        "doc_number":           s.doc_number,
        "revision":             s.revision,
        "spec_code":            s.spec_code,
        "material_grade":       s.material_grade,
        "material_type":        s.material_type,
        "pipe_size":            s.pipe_size,
        # Metric fields (preferred)
        "design_pressure_barg": getattr(s, "design_pressure_barg", None),
        "design_temp_c":        getattr(s, "design_temp_c", None),
        "corrosion_allowance":  getattr(s, "corrosion_allowance", None),
        "flange_class":         getattr(s, "flange_class", None),
        "service":              getattr(s, "service", None),
        "is_nace":              bool(getattr(s, "is_nace", 0)),
        "is_low_temp":          bool(getattr(s, "is_low_temp", 0)),
        # Legacy fields
        "design_pressure":      s.design_pressure,
        "design_temp":          s.design_temp,
        # File
        "excel_filename":       s.excel_filename,
        "file_exists":          file_exists,
        "created_at":           s.created_at.isoformat() if s.created_at else None,
        "pms_data":             pms_data,
    }


@router.get("/specs")
async def list_specs(db: Session = Depends(get_db)):
    specs = db.query(SavedSpec).order_by(SavedSpec.created_at.desc()).all()
    return [_spec_to_dict(s) for s in specs]


@router.get("/specs/{spec_id}")
async def get_spec(spec_id: int, db: Session = Depends(get_db)):
    spec = db.query(SavedSpec).filter(SavedSpec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")
    return _spec_to_dict(spec)


@router.delete("/specs/{spec_id}")
async def delete_spec(spec_id: int, db: Session = Depends(get_db)):
    spec = db.query(SavedSpec).filter(SavedSpec.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")
    db.delete(spec)
    db.commit()
    return {"success": True}
