"""
Module 3: Process P&ID and Line List Inputs
Captures design conditions from the process data.
"""


def get_line_list_inputs():
    """
    Collect process design inputs from the user.

    Returns:
        dict with all line list parameters
    """
    print("\n" + "=" * 65)
    print("  PROCESS P&ID & LINE LIST INPUTS")
    print("=" * 65)

    inputs = {}

    # Line Number
    inputs["line_number"] = input("\n  Enter Line Number (e.g., 6-P-1001-A1-1H): ").strip() or "6-P-1001-A1-1H"

    # Fluid Service
    inputs["fluid"] = input("  Enter Fluid Service (e.g., Process Water, Steam, HC): ").strip() or "Process Water"

    # Pipe Size
    while True:
        try:
            size = input("  Enter Nominal Pipe Size NPS (e.g., 6): ").strip() or "6"
            inputs["pipe_size_nps"] = size
            break
        except ValueError:
            print("  Please enter a valid pipe size.")

    # Design Pressure
    while True:
        try:
            dp = float(input("  Enter Design Pressure (psig): ") or "150")
            inputs["design_pressure_psig"] = dp
            inputs["design_pressure_bar"] = round(dp * 0.0689476, 2)
            break
        except ValueError:
            print("  Please enter a valid number.")

    # Test Pressure
    while True:
        try:
            default_tp = round(dp * 1.5, 1)
            tp = float(input(f"  Enter Test Pressure (psig) [default={default_tp}]: ") or default_tp)
            inputs["test_pressure_psig"] = tp
            break
        except ValueError:
            print("  Please enter a valid number.")

    # Design Temperature
    while True:
        try:
            dt = float(input("  Enter Design Temperature (degF): ") or "300")
            inputs["design_temp_f"] = dt
            inputs["design_temp_c"] = round((dt - 32) * 5 / 9, 1)
            break
        except ValueError:
            print("  Please enter a valid number.")

    # Minimum Design Metal Temperature (MDMT)
    while True:
        try:
            mdmt = float(input("  Enter Min Design Metal Temp MDMT (degF) [default=-20]: ") or "-20")
            inputs["mdmt_f"] = mdmt
            inputs["mdmt_c"] = round((mdmt - 32) * 5 / 9, 1)
            break
        except ValueError:
            print("  Please enter a valid number.")

    # Operating Conditions
    while True:
        try:
            op = float(input("  Enter Operating Pressure (psig): ") or str(dp * 0.8))
            inputs["operating_pressure_psig"] = op
            break
        except ValueError:
            print("  Please enter a valid number.")

    while True:
        try:
            ot = float(input("  Enter Operating Temperature (degF): ") or str(dt * 0.8))
            inputs["operating_temp_f"] = ot
            inputs["operating_temp_c"] = round((ot - 32) * 5 / 9, 1)
            break
        except ValueError:
            print("  Please enter a valid number.")

    # Insulation
    inputs["insulation"] = input("  Insulation Type (None/Hot/Cold/Personnel Protection): ").strip() or "None"

    # Code & Inspection Requirements
    print("\n  --- Code & Inspection Requirements ---")
    inputs["design_code_edition"] = input("  Design Code Edition [ASME B31.3 - 2022]: ").strip() or "ASME B31.3 - 2022"
    inputs["pwht"] = input("  PWHT Required (No/Yes/Per Code) [Per Code]: ").strip() or "Per Code"
    inputs["nde"] = input("  NDE Requirement (Visual Only/10% RT/100% RT/10% UT/100% UT) [10% RT]: ").strip() or "10% RT"
    inputs["painting_coating"] = input("  Painting/Coating Specification []: ").strip() or ""
    inputs["hydrotest_medium"] = input("  Hydrotest Medium (Water/Pneumatic (Air)/Combined) [Water]: ").strip() or "Water"

    # Print summary
    print("\n  " + "-" * 55)
    print("  Line List Summary:")
    print(f"    Line Number:          {inputs['line_number']}")
    print(f"    Fluid:                {inputs['fluid']}")
    print(f"    Pipe Size:            NPS {inputs['pipe_size_nps']}")
    print(f"    Design Pressure:      {inputs['design_pressure_psig']} psig ({inputs['design_pressure_bar']} bar)")
    print(f"    Test Pressure:        {inputs['test_pressure_psig']} psig")
    print(f"    Design Temperature:   {inputs['design_temp_f']} degF ({inputs['design_temp_c']} degC)")
    print(f"    MDMT:                 {inputs['mdmt_f']} degF ({inputs['mdmt_c']} degC)")
    print(f"    Operating Pressure:   {inputs['operating_pressure_psig']} psig")
    print(f"    Operating Temperature:{inputs['operating_temp_f']} degF ({inputs['operating_temp_c']} degC)")
    print(f"    Insulation:           {inputs['insulation']}")
    print(f"    Design Code:          {inputs['design_code_edition']}")
    print(f"    PWHT:                 {inputs['pwht']}")
    print(f"    NDE:                  {inputs['nde']}")
    print(f"    Painting/Coating:     {inputs['painting_coating'] or 'N/A'}")
    print(f"    Hydrotest Medium:     {inputs['hydrotest_medium']}")
    print("  " + "-" * 55)

    return inputs
