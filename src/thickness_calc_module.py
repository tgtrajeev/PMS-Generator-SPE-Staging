"""
Module 4: Pipe Thickness Calculation (ASME B31.3)
Calculates minimum required wall thickness per ASME B31.3 formula.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.reference_data import ALLOWABLE_STRESS, JOINT_EFFICIENCY


def interpolate_stress(material_grade, design_temp_f):
    """
    Interpolate allowable stress at design temperature.
    Uses linear interpolation between known temperature points.
    """
    stress_data = ALLOWABLE_STRESS.get(material_grade)
    if not stress_data:
        raise ValueError(f"Unknown material grade: {material_grade}")

    # Extract temperature-stress pairs (exclude non-numeric keys)
    temp_stress = {k: v for k, v in stress_data.items() if isinstance(k, (int, float))}
    temps = sorted(temp_stress.keys())

    # Convert design temp from F to C for lookup
    design_temp_c = (design_temp_f - 32) * 5 / 9

    if design_temp_c <= temps[0]:
        return temp_stress[temps[0]]
    if design_temp_c >= temps[-1]:
        return temp_stress[temps[-1]]

    # Linear interpolation
    for i in range(len(temps) - 1):
        if temps[i] <= design_temp_c <= temps[i + 1]:
            t1, t2 = temps[i], temps[i + 1]
            s1, s2 = temp_stress[t1], temp_stress[t2]
            fraction = (design_temp_c - t1) / (t2 - t1)
            return round(s1 + fraction * (s2 - s1), 0)

    return temp_stress[temps[-1]]


def calculate_thickness(design_pressure_psig, pipe_od_in, material_grade,
                        design_temp_f, corrosion_allowance_in,
                        joint_type="seamless", y_factor=0.4):
    """
    Calculate minimum required wall thickness per ASME B31.3.

    Formula: t = (P * D) / (2 * (S * E + P * Y)) + c

    Where:
        P = Design pressure (psig)
        D = Outside diameter (inches)
        S = Allowable stress at design temperature (psi)
        E = Joint efficiency factor
        Y = Coefficient (0.4 for ferrous materials below 900F)
        c = Corrosion allowance (inches)

    Returns:
        dict with calculation results
    """
    P = design_pressure_psig
    D = pipe_od_in
    S = interpolate_stress(material_grade, design_temp_f)
    E = JOINT_EFFICIENCY.get(joint_type, 1.0)
    Y = y_factor
    c = corrosion_allowance_in

    # Schedule Number (informational per ASME)
    schedule_number = round(1000 * P / S) if S > 0 else 0

    # ASME B31.3 internal pressure formula
    t_calc = (P * D) / (2 * (S * E + P * Y))
    t_min = t_calc + c

    # Mill tolerance (12.5% typical for seamless pipe)
    mill_tolerance = 0.125
    t_nominal = t_min / (1 - mill_tolerance)

    result = {
        "design_pressure_psig": P,
        "pipe_od_in": D,
        "material_grade": material_grade,
        "design_temp_f": design_temp_f,
        "allowable_stress_psi": S,
        "joint_efficiency": E,
        "joint_type": joint_type,
        "y_factor": Y,
        "corrosion_allowance_in": c,
        "schedule_number": schedule_number,
        "t_calculated_in": round(t_calc, 4),
        "t_min_required_in": round(t_min, 4),
        "mill_tolerance_pct": mill_tolerance * 100,
        "t_nominal_min_in": round(t_nominal, 4),
        "t_nominal_min_mm": round(t_nominal * 25.4, 2),
    }

    print("\n" + "=" * 65)
    print("  PIPE THICKNESS CALCULATION (ASME B31.3)")
    print("=" * 65)
    print(f"\n  Formula: t = (P x D) / (2 x (S x E + P x Y)) + c")
    print(f"\n  Input Parameters:")
    print(f"    P (Design Pressure):    {P} psig")
    print(f"    D (Outside Diameter):   {D} in")
    print(f"    S (Allowable Stress):   {S} psi @ {design_temp_f} degF")
    print(f"    E (Joint Efficiency):   {E} ({joint_type})")
    print(f"    Y (Coefficient):        {Y}")
    print(f"    c (Corrosion Allow.):   {c} in ({round(c * 25.4, 2)} mm)")
    print(f"    Sch.No (1000xP/S):     {schedule_number}")
    print(f"\n  Calculation Results:")
    print(f"    t (calculated):         {result['t_calculated_in']:.4f} in")
    print(f"    t (with CA):            {result['t_min_required_in']:.4f} in")
    print(f"    t (with 12.5% mill tol):{result['t_nominal_min_in']:.4f} in ({result['t_nominal_min_mm']:.2f} mm)")
    print("  " + "-" * 55)

    return result
