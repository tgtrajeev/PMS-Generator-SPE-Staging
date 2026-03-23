#!/usr/bin/env python3
"""
PMS Generator - Flask Web Application
Serves the Piping Material Specification generator on port 8080.
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, send_file, session
from src.msr_module import MATERIAL_OPTIONS, get_material_type
from src.spec_code_module import select_spec_code, get_spec_description
from src.thickness_calc_module import calculate_thickness, interpolate_stress
from src.schedule_selection_module import select_pipe_schedule
from src.fittings_module import assign_fittings
from src.flanges_module import select_flanges_gaskets_bolting
from src.valve_module import select_valves, VALVE_TYPES
from src.pms_generator import generate_pms_excel
from data.reference_data import (
    ALLOWABLE_STRESS, PIPE_DIMENSIONS_B36_10, PIPE_DIMENSIONS_B36_19,
    TYPICAL_CA, SPEC_CODE_MAP, JOINT_EFFICIENCY, FITTING_MATERIALS,
    FLANGE_MATERIALS, GASKET_MATERIALS, BOLTING_MATERIALS,
    VALVE_MATERIALS, VALVE_END_CONNECTIONS,
    FLANGE_RATINGS_CS, FLANGE_RATINGS_SS,
)

app = Flask(__name__)
app.secret_key = "pms-generator-secret-key-2024"


# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Main page with the multi-step wizard."""
    return render_template("index.html")


# ─── API ENDPOINTS ───────────────────────────────────────────────────────────

@app.route("/api/materials", methods=["GET"])
def api_materials():
    """Return list of available materials."""
    materials = []
    for num, (grade, desc) in MATERIAL_OPTIONS.items():
        mat_type = get_material_type(grade)
        props = ALLOWABLE_STRESS[grade]
        materials.append({
            "id": num,
            "grade": grade,
            "description": desc,
            "type": mat_type,
            "spec": props["spec"],
            "smts": props["smts"],
            "smys": props["smys"],
        })
    return jsonify(materials)


@app.route("/api/corrosion_allowance", methods=["GET"])
def api_corrosion_allowance():
    """Return typical CA values for a material type."""
    mat_type = request.args.get("material_type", "CS")
    ca_data = TYPICAL_CA.get(mat_type, TYPICAL_CA["CS"])
    return jsonify(ca_data)


@app.route("/api/spec_code", methods=["POST"])
def api_spec_code():
    """Calculate specification code."""
    data = request.json
    mat_type = data.get("material_type", "CS")
    ca = float(data.get("corrosion_allowance", 1.5))

    # Suppress print output
    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        result = select_spec_code(mat_type, ca)

    result["description"] = get_spec_description(result["spec_code"])
    return jsonify(result)


@app.route("/api/pipe_sizes", methods=["GET"])
def api_pipe_sizes():
    """Return available pipe sizes."""
    mat_type = request.args.get("material_type", "CS")
    if mat_type == "SS":
        sizes = list(PIPE_DIMENSIONS_B36_19.keys())
    else:
        sizes = list(PIPE_DIMENSIONS_B36_10.keys())
    return jsonify(sizes)


@app.route("/api/calculate_thickness", methods=["POST"])
def api_calculate_thickness():
    """Calculate pipe wall thickness per ASME B31.3."""
    data = request.json
    nps = str(data.get("pipe_size", "6"))
    mat_type = data.get("material_type", "CS")
    mat_grade = data.get("material_grade", "A106 Gr.B")

    # Get OD
    if mat_type == "SS" and nps in PIPE_DIMENSIONS_B36_19:
        od = PIPE_DIMENSIONS_B36_19[nps][0]
    else:
        od = PIPE_DIMENSIONS_B36_10[nps][0]

    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        result = calculate_thickness(
            design_pressure_psig=float(data.get("design_pressure", 150)),
            pipe_od_in=od,
            material_grade=mat_grade,
            design_temp_f=float(data.get("design_temp", 300)),
            corrosion_allowance_in=float(data.get("ca_inches", 0.0591)),
            joint_type=data.get("joint_type", "seamless"),
        )

    result["pipe_od_in"] = od
    return jsonify(result)


@app.route("/api/select_schedule", methods=["POST"])
def api_select_schedule():
    """Select pipe schedule."""
    data = request.json
    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        result = select_pipe_schedule(
            pipe_size_nps=str(data.get("pipe_size", "6")),
            min_thickness_in=float(data.get("min_thickness", 0.1)),
            material_type=data.get("material_type", "CS"),
        )
    return jsonify(result)


@app.route("/api/assign_fittings", methods=["POST"])
def api_assign_fittings():
    """Assign fittings materials."""
    data = request.json
    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        result = assign_fittings(
            material_grade=data.get("material_grade", "A106 Gr.B"),
            pipe_size_nps=str(data.get("pipe_size", "6")),
            schedule=data.get("schedule", "40"),
            material_type=data.get("material_type", "CS"),
        )
    return jsonify(result)


@app.route("/api/select_flanges", methods=["POST"])
def api_select_flanges():
    """Select flanges, gaskets, bolting."""
    data = request.json
    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        result = select_flanges_gaskets_bolting(
            material_grade=data.get("material_grade", "A106 Gr.B"),
            material_type=data.get("material_type", "CS"),
            design_pressure_psig=float(data.get("design_pressure", 150)),
            design_temp_f=float(data.get("design_temp", 300)),
        )
    return jsonify(result)


@app.route("/api/select_valves", methods=["POST"])
def api_select_valves():
    """Select valves."""
    data = request.json
    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        result = select_valves(
            material_type=data.get("material_type", "CS"),
            flange_class=int(data.get("flange_class", 150)),
            pipe_size_nps=str(data.get("pipe_size", "6")),
            spec_code=data.get("spec_code", "A1"),
            line_number=data.get("line_number", ""),
        )
    return jsonify(result)


@app.route("/api/generate_pms", methods=["POST"])
def api_generate_pms():
    """Generate complete PMS and return data + Excel file path."""
    data = request.json

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    import io
    from contextlib import redirect_stdout
    f = io.StringIO()
    with redirect_stdout(f):
        excel_path = generate_pms_excel(data, output_dir)

    filename = os.path.basename(excel_path) if excel_path else None
    return jsonify({"success": True, "filename": filename})


@app.route("/api/download/<filename>")
def download_file(filename):
    """Download generated Excel file."""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404


@app.route("/api/flange_ratings", methods=["GET"])
def api_flange_ratings():
    """Return flange P-T ratings for display."""
    mat_type = request.args.get("material_type", "CS")
    if mat_type == "SS":
        return jsonify({str(k): v for k, v in FLANGE_RATINGS_SS.items()})
    return jsonify({str(k): v for k, v in FLANGE_RATINGS_CS.items()})


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  PMS Generator - Web Interface")
    print("  Open http://localhost:8080 in your browser")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=8080, debug=True)
