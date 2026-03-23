"""
Module 2: Specification Code Selection
Matches material type and corrosion allowance to a piping spec code.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import SPEC_CODE_MAP


def select_spec_code(material_type, corrosion_allowance_mm):
    """
    Determine the piping specification code based on material type and CA.

    Args:
        material_type: CS, CS-LT, SS, or Alloy
        corrosion_allowance_mm: Corrosion allowance in mm

    Returns:
        dict with spec code details
    """
    # Find the closest matching CA
    key = (material_type, corrosion_allowance_mm)
    spec_code = SPEC_CODE_MAP.get(key)

    if not spec_code:
        # Find nearest CA match for the material type
        matching_keys = [(k, v) for k, v in SPEC_CODE_MAP.items() if k[0] == material_type]
        if matching_keys:
            nearest = min(matching_keys, key=lambda x: abs(x[0][1] - corrosion_allowance_mm))
            spec_code = nearest[1]
            used_ca = nearest[0][1]
        else:
            spec_code = "CUSTOM"
            used_ca = corrosion_allowance_mm
    else:
        used_ca = corrosion_allowance_mm

    result = {
        "spec_code": spec_code,
        "material_type": material_type,
        "corrosion_allowance_mm": used_ca,
        "pms_reference": f"PMS-{spec_code}",
    }

    print(f"\n  Specification Code Selection:")
    print(f"    Material Type:       {material_type}")
    print(f"    Corrosion Allowance: {used_ca} mm")
    print(f"    Spec Code:           {spec_code}")
    print(f"    PMS Reference:       PMS-{spec_code}")

    return result


def get_spec_description(spec_code):
    """Return a human-readable description for a spec code."""
    descriptions = {
        "A1":   "Carbon Steel, 1.5mm CA, General Service",
        "A1A":  "Carbon Steel, 2.0mm CA, Moderate Service",
        "A2":   "Carbon Steel, 3.0mm CA, Corrosive Service",
        "A2A":  "Carbon Steel, 4.5mm CA, Severe Service",
        "A3":   "Carbon Steel, No CA, Non-corrosive",
        "A4":   "Carbon Steel, 6.0mm CA, Highly Corrosive",
        "A1LN": "Carbon Steel Low Temp, 1.5mm CA",
        "A2LN": "Carbon Steel Low Temp, 3.0mm CA",
        "A3LN": "Carbon Steel Low Temp, No CA",
        "A4LN": "Carbon Steel Low Temp, 6.0mm CA, Highly Corrosive",
        "S1":   "Stainless Steel 304/316, No CA",
        "S2":   "Stainless Steel 304/316, 1.5mm CA",
        "D1":   "Stainless Steel 304/316, 3.0mm CA, Corrosive",
        "B1":   "Alloy Steel, No CA",
        "B2":   "Alloy Steel, 1.5mm CA",
        "B3":   "Alloy Steel, 3.0mm CA, Corrosive",
    }
    return descriptions.get(spec_code, "Custom Specification")
