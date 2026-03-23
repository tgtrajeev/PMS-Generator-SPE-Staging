"""
Module: PMS Code Generator (3-Part Naming Convention)
Generates PMS codes in format [Part1][Part2][Part3]
Part 1: Pressure rating letter (A-T)
Part 2: Material + CA number (1-60)
Part 3: Optional identifier (N/L for non-tubing, A/B/C for tubing, or None)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import (
    PRESSURE_RATING_CODES,
    PMS_MATERIAL_CODES,
    PMS_TUBING_CODES,
    PMS_NON_METALLIC_CODES,
    PMS_PART3_TUBING,
    PMS_PART3_NON_TUBING,
    PMS_GRADE_TO_PART2,
    PMS_LOW_TEMP_GRADES,
)


def auto_suggest_part1(design_pressure_psig):
    """Find lowest pressure class >= design pressure."""
    ordered = [
        ("A", 150), ("B", 300), ("D", 600), ("E", 900),
        ("F", 1500), ("G", 2500), ("J", 5000), ("K", 10000),
    ]
    for code, psig in ordered:
        if design_pressure_psig <= psig:
            return {"code": code, "rating": PRESSURE_RATING_CODES[code]["rating"],
                    "confidence": "auto"}
    return {"code": "K", "rating": "10000#", "confidence": "auto"}


def auto_suggest_part2(material_grade, corrosion_allowance_mm):
    """Lookup PMS_GRADE_TO_PART2 mapping."""
    ca = round(corrosion_allowance_mm, 1)
    key = (material_grade, ca)
    code = PMS_GRADE_TO_PART2.get(key)
    if code is not None:
        info = PMS_MATERIAL_CODES[code]
        return {"code": code, "material_type": info["material_type"],
                "description": info["description"], "ca_mm": info["ca_mm"],
                "confidence": "auto"}

    # Try nearest CA for same grade
    grade_keys = {k: v for k, v in PMS_GRADE_TO_PART2.items() if k[0] == material_grade}
    if grade_keys:
        nearest = min(grade_keys.items(), key=lambda x: abs(x[0][1] - ca))
        code = nearest[1]
        info = PMS_MATERIAL_CODES[code]
        return {"code": code, "material_type": info["material_type"],
                "description": info["description"], "ca_mm": info["ca_mm"],
                "confidence": "nearest"}

    return None


def auto_suggest_part3(material_grade, mdmt_f=None, part1_code=None):
    """Suggest Part 3 based on material and conditions."""
    if part1_code == "T":
        return {"code": None, "reason": "Select tubing pressure if applicable"}

    if material_grade in PMS_LOW_TEMP_GRADES:
        return {"code": "L", "reason": f"{material_grade} is a low-temperature grade",
                "description": PMS_PART3_NON_TUBING["L"]["description"]}

    if mdmt_f is not None and mdmt_f < -20:
        return {"code": "L", "reason": f"LDMT ({mdmt_f}°F) is below -20°F",
                "description": PMS_PART3_NON_TUBING["L"]["description"]}

    return {"code": None, "reason": "No modifier needed"}


def validate_pms_code(part1, part2, part3=None):
    """Validate the 3-part PMS code combination.

    Part 3 can now be multi-character:
      - Non-tubing: "L", "N", or "LN" (must be L before N)
      - Tubing: "A", "B", or "C"
    """
    errors = []
    warnings = []

    if part1 not in PRESSURE_RATING_CODES:
        errors.append(f"Invalid Part 1 code: '{part1}'")
        return {"valid": False, "errors": errors, "warnings": warnings}

    if part2 not in PMS_MATERIAL_CODES:
        errors.append(f"Invalid Part 2 code: '{part2}'")
        return {"valid": False, "errors": errors, "warnings": warnings}

    is_tubing_material = part2 in PMS_TUBING_CODES
    is_tubing_rating = (part1 == "T")
    is_non_metallic = part2 in PMS_NON_METALLIC_CODES

    # Rule 1 & 2: Tubing consistency
    if is_tubing_material and not is_tubing_rating:
        errors.append(f"Tubing material (code {part2}) requires Rating = T (Tubing)")
    if is_tubing_rating and not is_tubing_material:
        errors.append(f"Rating T (Tubing) can only be used with tubing materials (codes 50, 60)")

    # Rule 3 & 4: Part 3 modifier validation
    if part3:
        valid_tubing_modifiers = set(PMS_PART3_TUBING.keys())        # {"A", "B", "C"}
        valid_non_tubing_chars = set(PMS_PART3_NON_TUBING.keys())    # {"N", "L"}

        if is_tubing_rating:
            # Tubing: Part 3 must be a single tubing modifier (A, B, or C)
            if part3 not in valid_tubing_modifiers:
                errors.append(f"Modifier '{part3}' is not valid for tubing. Use A, B, or C.")
        else:
            # Non-tubing: Part 3 can be "L", "N", or "LN"
            if part3 in valid_tubing_modifiers:
                errors.append(f"Modifier '{part3}' (tubing pressure) is only valid for Rating = T")
            else:
                # Check each character is valid
                valid_chars = all(ch in valid_non_tubing_chars for ch in part3)
                if not valid_chars:
                    errors.append(f"Invalid Part 3 modifier: '{part3}'. Valid: L, N, or LN")
                elif len(part3) > 2:
                    errors.append(f"Part 3 modifier too long: '{part3}'. Maximum is 'LN'")
                elif len(part3) == 2 and part3 != "LN":
                    errors.append(f"Invalid ordering: '{part3}'. Must be 'LN' (L before N)")

    # Rule 5: Non-metallic + NACE
    if is_non_metallic and part3 and "N" in part3:
        warnings.append("Non-metallic materials typically do not require NACE designation")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def generate_pms_code(part1, part2, part3=None):
    """Assemble the final PMS code string and full description.

    Part 3 can be multi-character (e.g. "LN"), in which case each
    character's description is included separately.
    """
    part1_info = PRESSURE_RATING_CODES.get(part1, {})
    part2_info = PMS_MATERIAL_CODES.get(part2, {})

    code = f"{part1}{part2}"
    if part3:
        code += part3

    desc_parts = [part1_info.get("rating", "")]
    desc_parts.append(part2_info.get("description", ""))
    if part2_info.get("ca_mm", 0) > 0:
        desc_parts.append(f"{part2_info['ca_mm']}mm CA")
    else:
        desc_parts.append("No CA")

    # Build part3 description — support multi-char (e.g. "LN")
    part3_info = None
    if part3:
        # Check if it's a single tubing modifier first
        single_info = PMS_PART3_TUBING.get(part3) or PMS_PART3_NON_TUBING.get(part3)
        if single_info:
            desc_parts.append(single_info["description"])
            part3_info = single_info
        else:
            # Multi-char: build description from each character
            p3_descriptions = []
            p3_combined_info = {}
            for ch in part3:
                ch_info = PMS_PART3_NON_TUBING.get(ch)
                if ch_info:
                    p3_descriptions.append(ch_info["description"])
                    p3_combined_info[ch] = ch_info
            if p3_descriptions:
                desc_parts.extend(p3_descriptions)
                part3_info = {"description": " + ".join(p3_descriptions), "components": p3_combined_info}

    return {
        "pms_code": code,
        "description": ", ".join(desc_parts),
        "pms_reference": f"PMS-{code}",
        "part1": part1,
        "part2": part2,
        "part3": part3,
        "part1_info": part1_info,
        "part2_info": part2_info,
        "part3_info": part3_info,
    }


def get_suggestions(part1, part2, part3=None):
    """Return alternative PMS codes as suggestions."""
    suggestions = []
    part2_info = PMS_MATERIAL_CODES.get(part2, {})
    is_tubing = (part1 == "T")
    is_non_metallic = part2 in PMS_NON_METALLIC_CODES

    if not is_tubing and not is_non_metallic:
        if not part3:
            # Suggest NACE variant
            code = generate_pms_code(part1, part2, "N")
            suggestions.append({
                "pms_code": code["pms_code"],
                "reason": "Add NACE for sour service environments",
            })
            # Suggest Low Temp variant
            code = generate_pms_code(part1, part2, "L")
            suggestions.append({
                "pms_code": code["pms_code"],
                "reason": "Add Low Temperature for cryogenic/cold service",
            })
            # Suggest combined LN variant
            code = generate_pms_code(part1, part2, "LN")
            suggestions.append({
                "pms_code": code["pms_code"],
                "reason": "Low Temperature + NACE combined",
            })
        elif part3 == "L":
            # Suggest adding NACE too
            code = generate_pms_code(part1, part2, "LN")
            suggestions.append({
                "pms_code": code["pms_code"],
                "reason": "Add NACE for sour + low temp service",
            })
        elif part3 == "N":
            # Suggest adding Low Temp too
            code = generate_pms_code(part1, part2, "LN")
            suggestions.append({
                "pms_code": code["pms_code"],
                "reason": "Add Low Temperature for cold + sour service",
            })

    # Suggest higher CA variant if available
    mat_type = part2_info.get("material_type", "")
    same_mat_codes = sorted(
        [(c, i) for c, i in PMS_MATERIAL_CODES.items()
         if i["material_type"] == mat_type and c != part2],
        key=lambda x: x[1]["ca_mm"]
    )
    for alt_code, alt_info in same_mat_codes:
        if alt_info["ca_mm"] > part2_info.get("ca_mm", 0):
            code = generate_pms_code(part1, alt_code, part3)
            suggestions.append({
                "pms_code": code["pms_code"],
                "reason": f"Higher CA ({alt_info['ca_mm']}mm) for more corrosive service",
            })
            break

    return suggestions[:3]
