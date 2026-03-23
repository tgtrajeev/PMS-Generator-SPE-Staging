#!/usr/bin/env python3
"""
PMS Generator - Piping Material Specification Document Generator
================================================================
Follows the standard piping engineering workflow:

  START
    -> Material Selection Report (MSR)
    -> Specification Code Selection
    -> Process P&ID & Line List Inputs
    -> Pipe Thickness Calculation (ASME B31.3)
    -> Pipe Schedule Selection (ASME B36.10/B36.19)
    -> Pipe & Fittings Material Assignment
    -> Flanges, Gaskets & Bolting (ASME B16.5)
    -> Valve Selection
    -> Final PMS Sheet Generated

Usage:
    python main.py              # Interactive mode
    python main.py --demo       # Demo with sample data
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.msr_module import create_msr
from src.spec_code_module import select_spec_code, get_spec_description
from src.line_list_module import get_line_list_inputs
from src.thickness_calc_module import calculate_thickness
from src.schedule_selection_module import select_pipe_schedule
from src.fittings_module import assign_fittings
from src.flanges_module import select_flanges_gaskets_bolting
from src.valve_module import select_valves
from src.pms_generator import generate_pms
from data.reference_data import PIPE_DIMENSIONS_B36_10, PIPE_DIMENSIONS_B36_19


def print_banner():
    """Print application banner."""
    print("\n" + "=" * 65)
    print("  ╔═══════════════════════════════════════════════════════════╗")
    print("  ║     PMS GENERATOR - Piping Material Specification       ║")
    print("  ║              Document Generator v1.0                    ║")
    print("  ╚═══════════════════════════════════════════════════════════╝")
    print("=" * 65)
    print("  Generates code-compliant PMS documents following:")
    print("    - ASME B31.3  (Process Piping)")
    print("    - ASME B36.10 (Carbon Steel Pipe Dimensions)")
    print("    - ASME B36.19 (Stainless Steel Pipe Dimensions)")
    print("    - ASME B16.5  (Flange Ratings)")
    print("    - ASME B16.9  (Butt Weld Fittings)")
    print("    - ASME B16.20 (Gaskets)")
    print("=" * 65)


def get_pipe_od(pipe_size_nps, material_type):
    """Get pipe OD from reference data."""
    nps = str(pipe_size_nps)
    if material_type == "SS" and nps in PIPE_DIMENSIONS_B36_19:
        return PIPE_DIMENSIONS_B36_19[nps][0]
    elif nps in PIPE_DIMENSIONS_B36_10:
        return PIPE_DIMENSIONS_B36_10[nps][0]
    else:
        raise ValueError(f"Pipe size NPS {nps} not found in reference data")


def run_interactive():
    """Run the PMS generator in interactive mode."""
    print_banner()

    # Get project metadata
    print("\n  PROJECT INFORMATION")
    print("  " + "-" * 55)
    project_name = input("  Project Name: ").strip() or "Sample Project"
    doc_number = input("  Document Number: ").strip() or "PMS-001"
    revision = input("  Revision (0/A/B...): ").strip() or "0"

    metadata = {
        "project": project_name,
        "doc_number": doc_number,
        "revision": revision,
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    # Step 1: Material Selection Report
    print("\n\n  STEP 1 OF 8: MATERIAL SELECTION")
    msr = create_msr()

    # Step 2: Specification Code Selection
    print("\n\n  STEP 2 OF 8: SPECIFICATION CODE")
    spec = select_spec_code(msr["material_type"], msr["corrosion_allowance_mm"])
    desc = get_spec_description(spec["spec_code"])
    print(f"  Description: {desc}")

    # Step 3: Line List Inputs
    print("\n\n  STEP 3 OF 8: LINE LIST INPUTS")
    line_list = get_line_list_inputs()

    # Step 4: Pipe Thickness Calculation
    print("\n\n  STEP 4 OF 8: THICKNESS CALCULATION")
    pipe_od = get_pipe_od(line_list["pipe_size_nps"], msr["material_type"])

    # Select joint type
    print("\n  Joint Type:")
    print("    1. Seamless (E=1.0)")
    print("    2. ERW (E=0.85)")
    print("    3. SAW (E=0.85)")
    print("    4. DSAW (E=1.0)")
    jt_choice = input("  Select joint type (1-4) [default=1]: ").strip() or "1"
    joint_types = {"1": "seamless", "2": "ERW", "3": "SAW", "4": "DSAW"}
    joint_type = joint_types.get(jt_choice, "seamless")

    thickness = calculate_thickness(
        design_pressure_psig=line_list["design_pressure_psig"],
        pipe_od_in=pipe_od,
        material_grade=msr["material_grade"],
        design_temp_f=line_list["design_temp_f"],
        corrosion_allowance_in=msr["corrosion_allowance_in"],
        joint_type=joint_type,
    )

    # Step 5: Pipe Schedule Selection
    print("\n\n  STEP 5 OF 8: SCHEDULE SELECTION")
    schedule = select_pipe_schedule(
        pipe_size_nps=line_list["pipe_size_nps"],
        min_thickness_in=thickness["t_nominal_min_in"],
        material_type=msr["material_type"],
    )

    # Step 6: Fittings Material Assignment
    print("\n\n  STEP 6 OF 8: FITTINGS ASSIGNMENT")
    fittings = assign_fittings(
        material_grade=msr["material_grade"],
        pipe_size_nps=line_list["pipe_size_nps"],
        schedule=schedule["selected_schedule"],
        material_type=msr["material_type"],
    )

    # Step 7: Flanges, Gaskets & Bolting
    print("\n\n  STEP 7 OF 8: FLANGES, GASKETS & BOLTING")
    flanges = select_flanges_gaskets_bolting(
        material_grade=msr["material_grade"],
        material_type=msr["material_type"],
        design_pressure_psig=line_list["design_pressure_psig"],
        design_temp_f=line_list["design_temp_f"],
    )

    # Step 8: Valve Selection
    print("\n\n  STEP 8 OF 8: VALVE SELECTION")
    valves = select_valves(
        material_type=msr["material_type"],
        flange_class=flanges["flange"]["class"],
        pipe_size_nps=line_list["pipe_size_nps"],
        spec_code=spec["spec_code"],
        line_number=line_list["line_number"],
    )

    # Consolidate all data
    pms_data = {
        "metadata": metadata,
        "msr": msr,
        "spec_code": spec,
        "line_list": line_list,
        "thickness": thickness,
        "schedule": schedule,
        "fittings": fittings,
        "flanges": flanges,
        "valves": valves,
    }

    # Generate Final PMS
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    excel_path = generate_pms(pms_data, output_dir)

    if excel_path:
        print(f"\n  PMS document saved to: {excel_path}")
    print("\n  PMS Generation Complete!")
    print("=" * 65)

    return pms_data


def run_demo():
    """Run with sample data (non-interactive) for testing."""
    print_banner()
    print("\n  Running DEMO MODE with sample data...")

    metadata = {
        "project": "Demo Refinery Project",
        "doc_number": "PMS-DEMO-001",
        "revision": "0",
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    # Pre-set values
    msr = {
        "material_grade": "A106 Gr.B",
        "material_type": "CS",
        "material_spec": "ASTM A106",
        "corrosion_allowance_mm": 1.5,
        "corrosion_allowance_in": round(1.5 / 25.4, 4),
        "smts_psi": 60000,
        "smys_psi": 35000,
    }

    spec = select_spec_code("CS", 1.5)

    line_list = {
        "line_number": "6-P-1001-A1-1H",
        "fluid": "Process Water",
        "pipe_size_nps": "6",
        "design_pressure_psig": 150.0,
        "design_pressure_bar": 10.34,
        "test_pressure_psig": 225.0,
        "design_temp_f": 300.0,
        "design_temp_c": 148.9,
        "mdmt_f": -20.0,
        "mdmt_c": -28.9,
        "operating_pressure_psig": 120.0,
        "operating_temp_f": 240.0,
        "operating_temp_c": 115.6,
        "insulation": "Hot",
    }

    pipe_od = get_pipe_od("6", "CS")

    thickness = calculate_thickness(
        design_pressure_psig=150.0,
        pipe_od_in=pipe_od,
        material_grade="A106 Gr.B",
        design_temp_f=300.0,
        corrosion_allowance_in=msr["corrosion_allowance_in"],
        joint_type="seamless",
    )

    schedule = select_pipe_schedule(
        pipe_size_nps="6",
        min_thickness_in=thickness["t_nominal_min_in"],
        material_type="CS",
    )

    fittings = assign_fittings(
        material_grade="A106 Gr.B",
        pipe_size_nps="6",
        schedule=schedule["selected_schedule"],
        material_type="CS",
    )

    flanges = select_flanges_gaskets_bolting(
        material_grade="A106 Gr.B",
        material_type="CS",
        design_pressure_psig=150.0,
        design_temp_f=300.0,
    )

    valves = select_valves(
        material_type="CS",
        flange_class=flanges["flange"]["class"],
        pipe_size_nps="6",
        spec_code=spec["spec_code"],
        line_number="6-P-1001-A1-1H",
    )

    pms_data = {
        "metadata": metadata,
        "msr": msr,
        "spec_code": spec,
        "line_list": line_list,
        "thickness": thickness,
        "schedule": schedule,
        "fittings": fittings,
        "flanges": flanges,
        "valves": valves,
    }

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    excel_path = generate_pms(pms_data, output_dir)

    if excel_path:
        print(f"\n  PMS document saved to: {excel_path}")
    print("\n  DEMO Complete!")
    print("=" * 65)

    return pms_data


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        run_interactive()
