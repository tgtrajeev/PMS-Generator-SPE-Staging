"""
Module 8: Valve Selection & VDS Code Generation
VDS Format: [Type 2-char][Bore/Design 1-char][Seat 1-char][Spec Code][End Conn 1-char]
Example: BLRTA1R = Ball + Reduced Bore + PTFE + A1 + Raised Face
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import (
    VALVE_MATERIALS, VALVE_END_CONNECTIONS,
    VDS_VALVE_TYPE_CODES, VDS_DESIGN_CODES, VDS_SEAT_CODES,
    VDS_END_CONN_CODES, VDS_SEAT_SELECTION, VALVE_SIZE_APPLICABILITY,
)


def _end_code(pressure_class, size_cat):
    """Get VDS end connection code."""
    return VDS_END_CONN_CODES.get((pressure_class, size_cat), "R")


def _seat_code(material_type, valve_type, is_nace=False):
    """Get seat material code. NACE forces Metal for ball/butterfly."""
    code = VDS_SEAT_SELECTION.get((material_type, valve_type), "M")
    # NACE/sour: override soft seats to Metal for integrity
    if is_nace and code in ("T", "P"):
        if valve_type in ("Ball", "Butterfly"):
            code = "M"
    return code


def generate_vds_code(valve_type, seat_code, spec_code, end_code, size_cat="large"):
    """
    Generate a single VDS code.
    Format: [Type 2][Bore/Design 1][Seat 1][Spec][End 1]
    """
    type_code = VDS_VALVE_TYPE_CODES.get(valve_type, valve_type[:2].upper())
    design_code = VDS_DESIGN_CODES.get((valve_type, size_cat), "Y")
    return f"{type_code}{design_code}{seat_code}{spec_code}{end_code}"


def recommend_vds_for_class(spec_code, material_type, pressure_class,
                            is_nace=False, pms_material_type=None):
    """
    Recommend all VDS codes for a piping class.

    Returns:
        dict with 'small_bore' and 'large_bore' lists of VDS entries.
        Each entry: {"valve_type": str, "vds_code": str, "description": str}
    """
    eff_mat = pms_material_type or material_type
    end_sb = _end_code(pressure_class, "small")
    end_lb = _end_code(pressure_class, "large")

    result = {"small_bore": [], "large_bore": [], "spec_code": spec_code,
              "pressure_class": pressure_class, "material_type": eff_mat}

    # ── Small bore (NPS ≤ 1.5") ──────────────────────────────
    for vtype in VALVE_SIZE_APPLICABILITY.get("small", []):
        seat = _seat_code(eff_mat, vtype, is_nace)
        vds = generate_vds_code(vtype, seat, spec_code, end_sb, "small")
        result["small_bore"].append({
            "valve_type": vtype,
            "vds_code": vds,
            "description": _describe_vds(vtype, "small", seat, end_sb),
        })

    # ── Large bore (NPS ≥ 2") ────────────────────────────────
    for vtype in VALVE_SIZE_APPLICABILITY.get("large", []):
        seat = _seat_code(eff_mat, vtype, is_nace)
        vds = generate_vds_code(vtype, seat, spec_code, end_lb, "large")
        result["large_bore"].append({
            "valve_type": vtype,
            "vds_code": vds,
            "description": _describe_vds(vtype, "large", seat, end_lb),
        })

        # Check valve alternatives for large bore
        if vtype == "Check":
            # Also recommend Dual Plate check for large bore
            dp_design = VDS_DESIGN_CODES.get(("Check_DP", "large"), "D")
            dp_type = VDS_VALVE_TYPE_CODES["Check"]
            dp_vds = f"{dp_type}{dp_design}{seat}{spec_code}{end_lb}"
            result["large_bore"].append({
                "valve_type": "Check (Dual Plate)",
                "vds_code": dp_vds,
                "description": f"Check Valve, Dual Plate, {'Metal' if seat == 'M' else 'PTFE'} Seat",
            })

    return result


def _describe_vds(valve_type, size_cat, seat_code, end_code):
    """Human-readable description for a VDS code."""
    seat_names = {"M": "Metal", "P": "PEEK", "T": "PTFE"}
    end_names = {"R": "RF", "J": "RTJ", "F": "Flat Face", "H": "Hub"}
    design_names = {
        ("Ball", "small"): "Reduced Bore",
        ("Ball", "large"): "Full Bore",
        ("Gate", "small"): "Screw & Yoke", ("Gate", "large"): "Screw & Yoke",
        ("Globe", "small"): "Screw & Yoke", ("Globe", "large"): "Screw & Yoke",
        ("Check", "small"): "Piston", ("Check", "large"): "Swing",
        ("Butterfly", "large"): "Wafer",
        ("Needle", "small"): "Inline",
        ("DBB", "small"): "Reduced Bore", ("DBB", "large"): "Full Bore",
    }
    design = design_names.get((valve_type, size_cat), "")
    seat = seat_names.get(seat_code, seat_code)
    end = end_names.get(end_code, end_code)
    parts = [f"{valve_type} Valve"]
    if design:
        parts.append(design)
    parts.append(f"{seat} Seat")
    parts.append(end)
    return ", ".join(parts)


def select_valves(material_type, flange_class, pipe_size_nps, spec_code, line_number=""):
    """
    Select valve types and generate VDS tags.
    """
    try:
        size_num = float(pipe_size_nps)
        size_cat = "small" if size_num <= 1.5 else "large"
    except ValueError:
        size_cat = "large"

    available_valves = VALVE_MATERIALS.get(material_type, {})
    end_conn_desc = VALVE_END_CONNECTIONS.get((flange_class, size_cat), "Flanged RF")
    end_code = _end_code(flange_class, size_cat)

    valves = {}

    print(f"\n{'=' * 65}")
    print(f"  VALVE SELECTION")
    print(f"{'=' * 65}")
    print(f"\n  Material Type: {material_type}")
    print(f"  Pressure Class: #{flange_class}")
    print(f"  Pipe Size: NPS {pipe_size_nps}")
    print(f"  End Connection: {end_conn_desc}")

    for vtype in VALVE_SIZE_APPLICABILITY.get(size_cat, []):
        if vtype in available_valves:
            v = available_valves[vtype]
            seat = _seat_code(material_type, vtype)
            vds_tag = generate_vds_code(vtype, seat, spec_code, end_code, size_cat)

            valves[vtype] = {
                "type": vtype,
                "body_material": v["body"],
                "trim": v["trim"],
                "seat": v["seat"],
                "pressure_class": flange_class,
                "end_connection": end_conn_desc,
                "size": f"NPS {pipe_size_nps}",
                "vds_tag": vds_tag,
            }
            print(f"  {vtype:<12} {vds_tag:<14} {v['body']:<16} {v['seat']}")

    print(f"  {'-' * 55}")

    return {
        "valves": valves,
        "end_connection": end_conn_desc,
        "pressure_class": flange_class,
        "material_type": material_type,
    }
