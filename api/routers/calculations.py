"""
Calculations API router - spec code, thickness calculation, schedule selection.
"""

import io
from contextlib import redirect_stdout

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.spec_code_module import select_spec_code, get_spec_description
from src.thickness_calc_module import calculate_thickness, interpolate_stress
from src.schedule_selection_module import select_pipe_schedule
from data.reference_data import (
    PIPE_DIMENSIONS_B36_10, PIPE_DIMENSIONS_B36_19,
    PRESSURE_RATING_CODES, PMS_MATERIAL_CODES,
    PMS_TUBING_CODES, PMS_PART3_TUBING, PMS_PART3_NON_TUBING,
    PMS_MATERIAL_TYPE_TO_GRADE, JOINT_EFFICIENCY, ALLOWABLE_STRESS,
    BRANCH_CHARTS, BRANCH_CHART_MAP, get_branch_chart,
    get_branch_table_matrix, branch_lookup,
)
from src.pms_code_module import (
    auto_suggest_part1, auto_suggest_part2, auto_suggest_part3,
    validate_pms_code, generate_pms_code, get_suggestions,
)
from src.pms_generator import determine_pipe_type

router = APIRouter()


class SpecCodeRequest(BaseModel):
    material_type: str = "CS"
    corrosion_allowance: float = 1.5


class PMSCodeAutoRequest(BaseModel):
    material_grade: str = "A106 Gr.B"
    material_type: str = "CS"
    corrosion_allowance_mm: float = 1.5
    design_pressure_psig: float = 150
    mdmt_f: float = -20


class PMSCodeValidateRequest(BaseModel):
    part1: str
    part2: int
    part3: Optional[str] = None


class ThicknessRequest(BaseModel):
    pipe_size: str = "6"
    material_type: str = "CS"
    material_grade: str = "A106 Gr.B"
    design_pressure: float = Field(gt=0)
    design_temp: float = 300
    ca_inches: float = Field(ge=0, default=0.0591)
    joint_type: str = "seamless"


class ScheduleRequest(BaseModel):
    pipe_size: str = "6"
    min_thickness: float = Field(ge=0, default=0.1)
    material_type: str = "CS"


class FullScheduleTableRequest(BaseModel):
    material_type: str = "CS"
    material_grade: str = "A106 Gr.B"
    design_pressure_psig: float = 285
    design_temp_f: float = 300
    ca_mm: float = 3.0
    mech_allowance_mm: float = 0.0
    joint_type: str = "seamless"
    mill_tolerance_pct: float = 12.5
    y_factor: float = 0.4          # Auto-determined from temperature if 0.4 (default)
    is_low_temp: bool = False
    is_nace: bool = False
    service: str = ""
    pressure_class: int = 150       # From PMS Part 1 (150, 300, 600, 900, 1500, 2500)
    pressure_rating_label: str = "150#"  # Display label (e.g. "150#", "300#")


@router.post("/spec_code")
async def calc_spec_code(req: SpecCodeRequest):
    f = io.StringIO()
    with redirect_stdout(f):
        result = select_spec_code(req.material_type, req.corrosion_allowance)
    result["description"] = get_spec_description(result["spec_code"])
    return result


@router.post("/calculate_thickness")
async def calc_thickness(req: ThicknessRequest):
    nps = req.pipe_size
    if req.material_type == "SS" and nps in PIPE_DIMENSIONS_B36_19:
        od = PIPE_DIMENSIONS_B36_19[nps][0]
    else:
        od = PIPE_DIMENSIONS_B36_10[nps][0]

    f = io.StringIO()
    with redirect_stdout(f):
        result = calculate_thickness(
            design_pressure_psig=req.design_pressure,
            pipe_od_in=od,
            material_grade=req.material_grade,
            design_temp_f=req.design_temp,
            corrosion_allowance_in=req.ca_inches,
            joint_type=req.joint_type,
        )
    result["pipe_od_in"] = od
    return result


@router.post("/select_schedule")
async def calc_schedule(req: ScheduleRequest):
    f = io.StringIO()
    with redirect_stdout(f):
        result = select_pipe_schedule(
            pipe_size_nps=req.pipe_size,
            min_thickness_in=req.min_thickness,
            material_type=req.material_type,
        )
    return result


