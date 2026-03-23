"""
Validation Engine for PMS Generator.
Implements engineering validation rules per ASME standards.

Rules:
1. Schedule wall thickness >= calculated minimum thickness
2. Flange rating >= design pressure at design temperature
3. Gasket temperature limit > design temperature
4. Material-fluid compatibility check
5. MDMT compliance per UCS-66 impact test exemption curves
6. Corrosion allowance advisory per fluid service
7. Branch reinforcement per ASME B31.3 para 304.3
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import (
    FLANGE_RATINGS_CS, FLANGE_RATINGS_SS,
    GASKET_TEMP_LIMITS, MATERIAL_FLUID_INCOMPATIBLE,
    UCS_66_CURVES, MATERIAL_UCS66_CURVE, CA_RECOMMENDATIONS,
)


def validate_schedule_thickness(pms_data):
    """Rule 1: Schedule wall thickness must be >= calculated minimum thickness."""
    sched = pms_data.get("schedule", {})
    thick = pms_data.get("thickness", {})

    selected_wt = sched.get("selected_wall_thickness_in", 0)
    min_required = thick.get("t_nominal_min_in", 0)

    if not selected_wt or not min_required:
        return {
            "rule": "Schedule vs Thickness",
            "valid": True,
            "message": "Insufficient data to validate.",
            "severity": "info",
        }

    selected_wt = float(selected_wt)
    min_required = float(min_required)
    margin = selected_wt - min_required

    if selected_wt >= min_required:
        return {
            "rule": "Schedule vs Thickness",
            "valid": True,
            "message": f"PASS: Schedule WT ({selected_wt:.4f} in) >= min required ({min_required:.4f} in). Margin: {margin:.4f} in.",
            "severity": "info",
        }
    return {
        "rule": "Schedule vs Thickness",
        "valid": False,
        "message": f"FAIL: Schedule WT ({selected_wt:.4f} in) < min required ({min_required:.4f} in). Deficit: {abs(margin):.4f} in.",
        "severity": "error",
    }


def validate_flange_rating(pms_data):
    """Rule 2: Flange rating must handle design pressure at design temperature."""
    flanges = pms_data.get("flanges", {})
    line = pms_data.get("line_list", {})
    msr = pms_data.get("msr", {})

    flange_class = flanges.get("flange", {}).get("class")
    design_pressure = line.get("design_pressure_psig")
    design_temp_f = line.get("design_temp_f")
    mat_type = msr.get("material_type", "CS")

    if not flange_class or not design_pressure or design_temp_f is None:
        return {
            "rule": "Flange Rating vs Pressure",
            "valid": True,
            "message": "Insufficient data to validate.",
            "severity": "info",
        }

    flange_class = int(flange_class)
    design_pressure = float(design_pressure)
    design_temp_f = float(design_temp_f)

    # Look up the ratings table
    ratings = FLANGE_RATINGS_SS if mat_type == "SS" else FLANGE_RATINGS_CS

    # Find the closest temperature at or above design temp
    temps = sorted(ratings.keys())
    max_pressure = None
    for temp in temps:
        if temp >= design_temp_f:
            class_ratings = ratings[temp]
            max_pressure = class_ratings.get(flange_class, 0)
            break

    if max_pressure is None:
        # Use highest temperature available
        class_ratings = ratings[temps[-1]]
        max_pressure = class_ratings.get(flange_class, 0)

    if max_pressure >= design_pressure:
        return {
            "rule": "Flange Rating vs Pressure",
            "valid": True,
            "message": f"PASS: Class #{flange_class} max pressure ({max_pressure} psig) >= design pressure ({design_pressure} psig) at {design_temp_f} degF.",
            "severity": "info",
        }
    return {
        "rule": "Flange Rating vs Pressure",
        "valid": False,
        "message": f"FAIL: Class #{flange_class} max pressure ({max_pressure} psig) < design pressure ({design_pressure} psig) at {design_temp_f} degF.",
        "severity": "error",
    }


def validate_gasket_temp(pms_data):
    """Rule 3: Gasket temperature limit must exceed design temperature."""
    flanges = pms_data.get("flanges", {})
    line = pms_data.get("line_list", {})

    gasket_type = flanges.get("gasket", {}).get("type", "")
    design_temp_f = line.get("design_temp_f")

    if not gasket_type or design_temp_f is None:
        return {
            "rule": "Gasket Temperature Limit",
            "valid": True,
            "message": "Insufficient data to validate.",
            "severity": "info",
        }

    design_temp_f = float(design_temp_f)

    # Find matching gasket limit
    temp_limit = None
    for key, limit in GASKET_TEMP_LIMITS.items():
        if key.lower() in gasket_type.lower() or gasket_type.lower() in key.lower():
            temp_limit = limit
            break

    if temp_limit is None:
        temp_limit = GASKET_TEMP_LIMITS.get("Spiral Wound", 850)

    if temp_limit > design_temp_f:
        return {
            "rule": "Gasket Temperature Limit",
            "valid": True,
            "message": f"PASS: Gasket limit ({temp_limit} degF) > design temp ({design_temp_f} degF).",
            "severity": "info",
        }
    return {
        "rule": "Gasket Temperature Limit",
        "valid": False,
        "message": f"FAIL: Gasket limit ({temp_limit} degF) <= design temp ({design_temp_f} degF). Select higher-rated gasket.",
        "severity": "error",
    }


def validate_material_fluid(pms_data):
    """Rule 4: Material must be compatible with fluid service."""
    msr = pms_data.get("msr", {})
    line = pms_data.get("line_list", {})

    mat_type = msr.get("material_type", "")
    fluid = line.get("fluid", "")

    if not mat_type or not fluid:
        return {
            "rule": "Material-Fluid Compatibility",
            "valid": True,
            "message": "Insufficient data to validate.",
            "severity": "info",
        }

    incompatible_list = MATERIAL_FLUID_INCOMPATIBLE.get(mat_type, [])
    warnings = []
    for incomp in incompatible_list:
        # Check if fluid contains keywords from incompatible list
        incomp_keywords = incomp.lower().split()
        fluid_lower = fluid.lower()
        if any(kw in fluid_lower for kw in incomp_keywords if len(kw) > 3):
            warnings.append(incomp)

    if not warnings:
        return {
            "rule": "Material-Fluid Compatibility",
            "valid": True,
            "message": f"PASS: {mat_type} is compatible with '{fluid}'. No known incompatibilities.",
            "severity": "info",
        }
    return {
        "rule": "Material-Fluid Compatibility",
        "valid": False,
        "message": f"WARNING: {mat_type} may be incompatible with '{fluid}'. Known issues: {', '.join(warnings)}.",
        "severity": "warning",
    }


# ── NEW RULES ────────────────────────────────────────────────


def _interpolate_ucs66(curve_data, thickness):
    """Interpolate UCS-66 curve to find min exempt temperature for a given thickness."""
    thicknesses = sorted(curve_data.keys())

    # Below minimum thickness in table - use the minimum
    if thickness <= thicknesses[0]:
        return curve_data[thicknesses[0]]

    # Above maximum thickness in table - use the maximum
    if thickness >= thicknesses[-1]:
        return curve_data[thicknesses[-1]]

    # Linear interpolation between bracketing thicknesses
    for i in range(len(thicknesses) - 1):
        t_low = thicknesses[i]
        t_high = thicknesses[i + 1]
        if t_low <= thickness <= t_high:
            temp_low = curve_data[t_low]
            temp_high = curve_data[t_high]
            fraction = (thickness - t_low) / (t_high - t_low)
            return temp_low + fraction * (temp_high - temp_low)

    return curve_data[thicknesses[-1]]


def validate_mdmt_compliance(pms_data):
    """Rule 5: MDMT compliance per UCS-66 impact test exemption curves.

    Checks if the MDMT is above the UCS-66 curve exemption temperature
    for the material and governing thickness. If below, impact testing is required.
    """
    msr = pms_data.get("msr", {})
    line = pms_data.get("line_list", {})
    sched = pms_data.get("schedule", {})

    material_grade = msr.get("material_grade", "")
    mdmt_f = line.get("mdmt_f")
    governing_thickness = sched.get("selected_wall_thickness_in")

    if not material_grade or mdmt_f is None or not governing_thickness:
        return {
            "rule": "MDMT Compliance (UCS-66)",
            "valid": True,
            "message": "Insufficient data to validate MDMT compliance.",
            "severity": "info",
        }

    mdmt_f = float(mdmt_f)
    governing_thickness = float(governing_thickness)

    # Look up the curve assignment for this material
    # Strip leading "SA-" or "A" prefix variations for lookup
    grade_key = material_grade.replace("SA-", "A")
    curve_id = MATERIAL_UCS66_CURVE.get(grade_key)

    if curve_id is None:
        # Try matching with original grade
        curve_id = MATERIAL_UCS66_CURVE.get(material_grade)

    if curve_id is None:
        return {
            "rule": "MDMT Compliance (UCS-66)",
            "valid": True,
            "message": f"INFO: Material '{material_grade}' not in UCS-66 curve table. Verify impact test requirements manually.",
            "severity": "info",
        }

    # Austenitic stainless steels are exempt
    if curve_id == "exempt":
        return {
            "rule": "MDMT Compliance (UCS-66)",
            "valid": True,
            "message": f"PASS: {material_grade} is austenitic stainless steel - impact testing not required per UCS-66.",
            "severity": "info",
        }

    # Get the curve data and interpolate
    curve_data = UCS_66_CURVES.get(curve_id)
    if not curve_data:
        return {
            "rule": "MDMT Compliance (UCS-66)",
            "valid": True,
            "message": f"INFO: UCS-66 Curve {curve_id} data not available.",
            "severity": "info",
        }

    min_exempt_temp = _interpolate_ucs66(curve_data, governing_thickness)

    if mdmt_f >= min_exempt_temp:
        return {
            "rule": "MDMT Compliance (UCS-66)",
            "valid": True,
            "message": (
                f"PASS: MDMT ({mdmt_f:.0f} degF) >= UCS-66 Curve {curve_id} exemption "
                f"({min_exempt_temp:.0f} degF) at {governing_thickness:.3f} in thickness. "
                f"Impact test exemption applies."
            ),
            "severity": "info",
        }

    return {
        "rule": "MDMT Compliance (UCS-66)",
        "valid": False,
        "message": (
            f"WARNING: MDMT ({mdmt_f:.0f} degF) is below UCS-66 Curve {curve_id} exemption "
            f"({min_exempt_temp:.0f} degF) at {governing_thickness:.3f} in thickness. "
            f"Impact testing IS REQUIRED per ASME B31.3."
        ),
        "severity": "warning",
    }


def validate_ca_advisory(pms_data):
    """Rule 6: Corrosion allowance advisory based on fluid service.

    Provides engineering guidance on whether the selected CA is within
    typical industry ranges for the specified fluid.
    """
    msr = pms_data.get("msr", {})
    line = pms_data.get("line_list", {})

    ca_mm = msr.get("corrosion_allowance_mm")
    fluid = line.get("fluid", "")

    if ca_mm is None or not fluid:
        return {
            "rule": "CA Advisory",
            "valid": True,
            "message": "Insufficient data for CA advisory.",
            "severity": "info",
        }

    ca_mm = float(ca_mm)

    # Find matching fluid recommendation (keyword match)
    recommendation = None
    fluid_lower = fluid.lower()
    for fluid_key, rec in CA_RECOMMENDATIONS.items():
        if fluid_key.lower() in fluid_lower or fluid_lower in fluid_key.lower():
            recommendation = rec
            matched_fluid = fluid_key
            break

    if recommendation is None:
        return {
            "rule": "CA Advisory",
            "valid": True,
            "message": f"PASS: No specific CA recommendation for '{fluid}'. User-specified {ca_mm} mm accepted.",
            "severity": "info",
        }

    typical_low, typical_high = recommendation["typical_mm"]
    note = recommendation["note"]

    if typical_low <= ca_mm <= typical_high:
        return {
            "rule": "CA Advisory",
            "valid": True,
            "message": f"PASS: CA of {ca_mm} mm is within typical range ({typical_low}-{typical_high} mm) for {matched_fluid}. {note}.",
            "severity": "info",
        }
    elif ca_mm > typical_high:
        return {
            "rule": "CA Advisory",
            "valid": True,
            "message": (
                f"INFO: CA of {ca_mm} mm is conservative for {matched_fluid}. "
                f"Typical range: {typical_low}-{typical_high} mm. {note}. "
                f"Not incorrect, but may result in slightly overdesigned piping."
            ),
            "severity": "info",
        }
    else:
        return {
            "rule": "CA Advisory",
            "valid": False,
            "message": (
                f"WARNING: CA of {ca_mm} mm may be insufficient for {matched_fluid}. "
                f"Typical range: {typical_low}-{typical_high} mm. {note}. "
                f"Verify with corrosion engineer."
            ),
            "severity": "warning",
        }


def validate_branch_reinforcement(pms_data):
    """Rule 7: Branch reinforcement per ASME B31.3 para 304.3.

    Uses the area replacement method: checks if header excess thickness
    provides sufficient reinforcement for branch openings.
    """
    sched = pms_data.get("schedule", {})
    thick = pms_data.get("thickness", {})
    line = pms_data.get("line_list", {})

    header_wt = sched.get("selected_wall_thickness_in")
    min_required = thick.get("t_nominal_min_in")
    nps_str = line.get("pipe_size_nps", "")

    if not header_wt or not min_required or not nps_str:
        return {
            "rule": "Branch Reinforcement (B31.3 304.3)",
            "valid": True,
            "message": "Insufficient data to validate branch reinforcement.",
            "severity": "info",
        }

    header_wt = float(header_wt)
    min_required = float(min_required)
    try:
        nps = float(nps_str)
    except (ValueError, TypeError):
        return {
            "rule": "Branch Reinforcement (B31.3 304.3)",
            "valid": True,
            "message": "Cannot parse pipe size for branch reinforcement check.",
            "severity": "info",
        }

    # Area replacement method (simplified per B31.3 304.3.3)
    # Assume worst case: equal-size branch (d1 = header ID opening)
    # For a branch equal to half the header size (typical worst case scenario)
    d1 = nps / 2.0  # Branch opening diameter (assume half of header NPS as typical)

    # Required reinforcement area
    A_required = min_required * d1

    # Available area from header excess thickness (both sides of opening)
    excess_header = header_wt - min_required
    A_header_excess = 2.0 * excess_header * d1

    # Available area from branch excess (assume branch has same schedule)
    # Branch required thickness approximated as proportional
    branch_min_t = min_required * (d1 / nps) if nps > 0 else min_required
    branch_excess = header_wt - branch_min_t  # Assume same schedule
    L_branch = min(2.5 * header_wt, 2.5 * d1)  # Height of reinforcement zone
    A_branch_excess = 2.0 * branch_excess * L_branch

    A_available = A_header_excess + A_branch_excess
    deficit = A_required - A_available

    if A_available >= A_required:
        ratio = A_available / A_required if A_required > 0 else 999
        return {
            "rule": "Branch Reinforcement (B31.3 304.3)",
            "valid": True,
            "message": (
                f"PASS: Branch reinforcement adequate from excess thickness. "
                f"Available area: {A_available:.4f} sq.in >= Required: {A_required:.4f} sq.in "
                f"(ratio: {ratio:.1f}x). No reinforcing pad required."
            ),
            "severity": "info",
        }
    return {
        "rule": "Branch Reinforcement (B31.3 304.3)",
        "valid": False,
        "message": (
            f"WARNING: Branch reinforcement pad may be required per ASME B31.3 para 304.3. "
            f"Available area: {A_available:.4f} sq.in < Required: {A_required:.4f} sq.in. "
            f"Deficit: {deficit:.4f} sq.in. Verify with detailed calculation for actual branch sizes."
        ),
        "severity": "warning",
    }


def validate_all(pms_data):
    """Run all validation rules and return results."""
    results = [
        validate_schedule_thickness(pms_data),
        validate_flange_rating(pms_data),
        validate_gasket_temp(pms_data),
        validate_material_fluid(pms_data),
        validate_mdmt_compliance(pms_data),
        validate_ca_advisory(pms_data),
        validate_branch_reinforcement(pms_data),
    ]
    return results
