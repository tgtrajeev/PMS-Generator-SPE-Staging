"""
Module 5: Pipe Schedule Selection
Selects pipe schedule per ASME B36.10 (CS) or ASME B36.19 (SS).
Schedule >= Calculated minimum thickness.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import PIPE_DIMENSIONS_B36_10, PIPE_DIMENSIONS_B36_19


def select_pipe_schedule(pipe_size_nps, min_thickness_in, material_type):
    """
    Select the appropriate pipe schedule based on minimum required thickness.

    Args:
        pipe_size_nps: Nominal Pipe Size (string, e.g., "6")
        min_thickness_in: Minimum required wall thickness in inches
        material_type: CS, CS-LT, SS, or Alloy

    Returns:
        dict with schedule selection results
    """
    # Choose the right dimension table
    if material_type == "SS":
        dim_table = PIPE_DIMENSIONS_B36_19
        standard = "ASME B36.19"
    else:
        dim_table = PIPE_DIMENSIONS_B36_10
        standard = "ASME B36.10"

    nps = str(pipe_size_nps)
    if nps not in dim_table:
        # Try B36.10 as fallback for SS if size not in B36.19
        if material_type == "SS" and nps in PIPE_DIMENSIONS_B36_10:
            dim_table = PIPE_DIMENSIONS_B36_10
            standard = "ASME B36.10 (B36.19 N/A for this size)"
        else:
            raise ValueError(f"Pipe size NPS {nps} not found in {standard}")

    od, schedules = dim_table[nps]

    # Sort schedules by wall thickness
    sorted_schedules = sorted(schedules.items(), key=lambda x: x[1])

    # Find the minimum schedule that meets the thickness requirement
    selected_schedule = None
    selected_thickness = None
    for sch, wt in sorted_schedules:
        if wt >= min_thickness_in:
            selected_schedule = sch
            selected_thickness = wt
            break

    if selected_schedule is None:
        # Use the thickest available
        selected_schedule, selected_thickness = sorted_schedules[-1]
        warning = "WARNING: Maximum available schedule may not meet thickness requirement!"
    else:
        warning = None

    # PASS/FAIL verification
    pass_fail = "PASS" if selected_thickness >= min_thickness_in else "FAIL"

    result = {
        "pipe_size_nps": nps,
        "pipe_od_in": od,
        "standard": standard,
        "selected_schedule": selected_schedule,
        "selected_wall_thickness_in": selected_thickness,
        "selected_wall_thickness_mm": round(selected_thickness * 25.4, 2),
        "min_required_thickness_in": round(min_thickness_in, 4),
        "id_in": round(od - 2 * selected_thickness, 3),
        "id_mm": round((od - 2 * selected_thickness) * 25.4, 2),
        "all_schedules": dict(sorted_schedules),
        "pass_fail": pass_fail,
        "warning": warning,
    }

    print(f"\n" + "=" * 65)
    print(f"  PIPE SCHEDULE SELECTION ({standard})")
    print("=" * 65)
    print(f"\n  NPS {nps} (OD = {od} in)")
    print(f"  Min Required Thickness: {min_thickness_in:.4f} in")
    print(f"\n  Available Schedules:")
    print(f"  {'Schedule':<10} {'Wall (in)':<12} {'Wall (mm)':<12} {'Status'}")
    print(f"  {'-'*10} {'-'*12} {'-'*12} {'-'*15}")

    for sch, wt in sorted_schedules:
        status = ""
        if sch == selected_schedule:
            status = "<-- SELECTED"
        elif wt < min_thickness_in:
            status = "(insufficient)"
        print(f"  {sch:<10} {wt:<12.3f} {wt*25.4:<12.2f} {status}")

    print(f"\n  Selected: Schedule {selected_schedule} "
          f"(WT = {selected_thickness:.3f} in / {selected_thickness*25.4:.2f} mm)")
    print(f"  Pipe ID:  {result['id_in']:.3f} in ({result['id_mm']:.2f} mm)")
    print(f"  Status:   {pass_fail} (WT {selected_thickness:.3f} >= t_req {min_thickness_in:.4f})")

    if warning:
        print(f"\n  *** {warning} ***")

    print("  " + "-" * 55)

    return result