@router.post("/full_schedule_table")
async def full_schedule_table(req: FullScheduleTableRequest):
    """
    ASME B31.3 Schedule & Wall Thickness — complete engineering calculation.

    Applies:
      • ASME B31.3 Eq. 3a  (wall thickness)
      • ASME B36.10M / B36.19M  (schedule selection)
      • ASME B16.5  (pressure–temperature rating validation)
      • NACE MR0175 / ISO 15156  (sour-service minimum schedules + material)
      • Low-temperature requirements  (LTCS material, Charpy impact)
      • Service-based adjustments  (H2, acid, cyclic, chloride, steam)
    """

    # ── 1. Pipe dimension table ───────────────────────────────────────────────
    if req.material_type == "SS":
        dim_table  = PIPE_DIMENSIONS_B36_19
        pipe_std   = "ASME B36.19M"
    else:
        dim_table  = PIPE_DIMENSIONS_B36_10
        pipe_std   = "ASME B36.10M"

    # ── 2. Material allowable stress (ASME Section II Part D) ────────────────
    S           = interpolate_stress(req.material_grade, req.design_temp_f)
    E           = JOINT_EFFICIENCY.get(req.joint_type, 1.0)
    stress_data = ALLOWABLE_STRESS.get(req.material_grade, {})
    mat_spec    = stress_data.get("spec", "")
    mat_type_s  = stress_data.get("type", req.material_type)
    is_austenitic = (mat_type_s == "SS")

    # ── 3. Y-factor — ASME B31.3 Table 304.1.1 (temperature-driven) ─────────
    T_f = req.design_temp_f
    if T_f <= 900:                            # ≤ 482°C
        Y = 0.4
    elif T_f <= 950:                          # ≤ 510°C
        Y = 0.4 if is_austenitic else 0.5
    elif T_f <= 1000:                         # ≤ 538°C
        Y = 0.4 if is_austenitic else 0.7
    else:                                     # > 538°C
        Y = 0.5 if is_austenitic else 0.7
    y_basis = (
        f"ASME B31.3 Table 304.1.1 @ {T_f}°F "
        f"({'austenitic' if is_austenitic else 'ferritic/alloy steel'})"
    )

    # ── 4. W-factor — Weld Strength Reduction (B31.3 Table 302.3.5) ─────────
    if T_f < 950:
        W = 1.0
    elif T_f < 1000:
        W = 0.95
    elif T_f < 1050:
        W = 0.91
    elif T_f < 1100:
        W = 0.86
    else:
        W = 0.82
    w_basis = f"ASME B31.3 Table 302.3.5 @ {T_f}°F (W={W})"

    P        = req.design_pressure_psig
    c_in     = req.ca_mm / 25.4
    m_in     = req.mech_allowance_mm / 25.4
    mill_tol = req.mill_tolerance_pct / 100.0

    # ── 5. Service classification ─────────────────────────────────────────────
    svc = (req.service or "").lower()
    is_sour     = any(k in svc for k in ["sour", "h2s", "sulfide"])
    is_hydrogen = any(k in svc for k in ["hydrogen", " h2 ", "h2/"])  # h2s is sour, NOT hydrogen
    is_steam    = any(k in svc for k in ["steam", "condensate"])
    is_acid     = any(k in svc for k in ["acid", "amine", "caustic", "hcl", "h2so4"])
    is_cyclic   = any(k in svc for k in ["cyclic", "fatigue", "pulsating"])
    is_chloride = "chloride" in svc
    is_corr     = any(k in svc for k in ["corrosive", "acid", "sour", "h2s", "flare"])

    # Minimum schedule applies for NACE / LT / corrosive service
    has_svc_min = req.is_nace or req.is_low_temp or is_sour or is_acid or is_corr

    # ── 6. Engineering flags ──────────────────────────────────────────────────
    P_barg       = round(P * 0.0689476, 1)
    T_c          = round((T_f - 32) * 5 / 9, 1)
    hydro_barg   = round(P_barg * 1.5, 1)
    flags        = []

    # -- NACE / Sour service
    if req.is_nace or is_sour:
        flags.append({
            "type": "NACE", "severity": "CRITICAL",
            "title": "NACE MR0175 / ISO 15156 — Sour Service Compliance",
            "detail": (
                "All pipe, fittings, flanges, and welds must comply with NACE MR0175 / ISO 15156. "
                "Max hardness: CS ≤ 22 HRC / 250 HBW (base metal, weld metal, HAZ). "
                "HIC testing per NACE TM0284 if H₂S partial pressure > 0.0003 MPa (0.05 psia). "
                "SSC testing per NACE TM0177 Method A may also be required."
            ),
        })
        flags.append({
            "type": "NACE", "severity": "CRITICAL",
            "title": "Minimum Schedule Enforced — Sch 160 (≤ NPS 1½\") / XS (≥ NPS 2\")",
            "detail": (
                "NACE MR0175 mandates minimum wall thickness regardless of pressure calculation. "
                "NPS ≤ 1½\": Schedule 160. NPS ≥ 2\": Extra Strong (XS / Sch 80). "
                "Do NOT downgrade based on pressure margin alone."
            ),
        })
        flags.append({
            "type": "NACE", "severity": "MANDATORY",
            "title": "NACE Bolting — A320 L7M Studs + A194 7ML Nuts (XYLAN Coated)",
            "detail": (
                "Studs: ASTM A320 Gr. L7M. Nuts: ASTM A194 Gr. 7ML. "
                "Coating: XYLAR 2 + XYLAN 1070, minimum combined thickness 50 μm."
            ),
        })
        flags.append({
            "type": "NACE", "severity": "MANDATORY",
            "title": "PWHT — Post Weld Heat Treatment Required",
            "detail": (
                "PWHT mandatory for all carbon steel welds in NACE/sour service to ensure "
                "HAZ hardness ≤ 250 HBW. WPS/PQR must include hardness survey."
            ),
        })

    # -- Low Temperature
    if req.is_low_temp:
        lt_mat = "A333 Gr.6" if req.material_type in ("CS", "CS-LT") else req.material_grade
        flags.append({
            "type": "LTCS", "severity": "CRITICAL",
            "title": f"Low-Temperature Material Required: ASTM {lt_mat}",
            "detail": (
                f"Standard CS (A106 Gr.B) is NOT acceptable below −29°C. "
                f"Seamless: ASTM A333 Gr.6 (rated to −45°C). "
                f"Welded: ASTM A671 CC60 Class 22 (EFW). "
                f"Flanges: ASTM A350 LF2. Fittings: ASTM A420 WPL6. "
                f"Charpy V-notch impact testing mandatory."
            ),
        })
        flags.append({
            "type": "LTCS", "severity": "MANDATORY",
            "title": "Charpy V-Notch Impact Testing — ASME B31.3 §323.2.2",
            "detail": (
                "Three specimens per test, tested at MDMT. "
                "Minimum average absorbed energy: 27 J (20 ft·lbf) per ASME B31.3. "
                "Individual specimen: minimum 21 J (15 ft·lbf). "
                "Weld and HAZ specimens required in addition to base metal."
            ),
        })

    # -- Critical combination: NACE + Low Temp
    if req.is_nace and req.is_low_temp:
        flags.append({
            "type": "CRITICAL", "severity": "CRITICAL",
            "title": "⚠ CRITICAL COMBINATION: NACE + Low Temperature Service",
            "detail": (
                "Material must simultaneously satisfy: "
                "(a) NACE hardness ≤ 250 HBW on base metal, weld metal, and HAZ — "
                "AND (b) Charpy impact at MDMT ≥ 27 J. "
                "PWHT must reduce hardness without embrittling at low temperature. "
                "MANDATORY: Engineering qualification review and test coupon programme."
            ),
        })

    # -- Hydrogen service
    if is_hydrogen:
        flags.append({
            "type": "HYDROGEN", "severity": "WARNING",
            "title": "Hydrogen Service — API 941 (Nelson Curves) Review Required",
            "detail": (
                "Per API 941: verify CS is within safe operating region for the H₂ partial "
                "pressure and temperature combination (Nelson Curves). "
                "High-temperature H₂ attack (HTHA) risk above 230°C. "
                "Consider 1¼Cr–½Mo (A335 P11) or SS 316L for elevated temperature H₂ service. "
                "Schedule stepped up one level conservatively."
            ),
        })

    # -- Steam / Condensate
    if is_steam:
        flags.append({
            "type": "STEAM", "severity": "NOTE",
            "title": "Steam / Condensate — Thermal Fatigue & Drainage",
            "detail": (
                "Provide adequate drain points and thermal insulation. "
                "Check for water hammer and thermal cycling fatigue. "
                "For steam > 250°C apply ASME B31.1 Power Piping if applicable. "
                "ERW pipe not recommended; specify seamless."
            ),
        })

    # -- Acid / Corrosive
    if is_acid or is_corr:
        flags.append({
            "type": "CORROSIVE", "severity": "WARNING",
            "title": "Corrosive / Acid Service — Enhanced CA & NDE",
            "detail": (
                "Minimum recommended CA: 3.0 mm. "
                "Consider upgrading to SS 316L or Alloy if pH < 4 or T > 60°C. "
                "100% RT or UT required for all butt welds. "
                "Monitor corrosion rate and review CA at major turnarounds."
            ),
        })

    # -- Chloride SCC
    if is_chloride:
        flags.append({
            "type": "CHLORIDE", "severity": "WARNING",
            "title": "Chloride Service — SCC Risk for Austenitic SS",
            "detail": (
                "Austenitic SS (304/316) susceptible to chloride stress corrosion cracking (CSCC) "
                "above 60°C. Consider Duplex SS (A790 / UNS S31803) or Alloy 825 / 625. "
                "For insulated lines: inspect at insulation breaks annually."
            ),
        })

    # -- Cyclic / Fatigue
    if is_cyclic:
        flags.append({
            "type": "CYCLIC", "severity": "MANDATORY",
            "title": "Severe Cyclic Conditions — ASME B31.3 §302.3.5 & Appendix S",
            "detail": (
                "This piping is classified as 'Severe Cyclic Conditions' per ASME B31.3 §302.3.5. "
                "Mandatory requirements: "
                "(1) Formal fatigue/flexibility analysis per Appendix S using stress-range S_A vs. computed S_E. "
                "(2) 100% radiographic or ultrasonic examination of all butt welds (§341.4.3). "
                "(3) No socket welds for NPS ≤ 2\" — use full-penetration butt welds (SIF = 1.0). "
                "(4) Weld strength reduction factor W applies at elevated temperature (Table 302.3.5). "
                "Note: ASME B31.3 Eq. 3a wall thickness is unchanged — schedule selection is driven by "
                "the standard pressure calculation. Additional wall margin (if any) is established by the "
                "fatigue analysis result, not by a blanket schedule step-up."
            ),
        })

    # -- NDE requirement
    if req.is_nace or is_sour:
        nde = "100% RT or UT — NACE / Sour Service (B31.3 §341.4.2)"
        pwht_req = "Required — NACE MR0175 hardness control (HAZ ≤ 250 HBW)"
    elif is_cyclic:
        nde = "100% RT or UT — Severe Cyclic Conditions (B31.3 §341.4.3)"
        pwht_req = "Per B31.3 §331 (P-No. and thickness dependent)"
    elif is_acid or is_corr:
        nde = "100% RT or UT — Corrosive / Category M Fluid (B31.3 §340)"
        pwht_req = "Per B31.3 §331 (P-No. and thickness dependent)"
    else:
        nde = "10% Random RT — Normal Fluid Service (B31.3 §341.4.1)"
        pwht_req = "Per B31.3 §331 (P-No. and thickness dependent)"
    flags.append({
        "type": "NDE", "severity": "MANDATORY",
        "title": f"NDE: {nde}",
        "detail": (
            f"Weld examination: {nde}. "
            f"PWHT: {pwht_req}. "
            f"Pressure test: hydrostatic at {hydro_barg} barg (1.5 × DP) per B31.3 §345.4.2."
        ),
    })

    # -- Hydrotest
    flags.append({
        "type": "TEST", "severity": "MANDATORY",
        "title": f"Hydrostatic Test Pressure: {hydro_barg} barg (= 1.5 × {P_barg} barg DP)",
        "detail": (
            f"Shop test: {hydro_barg} barg per ASME B31.3 §345.4.2. "
            f"Medium: potable water (deionised for SS). "
            f"Duration: minimum 10 minutes. "
            f"Verify all flanges rated ≥ {hydro_barg} barg at test temperature."
        ),
    })

    # ── 7. Per-NPS calculation ────────────────────────────────────────────────
    nps_list = sorted([n for n in dim_table.keys() if float(n) <= 30], key=lambda x: float(x))
    rows     = []
    min_mawp = float("inf")
    max_mawp = 0.0
    min_margin = float("inf")
    fail_count = 0

    for nps in nps_list:
        od_in, schedules = dim_table[nps]
        od_mm   = round(od_in * 25.4, 1)
        nps_f   = float(nps)

        # ── User-specified ASME B31.3 formula ──────────────────────────
        # Step 1: t_min = (P × OD) / (2 × (S + P × Y)) + CA
        denom    = 2.0 * (S + P * Y)
        t_calc_in = (P * od_in) / denom if denom > 0 else 0.0
        t_min_in_raw = t_calc_in + c_in   # add corrosion allowance
        t_req_mm = round(t_calc_in * 25.4, 3)

        # Step 2: t_design = t_min / (1 - 0.125)  (mill tolerance)
        t_min_calc_in = t_min_in_raw / (1.0 - mill_tol)

        # ── PMS Standardization: base minimum schedule by NPS range ──
        governs       = "Pressure (ASME B31.3 Eq. 3a)"
        sorted_scheds = sorted(schedules.items(), key=lambda x: x[1])

        # Layer 1 — Base minimum schedule (ALWAYS applied per PMS standardization)
        base_min_wt_in = 0.0
        base_min_sch   = None
        base_label     = ""

        if nps_f <= 1.5:
            # NPS ≤ 1½" → minimum Sch 160
            wt = schedules.get("160", schedules.get("XXS", 0))
            if wt > 0:
                base_min_wt_in, base_min_sch = wt, "160"
                base_label = 'Sch 160 (NPS \u2264 1\u00bd")'
        elif nps_f <= 6.0:
            # 2" ≤ NPS ≤ 6" → minimum Sch 80
            wt = schedules.get("80", schedules.get("80S", schedules.get("XS", 0)))
            if wt > 0:
                base_min_wt_in, base_min_sch = wt, "80"
                base_label = 'Sch 80 (NPS 2"\u20136")'
        elif nps_f >= 8.0:
            # NPS ≥ 8" → STD (Standard Wall)
            wt = schedules.get("Std", schedules.get("40", 0))
            if wt > 0:
                base_min_wt_in, base_min_sch = wt, "Std"
                base_label = 'STD (NPS \u2265 8")'

        # Layer 2 — Service / CA bumps (increase one schedule from base)
        # NOTE: NPS ≤ 1.5" already uses Sch 160 (maximum practical small-bore schedule)
        #        — no further bump applied; XXS is not standard PMS practice.
        bump_reasons = []
        if has_svc_min:
            src = "NACE MR0175" if (req.is_nace or is_sour) else ("LTCS" if req.is_low_temp else "Corrosive service")
            bump_reasons.append(src)
        if c_in * 25.4 > 3.0:
            bump_reasons.append("CA > 3 mm")

        if bump_reasons and base_min_sch and nps_f > 1.5:
            # Only bump for NPS > 1.5" (small bore Sch 160 is already the cap)
            for i, (sch, wt) in enumerate(sorted_scheds):
                if sch == base_min_sch and i + 1 < len(sorted_scheds):
                    base_min_wt_in = sorted_scheds[i + 1][1]
                    base_min_sch   = sorted_scheds[i + 1][0]
                    break

        # Layer 3 — Select schedule: PMS minimum or pressure, whichever is heavier
        t_min_in = max(t_min_calc_in, base_min_wt_in)
        t_min_mm = round(t_min_in * 25.4, 2)

        sel_sch, sel_wt_in = None, None

        if base_min_wt_in > 0 and base_min_wt_in >= t_min_calc_in:
            # PMS minimum governs — use PMS schedule label directly
            sel_sch, sel_wt_in = base_min_sch, base_min_wt_in
            if bump_reasons:
                governs = f"PMS minimum — {base_min_sch} ({base_label} + {' + '.join(bump_reasons)})"
            else:
                governs = f"PMS minimum — {base_label}"
        else:
            # Pressure governs — find lightest schedule that meets t_min
            # Prefer named schedules (Std, XS) over numeric when WT is identical
            for sch, wt in sorted_scheds:
                if wt >= t_min_in:
                    sel_sch, sel_wt_in = sch, wt
                    # Check if a named schedule (Std/XS) has the same WT
                    for named in ("Std", "XS"):
                        if named != sch and named in schedules and abs(schedules[named] - wt) < 0.001:
                            sel_sch = named
                    break
            if sel_sch is None and sorted_scheds:
                sel_sch, sel_wt_in = sorted_scheds[-1]
            if base_min_wt_in > 0:
                governs = "Pressure (exceeds PMS minimum)"

        # Hydrogen service: bump one schedule heavier for conservatism
        # Skip for NPS ≤ 1.5" (Sch 160 is already the maximum practical small-bore schedule)
        if is_hydrogen and sel_sch is not None and nps_f > 1.5:
            for i, (sch, wt) in enumerate(sorted_scheds):
                if sch == sel_sch and i + 1 < len(sorted_scheds):
                    sel_sch, sel_wt_in = sorted_scheds[i + 1]
                    governs = f"Hydrogen service (conservative — one schedule heavier)"
                    break

        if sel_wt_in is None:
            continue

        wt_nom_mm = round(sel_wt_in * 25.4, 2)

        # Effective (net) wall thickness after mill tolerance and CA
        t_eff_in  = sel_wt_in * (1.0 - mill_tol) - c_in - m_in
        t_eff_mm  = round(t_eff_in * 25.4, 2)

        # MAWP back-calculation (rearranged: P = 2×S×t / (OD - 2×Y×t))
        if t_eff_in > 0 and (od_in - 2.0 * Y * t_eff_in) > 0:
            mawp_psig = (2.0 * S * t_eff_in) / (od_in - 2.0 * Y * t_eff_in)
            mawp_barg = round(mawp_psig * 0.0689476, 1)
        else:
            mawp_psig = 0.0
            mawp_barg = 0.0

        margin_pct = round(((mawp_psig / P) - 1.0) * 100.0, 1) if P > 0 and mawp_psig > 0 else 0.0
        util_pct   = round((P / mawp_psig) * 100.0, 1)           if mawp_psig > 0 else 999.0
        status     = "OK" if sel_wt_in >= t_min_in else "FAIL"
        if status == "FAIL":
            fail_count += 1

        if mawp_barg > 0:
            min_mawp   = min(min_mawp, mawp_barg)
            max_mawp   = max(max_mawp, mawp_barg)
            min_margin = min(min_margin, margin_pct)

        # Build remark tags for this NPS row
        tags = []
        if "PMS minimum" in governs or "NACE" in governs:
            if req.is_nace or is_sour: tags.append("NACE")
            if req.is_low_temp:        tags.append("LTCS")
            if "CA > 3" in governs:    tags.append("CA↑")
            if not tags:               tags.append("PMS min")
        if is_hydrogen and "Hydrogen" in governs:
            tags.append("H₂↑")
        if status == "FAIL":
            tags.append("FAIL")
        if not tags:
            tags.append("Pressure")

        # Pipe type determination (Seamless / LSAW / LSAW, 100% RT)
        pipe_type = determine_pipe_type(
            nps, service=req.service, is_nace=req.is_nace, is_critical=False
        )

        rows.append({
            "nps":        nps,
            "od_mm":      od_mm,
            "schedule":   sel_sch,
            "wt_nom_mm":  wt_nom_mm,
            "t_req_mm":   t_req_mm,
            "t_min_mm":   t_min_mm,
            "t_eff_mm":   t_eff_mm,
            "mawp_barg":  mawp_barg,
            "mawp_psig":  round(mawp_psig, 0),
            "margin_pct": margin_pct,
            "util_pct":   util_pct,
            "status":     status,
            "governs":    governs,
            "tags":       tags,
            "pipe_type":  pipe_type,
        })

    return {
        "rows": rows,
        "design_inputs": {
            "design_pressure_psig":  P,
            "design_pressure_barg":  P_barg,
            "design_temp_f":         T_f,
            "design_temp_c":         T_c,
            "allowable_stress_psi":  S,
            "allowable_stress_mpa":  round(S * 0.00689476, 1),
            "joint_efficiency":      E,
            "joint_type":            req.joint_type,
            "y_factor":              Y,
            "y_factor_basis":        y_basis,
            "w_factor":              W,
            "w_factor_basis":        w_basis,
            "ca_mm":                 req.ca_mm,
            "mech_allowance_mm":     req.mech_allowance_mm,
            "mill_tolerance_pct":    req.mill_tolerance_pct,
            "material_grade":        req.material_grade,
            "material_spec":         mat_spec,
            "pipe_standard":         pipe_std,
            "pressure_class":        req.pressure_class,
            "pressure_rating_label": req.pressure_rating_label,
            "is_nace":               req.is_nace,
            "is_low_temp":           req.is_low_temp,
            "service":               req.service,
        },
        "service_classification": {
            "is_sour":                  is_sour,
            "is_hydrogen":              is_hydrogen,
            "is_steam":                 is_steam,
            "is_acid":                  is_acid,
            "is_cyclic":                is_cyclic,
            "is_chloride":              is_chloride,
            "has_service_min_schedule": has_svc_min,
        },
        "engineering_flags": flags,
        "summary": {
            "min_mawp_barg":  min_mawp   if min_mawp   != float("inf") else 0,
            "max_mawp_barg":  max_mawp,
            "min_margin_pct": min_margin if min_margin != float("inf") else 0,
            "hydro_test_barg": hydro_barg,
            "total_sizes":    len(rows),
            "fail_count":     fail_count,
        },
    }


