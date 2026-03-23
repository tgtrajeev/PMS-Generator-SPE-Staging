"""
Materials API router - material listing, corrosion allowance, pipe sizes, flange ratings.
"""

from fastapi import APIRouter

from src.msr_module import MATERIAL_OPTIONS, get_material_type
from data.reference_data import (
    ALLOWABLE_STRESS, PIPE_DIMENSIONS_B36_10, PIPE_DIMENSIONS_B36_19,
    TYPICAL_CA, FLANGE_RATINGS_CS, FLANGE_RATINGS_SS,
    FLANGE_RATINGS_CS_METRIC, FLANGE_RATINGS_SS_METRIC,
    PRESSURE_RATING_CODES,
)

router = APIRouter()


@router.get("/materials")
async def get_materials():
    materials = []
    for num, (grade, desc) in MATERIAL_OPTIONS.items():
        mat_type = get_material_type(grade)
        props = ALLOWABLE_STRESS[grade]
        materials.append({
            "id": num,
            "grade": grade,
            "description": desc,
            "type": mat_type,
            "spec": props["spec"],
            "smts": props["smts"],
            "smys": props["smys"],
        })
    return materials


@router.get("/corrosion_allowance")
async def get_corrosion_allowance(material_type: str = "CS"):
    ca_data = TYPICAL_CA.get(material_type, TYPICAL_CA["CS"])
    return ca_data


@router.get("/pipe_sizes")
async def get_pipe_sizes(material_type: str = "CS"):
    if material_type == "SS":
        sizes = list(PIPE_DIMENSIONS_B36_19.keys())
    else:
        sizes = list(PIPE_DIMENSIONS_B36_10.keys())
    return sizes


@router.get("/flange_ratings")
async def get_flange_ratings(material_type: str = "CS"):
    if material_type == "SS":
        return {str(k): v for k, v in FLANGE_RATINGS_SS.items()}
    return {str(k): v for k, v in FLANGE_RATINGS_CS.items()}


@router.get("/pressure_rating_codes")
async def get_pressure_rating_codes():
    return PRESSURE_RATING_CODES


@router.get("/pt_rating_table")
async def get_pt_rating_table(
    pressure_class: int = 150,
    material_type: str = "CS",
):
    """
    Return P-T rating table for a given pressure class and material type.
    Classes 150-2500: ASME B16.5-2020 Metric tables (direct bar/°C values, no conversion error)
    Classes 5000-10000: API 6A (converted from FLANGE_RATINGS_CS/SS)
    Returns temperatures in °C and pressures in barg.
    """
    # Determine applicable standard
    if pressure_class <= 2500:
        standard = "ASME B16.5-2020"
        # Use metric tables directly (proper °C / bar values)
        metric_ratings = FLANGE_RATINGS_SS_METRIC if material_type in ("SS",) else FLANGE_RATINGS_CS_METRIC
        pt_pairs = []
        for temp_c in sorted(metric_ratings.keys()):
            class_pressures = metric_ratings[temp_c]
            if pressure_class in class_pressures:
                pressure_barg = class_pressures[pressure_class]
                temp_f = round(temp_c * 9 / 5 + 32)
                pressure_psig = round(pressure_barg / 0.0689476)
                pt_pairs.append({
                    "temp_f": temp_f,
                    "temp_c": temp_c,
                    "pressure_psig": pressure_psig,
                    "pressure_barg": pressure_barg,
                })
    else:
        standard = "API 6A"
        # API 6A classes use imperial tables — convert to metric
        imperial_ratings = FLANGE_RATINGS_SS if material_type in ("SS",) else FLANGE_RATINGS_CS
        pt_pairs = []
        for temp_f in sorted(imperial_ratings.keys()):
            class_pressures = imperial_ratings[temp_f]
            if pressure_class in class_pressures:
                temp_c = round((temp_f - 32) * 5 / 9)
                pressure_psig = class_pressures[pressure_class]
                pressure_barg = round(pressure_psig * 0.0689476, 1)
                pt_pairs.append({
                    "temp_f": temp_f,
                    "temp_c": temp_c,
                    "pressure_psig": pressure_psig,
                    "pressure_barg": pressure_barg,
                })

    return {
        "pressure_class": pressure_class,
        "material_type": material_type,
        "standard": standard,
        "pt_pairs": pt_pairs,
    }
