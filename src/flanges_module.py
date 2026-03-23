"""
Module 7: Flanges, Gaskets & Bolting
Selects flange rating (ASME B16.5), gasket type/material, and stud bolt/nut material.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import (
    FLANGE_RATINGS_CS, FLANGE_RATINGS_SS,
    FLANGE_MATERIALS, GASKET_MATERIALS, BOLTING_MATERIALS
)


def select_flange_rating(design_pressure_psig, design_temp_f, material_type):
    """
    Select the appropriate flange pressure class per ASME B16.5.

    Args:
        design_pressure_psig: Design pressure in psig
        design_temp_f: Design temperature in degF
        material_type: CS, CS-LT, SS, or Alloy

    Returns:
        Selected flange class (150, 300, 600, etc.)
    """
    if material_type in ("SS",):
        ratings = FLANGE_RATINGS_SS
    else:
        ratings = FLANGE_RATINGS_CS

    # Find the temperature row (round up to nearest rating temperature)
    temps = sorted(ratings.keys())
    rating_temp = temps[-1]  # default to highest
    for t in temps:
        if t >= design_temp_f:
            rating_temp = t
            break

    # Find the minimum class that can handle the design pressure
    pressure_ratings = ratings[rating_temp]
    classes = sorted(pressure_ratings.keys())

    selected_class = None
    for cls in classes:
        if pressure_ratings[cls] >= design_pressure_psig:
            selected_class = cls
            break

    if selected_class is None:
        selected_class = classes[-1]  # Use highest class

    return selected_class, rating_temp, pressure_ratings


def select_flanges_gaskets_bolting(material_grade, material_type,
                                   design_pressure_psig, design_temp_f):
    """
    Complete selection of flanges, gaskets, and bolting materials.

    Returns:
        dict with all flange/gasket/bolting data
    """
    # Flange rating
    flange_class, rating_temp, all_ratings = select_flange_rating(
        design_pressure_psig, design_temp_f, material_type
    )

    # Flange material
    flange_mat = FLANGE_MATERIALS.get(material_grade, {})
    flange_spec = flange_mat.get("flange", "N/A")
    flange_types = flange_mat.get("type", "WN/SO/BL")

    # Gasket
    gasket = GASKET_MATERIALS.get(material_type, GASKET_MATERIALS["CS"])

    # Bolting
    bolting = BOLTING_MATERIALS.get(material_type, BOLTING_MATERIALS["CS"])

    # Flange face type based on class
    if flange_class <= 600:
        face_type = "Raised Face (RF)"
        face_finish = "125-250 AARH"
    else:
        face_type = "Ring Type Joint (RTJ)"
        face_finish = "Per ASME B16.5"

    result = {
        "flange": {
            "class": flange_class,
            "rating_temp_f": rating_temp,
            "material": flange_spec,
            "types": flange_types,
            "face_type": face_type,
            "face_finish": face_finish,
            "standard": "ASME B16.5",
            "max_pressure_at_temp": all_ratings.get(flange_class, "N/A"),
        },
        "gasket": {
            "type": gasket["type"],
            "material": gasket["material"],
            "inner_ring": gasket["inner"],
            "filler": gasket["filler"],
            "standard": gasket["spec"],
        },
        "bolting": {
            "stud_bolt": bolting["stud"],
            "nut": bolting["nut"],
            "temp_range": bolting["temp_range"],
            "standard": "ASME B16.5 / B18.2.1",
        },
    }

    # Print summary
    print(f"\n" + "=" * 65)
    print(f"  FLANGES, GASKETS & BOLTING (ASME B16.5)")
    print("=" * 65)

    print(f"\n  Design Conditions: {design_pressure_psig} psig @ {design_temp_f} degF")

    print(f"\n  FLANGE:")
    print(f"    Pressure Class:    #{flange_class}")
    print(f"    Material:          {flange_spec}")
    print(f"    Types:             {flange_types}")
    print(f"    Face Type:         {face_type}")
    print(f"    Face Finish:       {face_finish}")
    print(f"    Standard:          ASME B16.5")

    print(f"\n  Pressure-Temperature Ratings @ {rating_temp} degF:")
    for cls in sorted(all_ratings.keys()):
        marker = " <-- SELECTED" if cls == flange_class else ""
        print(f"    Class {cls:>5}: {all_ratings[cls]:>6} psig{marker}")

    print(f"\n  GASKET:")
    print(f"    Type:              {gasket['type']}")
    print(f"    Material:          {gasket['material']}")
    print(f"    Inner Ring:        {gasket['inner']}")
    print(f"    Filler:            {gasket['filler']}")
    print(f"    Standard:          {gasket['spec']}")

    print(f"\n  BOLTING:")
    print(f"    Stud Bolt:         {bolting['stud']}")
    print(f"    Nut:               {bolting['nut']}")
    print(f"    Temp Range:        {bolting['temp_range']}")

    print("  " + "-" * 55)

    return result
