"""
Module 6: Pipe & Fittings Material Assignment
Per ASME B16.9 (BW), ASME B16.11 (SW/THD Forged), MSS SP-97 (Weldolet), ASME B31.3.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import FITTING_MATERIALS, PIPE_DIMENSIONS_B36_10


# ── Forged fitting material mapping (ASME B16.11) ────────────
# Maps pipe material → forged fitting material for SW/THD fittings
FORGED_MATERIAL = {
    "A106 Gr.B":   "ASTM A105",
    "A53 Gr.B":    "ASTM A105",
    "A333 Gr.6":   "ASTM A350 LF2",
    "A312 TP304":  "ASTM A182 F304",
    "A312 TP316":  "ASTM A182 F316",
    "A335 P11":    "ASTM A182 F11",
    "A335 P22":    "ASTM A182 F22",
}

# ── Weldolet material mapping (MSS SP-97) ─────────────────────
WELDOLET_MATERIAL = {
    "A106 Gr.B":   "ASTM A105 (MSS SP-97)",
    "A53 Gr.B":    "ASTM A105 (MSS SP-97)",
    "A333 Gr.6":   "ASTM A350 LF2 (MSS SP-97)",
    "A312 TP304":  "ASTM A182 F304 (MSS SP-97)",
    "A312 TP316":  "ASTM A182 F316 (MSS SP-97)",
    "A335 P11":    "ASTM A182 F11 (MSS SP-97)",
    "A335 P22":    "ASTM A182 F22 (MSS SP-97)",
}


def assign_fittings(material_grade, pipe_size_nps, schedule, material_type,
                    pms_material_type=None, service="", is_nace=False, is_low_temp=False):
    """
    Assign material specifications for pipe fittings per:
    - ASME B16.9 (BW fittings, NPS > 2")
    - ASME B16.11 (Forged SW/THD fittings, NPS ≤ 2")
    - MSS SP-97 (Weldolet/branch outlets)
    - ASME B31.3 (design rules)

    Args:
        material_grade: e.g., "A106 Gr.B"
        pipe_size_nps: Nominal Pipe Size (string)
        schedule: Selected pipe schedule
        material_type: CS, CS-LT, SS, Alloy (base type)
        pms_material_type: Original material selection (e.g. "CS GALV", "CuNi")
        service: Service description string
        is_nace: NACE MR0175 compliance required
        is_low_temp: Low temperature service

    Returns:
        dict with fitting assignments
    """
    pms_mat = pms_material_type or material_type or "CS"

    # ── BW fitting materials (ASME B16.9) ─────────────────────
    fittings = FITTING_MATERIALS.get(material_grade)
    if not fittings:
        # Fallback to CS defaults
        fittings = {"elbow": "A234 WPB", "tee": "A234 WPB",
                     "reducer": "A234 WPB", "cap": "A234 WPB"}

    # ── Schedule / class label ────────────────────────────────
    if schedule in ("5S", "10S"):
        fitting_class = "Sch 10S"
    elif schedule in ("40", "40S", "Std"):
        fitting_class = "Sch 40 / STD"
    elif schedule in ("80", "80S", "XS"):
        fitting_class = "Sch 80 / XS"
    elif schedule in ("160",):
        fitting_class = "Sch 160"
    elif schedule in ("XXS",):
        fitting_class = "XXS"
    else:
        fitting_class = f"Sch {schedule}"

    # ── Size classification ───────────────────────────────────
    try:
        size_num = float(pipe_size_nps)
        is_small_bore = size_num <= 2.0
    except ValueError:
        size_num = 0
        is_small_bore = False

    # ── 4.1 TYPE: Forged (≤2") vs Wrought BW (>2") ───────────
    if is_small_bore:
        fitting_type = "Forged"
        fitting_standard = "ASME B16.11"
    else:
        fitting_type = "Seamless" if schedule in ("160", "XXS") else "Wrought Seamless"
        fitting_standard = "ASME B16.9"

    # ── 4.2 MOC ───────────────────────────────────────────────
    bw_mat = fittings.get("elbow", "A234 WPB")
    forged_mat = FORGED_MATERIAL.get(material_grade, "ASTM A105")
    weldolet_mat = WELDOLET_MATERIAL.get(material_grade, "ASTM A105 (MSS SP-97)")

    # ── 4.3 End Connection ────────────────────────────────────
    if is_small_bore:
        if material_type in ("CS", "CS-LT") or pms_mat.upper().replace(" ", "_") in ("CS_GALV",):
            connection = "Socket Weld (SW)"
        elif material_type == "SS":
            connection = "Socket Weld (SW) / Butt Weld (BW)"
        else:
            connection = "Socket Weld (SW)"
    else:
        connection = "Butt Weld (BW)"

    # ── Small bore forged fittings (ASME B16.11) ──────────────
    if is_small_bore:
        small_bore_fittings = {
            "coupling": {"material": forged_mat, "standard": "ASME B16.11", "rating": "3000# / 6000#"},
            "half_coupling": {"material": forged_mat, "standard": "ASME B16.11", "rating": "3000# / 6000#"},
            "plug": {"material": forged_mat, "standard": "ASME B16.11", "type": "Round Head / Hex Head"},
        }
    else:
        small_bore_fittings = {}

    # ── Build result ──────────────────────────────────────────
    result = {
        "fitting_type": fitting_type,
        "fitting_standard": fitting_standard,
        "moc": bw_mat if not is_small_bore else forged_mat,
        "pipe": {
            "material": material_grade,
            "schedule": schedule,
            "connection": connection,
            "size": f"NPS {pipe_size_nps}",
        },
        # 4.4 ELBOW — 90° LR default (ASME B16.9 / B16.11)
        "elbow_90": {
            "type": "90° Long Radius (LR) Elbow",
            "material": bw_mat if not is_small_bore else forged_mat,
            "schedule": fitting_class,
            "standard": fitting_standard,
        },
        "elbow_45": {
            "type": "45° Elbow",
            "material": bw_mat if not is_small_bore else forged_mat,
            "schedule": fitting_class,
            "standard": fitting_standard,
        },
        # 4.5 TEE — Equal and Reducing
        "tee_equal": {
            "type": "Equal Tee",
            "material": fittings["tee"] if not is_small_bore else forged_mat,
            "schedule": fitting_class,
            "standard": fitting_standard,
        },
        "tee_reducing": {
            "type": "Reducing Tee",
            "material": fittings["tee"] if not is_small_bore else forged_mat,
            "schedule": fitting_class,
            "standard": fitting_standard,
        },
        # 4.6 REDUCER — Concentric (vertical) / Eccentric (horizontal liquid)
        "reducer_concentric": {
            "type": "Concentric Reducer",
            "material": fittings["reducer"] if not is_small_bore else forged_mat,
            "schedule": fitting_class,
            "standard": fitting_standard,
            "note": "Use for vertical lines",
        },
        "reducer_eccentric": {
            "type": "Eccentric Reducer (Flat Bottom Up)",
            "material": fittings["reducer"] if not is_small_bore else forged_mat,
            "schedule": fitting_class,
            "standard": fitting_standard,
            "note": "Use for horizontal liquid lines (flat bottom)",
        },
        # 4.7 CAP — BW permanent closure
        "cap": {
            "type": "Pipe Cap (BW)",
            "material": fittings["cap"] if not is_small_bore else forged_mat,
            "schedule": fitting_class,
            "standard": fitting_standard,
        },
        # 4.8 PLUG — Only for ≤ 2" SW/THD
        "plug": {
            "type": "Plug (Round Head)" if is_small_bore else "N/A (use BW Cap)",
            "material": forged_mat if is_small_bore else "N/A",
            "standard": "ASME B16.11" if is_small_bore else "N/A",
        },
        # 4.5 WELDOLET — MSS SP-97 (for branch < 50% of header)
        "weldolet": {
            "type": "Weldolet",
            "material": weldolet_mat,
            "standard": "MSS SP-97",
            "note": "Use when branch < 50% of header size",
        },
        "small_bore_fittings": small_bore_fittings,
        "is_small_bore": is_small_bore,
        "material_type": material_type,
        "pms_material_type": pms_mat,
        "branch_reinforcement": {},
    }

    # ── Branch reinforcement calculation (ASME B31.3 304.3) ───
    try:
        header_data = PIPE_DIMENSIONS_B36_10.get(str(pipe_size_nps))
        if header_data and not is_small_bore:
            header_wt_val = header_data[1].get(schedule, header_data[1].get("40", 0))
            header_nps_num = float(pipe_size_nps)
            branch_nps_val = str(max(2, int(header_nps_num / 2)))
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

    # ── Console summary ───────────────────────────────────────
    print(f"\n{'=' * 65}")
    print(f"  PIPE & FITTINGS MATERIAL ASSIGNMENT")
    print(f"  Standard: {fitting_standard} | Type: {fitting_type}")
    print(f"  MOC: {result['moc']}")
    print(f"{'=' * 65}")
    print(f"\n  Pipe: {material_grade}, NPS {pipe_size_nps}, {fitting_class}")
    print(f"  Connection: {connection}")
    print(f"\n  {'Component':<25} {'Material':<25} {'Standard'}")
    print(f"  {'-'*25} {'-'*25} {'-'*15}")
    components = [
        ("90° LR Elbow", result["elbow_90"]),
        ("45° Elbow", result["elbow_45"]),
        ("Equal Tee", result["tee_equal"]),
        ("Reducing Tee", result["tee_reducing"]),
        ("Concentric Reducer", result["reducer_concentric"]),
        ("Eccentric Reducer", result["reducer_eccentric"]),
        ("Cap", result["cap"]),
        ("Weldolet", result["weldolet"]),
    ]
    if is_small_bore:
        components.append(("Plug", result["plug"]))
    for name, comp in components:
        mat = comp.get("material", "N/A")
        std = comp.get("standard", "")
        print(f"  {name:<25} {mat:<25} {std}")
    print(f"  {'-' * 65}")

    return result


def calculate_branch_reinforcement(header_nps, branch_nps, header_wt, header_min_wt,
                                    branch_wt=None, branch_min_wt=None):
    """
    Calculate branch reinforcement per ASME B31.3 para 304.3 (Area Replacement Method).
    """
    header_data = PIPE_DIMENSIONS_B36_10.get(str(header_nps))
    branch_data = PIPE_DIMENSIONS_B36_10.get(str(branch_nps))

    if not header_data or not branch_data:
        return {
            "adequate": True, "A_required": 0, "A_available": 0,
            "deficit": 0, "pad_required": False,
            "note": f"Cannot calculate: pipe data not found for NPS {header_nps} or {branch_nps}."
        }

    header_od = header_data[0]
    branch_od = branch_data[0]
    d1 = branch_od - 2 * (branch_wt if branch_wt else header_wt)
    t_h = header_min_wt
    T_h = header_wt

    if branch_wt is None:
        branch_scheds = branch_data[1]
        branch_wt = branch_scheds.get("40", branch_scheds.get("40S", list(branch_scheds.values())[0]))

    if branch_min_wt is None:
        ratio = header_min_wt / header_wt if header_wt > 0 else 0.5
        branch_min_wt = branch_wt * ratio

    t_b = branch_min_wt
    T_b = branch_wt
    L4 = min(2.5 * T_h, 2.5 * T_b)
    A_required = t_h * d1
    A1 = 2 * d1 * (T_h - t_h)
    A2 = 2 * L4 * (T_b - t_b)
    A_available = A1 + A2
    deficit = max(0, A_required - A_available)
    adequate = A_available >= A_required

    if adequate:
        note = (f"Branch reinforcement adequate. A_avail={A_available:.4f} sq.in. >= "
                f"A_req={A_required:.4f} sq.in.")
    else:
        note = (f"Reinforcement pad required per B31.3 304.3. "
                f"Deficit={deficit:.4f} sq.in.")

    return {
        "adequate": adequate,
        "A_required": round(A_required, 4),
        "A_available": round(A_available, 4),
        "deficit": round(deficit, 4),
        "pad_required": not adequate,
        "header_nps": header_nps,
        "branch_nps": branch_nps,
        "d1": round(d1, 4),
        "note": note,
    }
