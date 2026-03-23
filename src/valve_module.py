"""
Module 8: Valve Selection
Selects valve type, materials, pressure class, and end connections.
Generates Valve Data Sheet (VDS) tag information.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import VALVE_MATERIALS, VALVE_END_CONNECTIONS, VDS_VALVE_TYPE_CODES, VDS_DESIGN_CODES


VALVE_TYPES = {
    1: "Gate",
    2: "Globe",
    3: "Check",
    4: "Ball",
    5: "Butterfly",
    6: "Needle",
    7: "DBB",
}


def get_end_connection(flange_class, pipe_size_nps):
    """Determine valve end connection based on class and size."""
    try:
        size_num = float(pipe_size_nps)
        size_cat = "small" if size_num <= 2.0 else "large"
    except ValueError:
        size_cat = "large"

    return VALVE_END_CONNECTIONS.get((flange_class, size_cat), "Flanged RF")


def generate_vds_code(valve_type, seat_material, spec_code, end_connection):
    """
    Generate structured VDS code per project standard.
    Format: [Type 2-char][Bore/Design 1-char][Seat 1-char][Spec Code][End Conn 1-char]
    Example: GAYMA1R = Gate + Screw&Yoke + Metal + A1 + Raised Face
    """
    type_code = VDS_VALVE_TYPE_CODES.get(valve_type, valve_type[:2].upper())
    design_code = VDS_DESIGN_CODES.get(valve_type, "X")

    # Seat code: T=PTFE, P=PEEK, M=Metal
    seat_lower = seat_material.lower()
    if "ptfe" in seat_lower or "rptfe" in seat_lower or "epdm" in seat_lower:
        seat_code = "T"
    elif "peek" in seat_lower:
        seat_code = "P"
    else:
        seat_code = "M"

    # End connection code: R=RF, J=RTJ, F=Flat, H=Hub, T=NPT
    ec_lower = end_connection.lower()
    if "rtj" in ec_lower:
        end_code = "J"
    elif "rf" in ec_lower or "raised" in ec_lower:
        end_code = "R"
    elif "flat" in ec_lower:
        end_code = "F"
    elif "hub" in ec_lower:
        end_code = "H"
    elif "npt" in ec_lower or "screwed" in ec_lower or "socket" in ec_lower:
        end_code = "T"
    else:
        end_code = "R"

    return f"{type_code}{design_code}{seat_code}{spec_code}{end_code}"


def select_valves(material_type, flange_class, pipe_size_nps, spec_code, line_number=""):
    """
    Select valve types and generate VDS tags.

    Args:
        material_type: CS, CS-LT, SS, or Alloy
        flange_class: Pressure class (150, 300, etc.)
        pipe_size_nps: Nominal Pipe Size
        spec_code: Piping specification code
        line_number: Line number for tagging

    Returns:
        dict with valve selections
    """
    available_valves = VALVE_MATERIALS.get(material_type, {})
    end_conn = get_end_connection(flange_class, pipe_size_nps)

    valves = {}

    print(f"\n" + "=" * 65)
    print(f"  VALVE SELECTION")
    print("=" * 65)
    print(f"\n  Material Type: {material_type}")
    print(f"  Pressure Class: #{flange_class}")
    print(f"  Pipe Size: NPS {pipe_size_nps}")
    print(f"  End Connection: {end_conn}")

    print(f"\n  Available Valve Types:")
    print(f"  {'No.':<5} {'Type':<12} {'Body Material':<16} {'Trim':<18} {'Seat'}")
    print(f"  {'-'*5} {'-'*12} {'-'*16} {'-'*18} {'-'*15}")

    for num, vtype in VALVE_TYPES.items():
        if vtype in available_valves:
            v = available_valves[vtype]
            vds_tag = generate_vds_code(vtype, v["seat"], spec_code, end_conn)
            print(f"  {num:<5} {vtype:<12} {v['body']:<16} {v['trim']:<18} {v['seat']}")

            valves[vtype] = {
                "type": vtype,
                "body_material": v["body"],
                "trim": v["trim"],
                "seat": v["seat"],
                "pressure_class": flange_class,
                "end_connection": end_conn,
                "size": f"NPS {pipe_size_nps}",
                "vds_tag": vds_tag,
            }

    print(f"\n  Valve Data Sheet (VDS) Tags:")
    for vtype, vdata in valves.items():
        print(f"    {vdata['vds_tag']} - {vtype} Valve, {vdata['body_material']}, "
              f"#{flange_class}, {end_conn}")

    print("  " + "-" * 55)

    return {
        "valves": valves,
        "end_connection": end_conn,
        "pressure_class": flange_class,
        "material_type": material_type,
    }
