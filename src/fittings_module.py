"""
Module 6: Pipe & Fittings Material Assignment
Assigns material codes for pipes, elbows, tees, reducers, and branch fittings.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import FITTING_MATERIALS, BRANCH_CONNECTIONS, PIPE_DIMENSIONS_B36_10


def assign_fittings(material_grade, pipe_size_nps, schedule, material_type):
    """
    Assign material specifications for pipe fittings.

    Args:
        material_grade: e.g., "A106 Gr.B"
        pipe_size_nps: Nominal Pipe Size (string)
        schedule: Selected pipe schedule
        material_type: CS, CS-LT, SS, Alloy

    Returns:
        dict with fitting assignments
    """
    fittings = FITTING_MATERIALS.get(material_grade)
    if not fittings:
        raise ValueError(f"No fitting data for material: {material_grade}")

    # Determine fitting rating based on schedule
    if schedule in ("5S", "10S"):
        fitting_class = "Sch 10S"
    elif schedule in ("40", "40S", "STD"):
        fitting_class = "Sch 40 / STD"
    elif schedule in ("80", "80S", "XS"):
        fitting_class = "Sch 80 / XS"
    elif schedule in ("160",):
        fitting_class = "Sch 160"
    else:
        fitting_class = f"Sch {schedule}"

    # Small bore vs large bore
    try:
        size_num = float(pipe_size_nps)
        is_small_bore = size_num <= 2.0
    except ValueError:
        is_small_bore = False

    # Connection type
    if is_small_bore:
        connection = "Socket Weld (SW)" if material_type != "SS" else "Socket Weld (SW) / Butt Weld (BW)"
        small_bore_fittings = {
            "coupling": f"A105 (CS)" if material_type in ("CS", "CS-LT") else f"A182 ({material_type})",
            "half_coupling": f"A105 (CS)" if material_type in ("CS", "CS-LT") else f"A182 ({material_type})",
        }
    else:
        connection = "Butt Weld (BW)"
        small_bore_fittings = {}

    result = {
        "pipe": {
            "material": material_grade,
            "schedule": schedule,
            "connection": connection,
            "size": f"NPS {pipe_size_nps}",
        },
        "elbow_90": {
            "type": "90 deg LR Elbow",
            "material": fittings["elbow"],
            "schedule": fitting_class,
            "standard": "ASME B16.9",
        },
        "elbow_45": {
            "type": "45 deg Elbow",
            "material": fittings["elbow"],
            "schedule": fitting_class,
            "standard": "ASME B16.9",
        },
        "tee_equal": {
            "type": "Equal Tee",
            "material": fittings["tee"],
            "schedule": fitting_class,
            "standard": "ASME B16.9",
        },
        "tee_reducing": {
            "type": "Reducing Tee",
            "material": fittings["tee"],
            "schedule": fitting_class,
            "standard": "ASME B16.9",
        },
        "reducer_concentric": {
            "type": "Concentric Reducer",
            "material": fittings["reducer"],
            "schedule": fitting_class,
            "standard": "ASME B16.9",
        },
        "reducer_eccentric": {
            "type": "Eccentric Reducer",
            "material": fittings["reducer"],
            "schedule": fitting_class,
            "standard": "ASME B16.9",
        },
        "cap": {
            "type": "Pipe Cap",
            "material": fittings["cap"],
            "schedule": fitting_class,
            "standard": "ASME B16.9",
        },
        "branch_connections": {
            "equal": BRANCH_CONNECTIONS["equal"],
            "1_size_down": BRANCH_CONNECTIONS["1_size"],
            "2_size_down": BRANCH_CONNECTIONS["2_size"],
            "3_plus_down": BRANCH_CONNECTIONS["3_plus"],
        },
        "small_bore_fittings": small_bore_fittings,
        "is_small_bore": is_small_bore,
        "material_type": material_type,
        "branch_reinforcement": {},  # populated below
    }

    # Calculate branch reinforcement for a common branch scenario
    # (header = main pipe, branch = 2 sizes smaller or half)
    try:
        header_data = PIPE_DIMENSIONS_B36_10.get(str(pipe_size_nps))
        if header_data and not is_small_bore:
            header_wt_val = header_data[1].get(schedule, header_data[1].get("40", 0))
            # Use a representative branch size (half the header NPS, minimum NPS 2)
            header_nps_num = float(pipe_size_nps)
            branch_nps_val = str(max(2, int(header_nps_num / 2)))
            # Rough estimate of min required thickness (placeholder, real value from thickness calc)
            # Use 60% of actual as typical approximation
            min_wt_est = header_wt_val * 0.6
            reinf = calculate_branch_reinforcement(
                header_nps=pipe_size_nps,
                branch_nps=branch_nps_val,
                header_wt=header_wt_val,
                header_min_wt=min_wt_est,
            )
            result["branch_reinforcement"] = reinf
    except Exception:
        pass

    # Print summary
    print(f"\n" + "=" * 65)
    print(f"  PIPE & FITTINGS MATERIAL ASSIGNMENT")
    print("=" * 65)
    print(f"\n  Pipe: {material_grade}, NPS {pipe_size_nps}, {fitting_class}")
    print(f"  Connection: {connection}")
    print(f"\n  {'Component':<25} {'Material':<18} {'Standard'}")
    print(f"  {'-'*25} {'-'*18} {'-'*15}")
    print(f"  {'Pipe':<25} {material_grade:<18} {'ASTM'}")
    print(f"  {'90 LR Elbow':<25} {fittings['elbow']:<18} {'ASME B16.9'}")
    print(f"  {'45 Elbow':<25} {fittings['elbow']:<18} {'ASME B16.9'}")
    print(f"  {'Equal Tee':<25} {fittings['tee']:<18} {'ASME B16.9'}")
    print(f"  {'Reducing Tee':<25} {fittings['tee']:<18} {'ASME B16.9'}")
    print(f"  {'Concentric Reducer':<25} {fittings['reducer']:<18} {'ASME B16.9'}")
    print(f"  {'Eccentric Reducer':<25} {fittings['reducer']:<18} {'ASME B16.9'}")
    print(f"  {'Cap':<25} {fittings['cap']:<18} {'ASME B16.9'}")

    if is_small_bore:
        print(f"\n  Small Bore Fittings (SW):")
        for name, mat in small_bore_fittings.items():
            print(f"    {name:<20} {mat}")

    print(f"\n  Branch Connection Guide:")
    for key, val in result["branch_connections"].items():
        print(f"    {key:<15} -> {val}")

    print("  " + "-" * 55)

    return result


def calculate_branch_reinforcement(header_nps, branch_nps, header_wt, header_min_wt,
                                    branch_wt=None, branch_min_wt=None):
    """
    Calculate branch reinforcement per ASME B31.3 para 304.3 (Area Replacement Method).

    The opening in the header pipe for a branch connection must be reinforced such that
    the available reinforcement area >= required reinforcement area.

    Args:
        header_nps: Header pipe NPS (string, e.g., "6")
        branch_nps: Branch pipe NPS (string, e.g., "2")
        header_wt: Header actual wall thickness (inches)
        header_min_wt: Header minimum required thickness (inches)
        branch_wt: Branch actual wall thickness (inches), auto-looked up if None
        branch_min_wt: Branch minimum required thickness (inches), defaults to header_min_wt ratio

    Returns:
        dict with reinforcement calculation results:
        - adequate (bool): True if reinforcement is adequate
        - A_required (float): Required reinforcement area (sq.in.)
        - A_available (float): Available reinforcement area (sq.in.)
        - deficit (float): Deficit area if inadequate (sq.in.), 0 if adequate
        - pad_required (bool): True if reinforcement pad needed
        - note (str): Summary note
    """
    # Look up header and branch OD from pipe dimensions
    header_data = PIPE_DIMENSIONS_B36_10.get(str(header_nps))
    branch_data = PIPE_DIMENSIONS_B36_10.get(str(branch_nps))

    if not header_data or not branch_data:
        return {
            "adequate": True,
            "A_required": 0,
            "A_available": 0,
            "deficit": 0,
            "pad_required": False,
            "note": f"Cannot calculate: pipe size data not found for NPS {header_nps} or {branch_nps}."
        }

    header_od = header_data[0]
    branch_od = branch_data[0]

    # d1 = effective length removed from header (branch opening)
    # For 90-degree branch: d1 = branch internal diameter
    d1 = branch_od - 2 * (branch_wt if branch_wt else header_wt)

    # t_h = minimum required header thickness
    t_h = header_min_wt
    T_h = header_wt  # actual header thickness

    # If branch_wt not provided, try to look up Sch 40 for the branch size
    if branch_wt is None:
        branch_scheds = branch_data[1]
        branch_wt = branch_scheds.get("40", branch_scheds.get("40S", list(branch_scheds.values())[0]))

    # If branch_min_wt not provided, estimate proportionally
    if branch_min_wt is None:
        # Approximate: same ratio of min/actual as header
        ratio = header_min_wt / header_wt if header_wt > 0 else 0.5
        branch_min_wt = branch_wt * ratio

    t_b = branch_min_wt  # min required branch thickness
    T_b = branch_wt  # actual branch thickness

    # L4 = height of reinforcement zone on branch
    # Per B31.3: L4 = min(2.5 * T_h, 2.5 * T_b + tr) where tr is pad thickness (assume 0 initially)
    L4 = min(2.5 * T_h, 2.5 * T_b)

    # A_required = t_h * d1 (area removed that needs replacement)
    A_required = t_h * d1

    # A1 = excess in header = (2 * d1) * (T_h - t_h)
    # Only the area within the reinforcement zone of header (d1 each side)
    A1 = 2 * d1 * (T_h - t_h)

    # A2 = excess in branch = 2 * L4 * (T_b - t_b)
    A2 = 2 * L4 * (T_b - t_b)

    # A_available = A1 + A2
    A_available = A1 + A2

    deficit = max(0, A_required - A_available)
    adequate = A_available >= A_required
    pad_required = not adequate

    if adequate:
        note = (f"Branch reinforcement adequate. A_avail={A_available:.4f} sq.in. >= "
                f"A_req={A_required:.4f} sq.in. (excess from header + branch).")
    else:
        note = (f"Reinforcement pad required per B31.3 304.3. "
                f"A_avail={A_available:.4f} sq.in. < A_req={A_required:.4f} sq.in. "
                f"Deficit={deficit:.4f} sq.in.")

    return {
        "adequate": adequate,
        "A_required": round(A_required, 4),
        "A_available": round(A_available, 4),
        "deficit": round(deficit, 4),
        "pad_required": pad_required,
        "header_nps": header_nps,
        "branch_nps": branch_nps,
        "d1": round(d1, 4),
        "note": note,
    }
