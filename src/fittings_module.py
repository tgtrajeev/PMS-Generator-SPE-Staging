"""
Module 6: Pipe & Fittings Material Assignment
Per ASME B16.9 (BW), ASME B16.11 (SW/THD Forged), MSS SP-97 (Olet),
MSS SP-95 (Swage), BS 3799 (Union), ASME B31.3.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import FITTING_MATERIALS, PIPE_DIMENSIONS_B36_10


# ── Forged fitting material mapping (ASME B16.11) ────────────
FORGED_MATERIAL = {
    "A106 Gr.B":   "ASTM A105",
    "A53 Gr.B":    "ASTM A105",
    "A333 Gr.6":   "ASTM A350 LF2",
    "A312 TP304":  "ASTM A182 F304",
    "A312 TP316":  "ASTM A182 F316",
    "A335 P11":    "ASTM A182 F11",
    "A335 P22":    "ASTM A182 F22",
}

# ── Weldolet / Olet material mapping (MSS SP-97) ────────────
WELDOLET_MATERIAL = {
    "A106 Gr.B":   "ASTM A105",
    "A53 Gr.B":    "ASTM A105",
    "A333 Gr.6":   "ASTM A350 LF2",
    "A312 TP304":  "ASTM A182 F304",
    "A312 TP316":  "ASTM A182 F316",
    "A335 P11":    "ASTM A182 F11",
    "A335 P22":    "ASTM A182 F22",
}

# ── BW fitting material mapping (ASME B16.9) ─────────────────
BW_MATERIAL = {
    "A106 Gr.B":   "ASTM A 234 Gr. WPB",
    "A53 Gr.B":    "ASTM A 234 Gr. WPB",
    "A333 Gr.6":   "ASTM A 420 Gr. WPL6",
    "A312 TP304":  "ASTM A 403 WP304",
    "A312 TP316":  "ASTM A 403 WP316",
    "A335 P11":    "ASTM A 234 WP11",
    "A335 P22":    "ASTM A 234 WP22",
}


def _is_galv(pms_mat):
    """Check if material is CS Galvanized."""
    return pms_mat.upper().replace(" ", "_").replace("-", "_") in ("CS_GALV", "CS_GALVANIZED")


def assign_fittings(material_grade, pipe_size_nps, schedule, material_type,
                    pms_material_type=None, service="", is_nace=False, is_low_temp=False,
                    flange_class=150):
    """
    Assign material specifications for pipe fittings per:
    - ASME B16.9 (BW fittings, NPS > 2")
    - ASME B16.11 (Forged SW/THD fittings, NPS ≤ 2")
    - MSS SP-97 (Olet / branch outlets)
    - MSS SP-95 (Swage nipples)
    - BS 3799 (Unions, large bore)
    - ASME B31.3 (design rules)

    Returns:
        dict with fitting assignments for PMS sheet format
    """
    pms_mat = pms_material_type or material_type or "CS"
    is_galv = _is_galv(pms_mat)

    # ── Size classification ───────────────────────────────────
    try:
        size_num = float(pipe_size_nps)
        is_small_bore = size_num <= 1.5
    except ValueError:
        size_num = 0
        is_small_bore = False

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

    # ── Base materials ────────────────────────────────────────
    forged_mat = FORGED_MATERIAL.get(material_grade, "ASTM A105")
    bw_mat = BW_MATERIAL.get(material_grade, "ASTM A 234 Gr. WPB")
    olet_mat = WELDOLET_MATERIAL.get(material_grade, "ASTM A105")

    # ── Galvanized suffix ─────────────────────────────────────
    galv_suffix = ""
    if is_galv:
        galv_suffix = ", Galvanized"
        # CS GALV uses Normalized forged material
        if forged_mat == "ASTM A105":
            forged_mat = "ASTM A 105N"

    # ── Template: CS GALV uses SW/SCRD small bore; all others use all-BW ──
    use_sw_small_bore = is_galv

    # Normalize olet material to "N" (Normalized) for CS
    olet_mat_n = olet_mat
    if "A105" in olet_mat.replace(" ", "") or "A 105" in olet_mat:
        olet_mat_n = "ASTM A 105N"

    if use_sw_small_bore and is_small_bore:
        # ── Template B: CS GALV small bore → SW/SCRD, ASME B16.11 ──
        if is_galv:
            fitting_type = "Screwed (SCRD), #3000"
            connection = "Screwed (SCRD)"
        else:
            fitting_type = "Socket Weld (SW), #3000"
            connection = "Socket Weld (SW)"
        fitting_standard = "ASME B16.11"
        moc = forged_mat + galv_suffix if galv_suffix else forged_mat
        comp_std = "ASME B16.11"

        # Components
        elbow   = {"standard": comp_std, "material": moc}
        tee     = {"standard": comp_std, "material": moc}
        reducer = {"standard": comp_std, "material": moc}
        cap     = {"standard": comp_std, "material": moc}
        coupling = {"standard": comp_std, "material": forged_mat + galv_suffix}
        hex_head_plug = {
            "standard": comp_std,
            "material": forged_mat + galv_suffix,
            "description": f"Hex Head Plug, {comp_std}",
        }
        union = {"standard": comp_std, "material": forged_mat + galv_suffix}
        olet  = {"standard": "MSS SP 97", "material": olet_mat + galv_suffix}
        swage = {
            "standard": "MSS SP 95",
            "material": f"MOC Same as pipe{galv_suffix}",
            "description": f"MSS SP 95, MOC Same as pipe{galv_suffix}",
        }

    else:
        # ── Template A: Process (all sizes BW) or GALV large bore ──
        fitting_type = "Butt Weld (SCH to match pipe), Seamless"
        fitting_standard = "ASME B16.9"
        moc = bw_mat + (", Seamless" + galv_suffix if galv_suffix else ", Seamless")
        connection = "Butt Weld (BW)"
        comp_std = "ASME B16.9"

        # Components — all BW
        elbow   = {"standard": comp_std, "material": moc}
        tee     = {"standard": comp_std, "material": moc}
        reducer = {"standard": comp_std, "material": moc}
        cap     = {"standard": comp_std, "material": moc}
        coupling = None  # No coupling for BW

        # Plug: Hex Head ASME B16.11 (small bore only, even in BW template)
        if is_small_bore:
            hex_head_plug = {
                "standard": "ASME B16.11",
                "material": forged_mat + galv_suffix,
                "description": f"Hex Head, ASME B16.11",
            }
        else:
            hex_head_plug = None

        # Union: BS 3799 for large bore (none for small bore in BW template)
        if is_small_bore:
            union = None
        else:
            union = {"standard": "BS 3799", "material": bw_mat + galv_suffix}

        # Olet: MSS SP 97
        olet = {
            "standard": "MSS SP 97",
            "material": olet_mat_n + galv_suffix,
            "description": f"MSS SP 97, {olet_mat_n}{galv_suffix}",
        }

        # Swage: not applicable for process BW template
        if is_galv:
            swage = {
                "standard": "MSS SP 95",
                "material": f"MOC Same as pipe{galv_suffix}",
                "description": f"MSS SP 95, MOC Same as pipe{galv_suffix}",
            }
        else:
            swage = None

    # ── Pipe data ─────────────────────────────────────────────
    pipe = {
        "material": material_grade,
        "schedule": schedule,
        "connection": connection,
        "size": f"NPS {pipe_size_nps}",
    }

    # ── Build result ──────────────────────────────────────────
    result = {
        "fitting_type": fitting_type,
        "fitting_standard": fitting_standard,
        "moc": moc,
        "connection": connection,
        "pipe": pipe,
        "elbow": elbow,
        "tee": tee,
        "reducer": reducer,
        "cap": cap,
        "coupling": coupling,
        "hex_head_plug": hex_head_plug,
        "union": union,
        "olet": olet,
        "swage": swage,
        "is_small_bore": is_small_bore,
        "material_type": material_type,
        "pms_material_type": pms_mat,
        "is_galvanized": is_galv,
        "use_sw_small_bore": use_sw_small_bore,
        # Keep legacy keys for backward compatibility
        "elbow_90": {"type": "90° LR Elbow", "material": elbow["material"],
                     "schedule": fitting_class, "standard": comp_std},
        "elbow_45": {"type": "45° Elbow", "material": elbow["material"],
                     "schedule": fitting_class, "standard": comp_std},
        "tee_equal": {"type": "Equal Tee", "material": tee["material"],
                      "schedule": fitting_class, "standard": comp_std},
        "tee_reducing": {"type": "Reducing Tee", "material": tee["material"],
                         "schedule": fitting_class, "standard": comp_std},
        "reducer_concentric": {"type": "Concentric Reducer", "material": reducer["material"],
                               "schedule": fitting_class, "standard": comp_std},
        "reducer_eccentric": {"type": "Eccentric Reducer", "material": reducer["material"],
                              "schedule": fitting_class, "standard": comp_std},
        "cap_legacy": {"type": "Pipe Cap", "material": cap["material"],
                       "schedule": fitting_class, "standard": comp_std},
        "plug": hex_head_plug if is_small_bore else {"type": "N/A", "material": "N/A", "standard": "N/A"},
        "weldolet": olet,
        "small_bore_fittings": {
            "coupling": {"material": (forged_mat + galv_suffix).strip(", "), "standard": "ASME B16.11", "rating": "#3000"},
            "half_coupling": {"material": (forged_mat + galv_suffix).strip(", "), "standard": "ASME B16.11", "rating": "#3000"},
            "plug": hex_head_plug,
        } if (is_small_bore and use_sw_small_bore) else {},
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
    bore = "Small Bore" if is_small_bore else "Large Bore"
    print(f"\n{'=' * 65}")
    print(f"  FITTINGS DATA — {bore}")
    print(f"  TYPE: {fitting_type}")
    print(f"  MOC:  {moc}")
    print(f"{'=' * 65}")
    for label, comp in [("Elbow", elbow), ("Tee", tee), ("Red.", reducer),
                        ("Cap", cap), ("Olet", olet), ("Swage", swage)]:
        if comp:
            print(f"  {label:<15} {comp.get('standard','')}")
    if coupling:
        print(f"  {'Coupl':<15} {coupling['standard']}")
    if hex_head_plug:
        print(f"  {'Hex Hd.Plug':<15} {hex_head_plug['description']}")
    if union:
        print(f"  {'Union':<15} {union['standard']}")
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
