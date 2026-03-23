"""
PMS generation API router - generate Excel, download files.
"""

import os
import io
import json
from contextlib import redirect_stdout

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.pms_generator import generate_pms_excel
from db.database import get_db
from db.models import SavedSpec

router = APIRouter()

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")


@router.post("/generate_pms")
async def api_generate_pms(data: dict, db: Session = Depends(get_db)):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate the Excel file
    excel_path = None
    gen_error = None
    try:
        f = io.StringIO()
        with redirect_stdout(f):
            excel_path = generate_pms_excel(data, OUTPUT_DIR)
    except Exception as exc:
        gen_error = str(exc)

    if not excel_path:
        return {"success": False, "error": gen_error or "Excel generation failed", "filename": None}

    filename = os.path.basename(excel_path)

    # Extract all engineering fields for dedicated DB columns
    msr           = data.get("msr", {})
    line_list     = data.get("line_list", {})
    metadata      = data.get("metadata", {})
    sc            = data.get("spec_code", {})
    svc           = data.get("service", {})
    flanges_data  = data.get("flanges", {})
    fl            = flanges_data.get("flange", {}) if isinstance(flanges_data, dict) else {}

    # Pressure / temperature (prefer metric from service step, fallback to legacy)
    dp_barg = svc.get("design_pressure") or line_list.get("design_pressure_barg")
    dt_c    = svc.get("design_temperature") or line_list.get("design_temp_c")
    try:
        dp_barg = float(dp_barg) if dp_barg is not None else None
        dt_c    = float(dt_c)    if dt_c    is not None else None
    except (TypeError, ValueError):
        dp_barg = dp_c = None

    # Save to database
    save_error = None
    try:
        saved = SavedSpec(
            project_name       = metadata.get("project", ""),
            doc_number         = metadata.get("doc_number", ""),
            revision           = metadata.get("revision", "0"),
            spec_code          = sc.get("spec_code", ""),
            material_grade     = msr.get("material_grade", ""),
            material_type      = msr.get("material_type", ""),
            pipe_size          = line_list.get("pipe_size_nps", ""),
            # Legacy (psig/°F) kept for backward compatibility
            design_pressure    = line_list.get("design_pressure_psig"),
            design_temp        = line_list.get("design_temp_f"),
            # Engineering fields
            design_pressure_barg = dp_barg,
            design_temp_c        = dt_c,
            corrosion_allowance  = sc.get("corrosion_allowance"),
            flange_class         = str(fl.get("class", sc.get("pressure_class", ""))),
            service              = svc.get("service_description", line_list.get("fluid", "")),
            is_nace              = 1 if sc.get("is_nace") else 0,
            is_low_temp          = 1 if sc.get("is_low_temp") else 0,
            pms_data_json        = json.dumps(data),
            excel_filename       = filename,
        )
        db.add(saved)
        db.commit()
    except Exception as e:
        db.rollback()
        save_error = str(e)

    return {
        "success": True,
        "filename": filename,
        "saved_to_db": save_error is None,
        "db_error": save_error,
    }


@router.get("/download/{filename}")
async def download_file(filename: str):
    # Sanitise filename — no path traversal
    filename = os.path.basename(filename)
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return FileResponse(
            filepath, filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    return {"error": "File not found"}