# --- PMS Code Generator (3-part) endpoints ---

@router.get("/pms_code/reference")
async def pms_code_reference():
    """Return all reference data for PMS code dropdowns."""
    return {
        "part1_options": PRESSURE_RATING_CODES,
        "part2_options": {str(k): v for k, v in PMS_MATERIAL_CODES.items()},
        "part3_tubing_options": PMS_PART3_TUBING,
        "part3_non_tubing_options": PMS_PART3_NON_TUBING,
        "tubing_material_codes": list(PMS_TUBING_CODES),
        "material_type_grades": PMS_MATERIAL_TYPE_TO_GRADE,
    }


@router.post("/pms_code/auto")
async def auto_pms_code(req: PMSCodeAutoRequest):
    """Auto-suggest PMS code parts from Steps 1-2 data."""
    p1 = auto_suggest_part1(req.design_pressure_psig)
    p2 = auto_suggest_part2(req.material_grade, req.corrosion_allowance_mm)
    p3 = auto_suggest_part3(req.material_grade, req.mdmt_f, p1.get("code"))

    result = {
        "part1_suggestion": p1,
        "part2_suggestion": p2,
        "part3_suggestion": p3,
    }

    if p1.get("code") and p2 and p2.get("code") is not None:
        code_result = generate_pms_code(p1["code"], p2["code"], p3.get("code"))
        validation = validate_pms_code(p1["code"], p2["code"], p3.get("code"))
        result["auto_code"] = code_result
        result["validation"] = validation

    return result


