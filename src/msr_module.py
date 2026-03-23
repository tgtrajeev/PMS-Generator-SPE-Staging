"""
Module 1: Material Selection Report (MSR)
Handles base material selection and corrosion allowance input.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import ALLOWABLE_STRESS, TYPICAL_CA


MATERIAL_OPTIONS = {
    1: ("A106 Gr.B",  "Carbon Steel Seamless Pipe (General Service)"),
    2: ("A53 Gr.B",   "Carbon Steel ERW/Seamless Pipe"),
    3: ("A333 Gr.6",  "Carbon Steel Low Temperature Service"),
    4: ("A312 TP304", "Stainless Steel 304 (18Cr-8Ni)"),
    5: ("A312 TP316", "Stainless Steel 316 (16Cr-12Ni-2Mo)"),
    6: ("A335 P11",   "Alloy Steel 1.25Cr-0.5Mo"),
    7: ("A335 P22",   "Alloy Steel 2.25Cr-1Mo"),
}


def get_material_type(material_grade):
    """Return the material type (CS, SS, Alloy, CS-LT) for a given grade."""
    return ALLOWABLE_STRESS.get(material_grade, {}).get("type", "CS")


def display_material_options():
    """Display available material options."""
    print("\n" + "=" * 65)
    print("  MATERIAL SELECTION REPORT (MSR)")
    print("=" * 65)
    print("\n  Available Pipe Materials:")
    print("  " + "-" * 60)
    for num, (grade, desc) in MATERIAL_OPTIONS.items():
        mat_type = get_material_type(grade)
        print(f"  {num}. {grade:<15} - {desc} [{mat_type}]")
    print("  " + "-" * 60)


def select_material():
    """Interactive material selection."""
    display_material_options()
    while True:
        try:
            choice = int(input("\n  Select material (1-7): "))
            if choice in MATERIAL_OPTIONS:
                grade, desc = MATERIAL_OPTIONS[choice]
                mat_type = get_material_type(grade)
                print(f"\n  Selected: {grade} - {desc}")
                return grade, mat_type
            print("  Invalid choice. Please select 1-7.")
        except ValueError:
            print("  Please enter a number.")


def select_corrosion_allowance(material_type):
    """Interactive corrosion allowance selection."""
    typical = TYPICAL_CA.get(material_type, TYPICAL_CA["CS"])
    print(f"\n  Typical Corrosion Allowances for {material_type}:")
    print(f"    Non-corrosive:    {typical['non_corrosive']} mm")
    print(f"    Mildly corrosive: {typical['mildly_corrosive']} mm")
    print(f"    Corrosive:        {typical['corrosive']} mm")

    while True:
        try:
            ca = float(input(f"\n  Enter Corrosion Allowance (mm) [default={typical['non_corrosive']}]: ") or typical['non_corrosive'])
            if 0 <= ca <= 12.0:
                print(f"  Corrosion Allowance set to: {ca} mm")
                return ca
            print("  CA must be between 0 and 12 mm.")
        except ValueError:
            print("  Please enter a valid number.")


def create_msr():
    """Create complete MSR data."""
    grade, mat_type = select_material()
    ca = select_corrosion_allowance(mat_type)
    props = ALLOWABLE_STRESS[grade]

    msr = {
        "material_grade": grade,
        "material_type": mat_type,
        "material_spec": props["spec"],
        "corrosion_allowance_mm": ca,
        "corrosion_allowance_in": round(ca / 25.4, 4),
        "smts_psi": props["smts"],
        "smys_psi": props["smys"],
    }

    print("\n  " + "-" * 50)
    print("  MSR Summary:")
    print(f"    Material:            {grade}")
    print(f"    Specification:       {props['spec']}")
    print(f"    Type:                {mat_type}")
    print(f"    SMTS:                {props['smts']} psi")
    print(f"    SMYS:                {props['smys']} psi")
    print(f"    Corrosion Allowance: {ca} mm ({msr['corrosion_allowance_in']:.4f} in)")
    print("  " + "-" * 50)

    return msr


if __name__ == "__main__":
    result = create_msr()
    print(f"\nMSR Data: {result}")