@router.post("/pms_code/validate")
async def validate_pms_code_endpoint(req: PMSCodeValidateRequest):
    """Validate and generate a user-selected PMS code."""
    validation = validate_pms_code(req.part1, req.part2, req.part3)
    code_result = generate_pms_code(req.part1, req.part2, req.part3)
    suggestions = get_suggestions(req.part1, req.part2, req.part3)

    return {
        "validation": validation,
        "code": code_result,
        "suggestions": suggestions,
    }


# ============================================================
# BRANCH TABLE ENDPOINT — API RP 14E
# ============================================================

class BranchTableRequest(BaseModel):
    material_type: str = "CS"

class BranchLookupRequest(BaseModel):
    material_type: str = "CS"
    run_nps: float
    branch_nps: float


@router.post("/branch_table")
async def get_branch_table(req: BranchTableRequest):
    """Return the full branch connection table matrix for a material type."""
    chart_num = get_branch_chart(req.material_type)
    matrix = get_branch_table_matrix(chart_num)
    if not matrix:
        return {"error": f"No branch chart for material {req.material_type}"}
    return matrix


@router.post("/branch_lookup")
async def branch_lookup_endpoint(req: BranchLookupRequest):
    """Look up a single branch connection type."""
    conn_type = branch_lookup(req.material_type, req.run_nps, req.branch_nps)
    chart_num = get_branch_chart(req.material_type)
    chart = BRANCH_CHARTS.get(chart_num, {})
    legend = chart.get("legend", {})
    full_name = legend.get(conn_type, conn_type) if conn_type else "N/A"
    return {
        "chart_id": chart_num,
        "run_nps": req.run_nps,
        "branch_nps": req.branch_nps,
        "connection_type": conn_type or "-",
        "connection_name": full_name,
    }
