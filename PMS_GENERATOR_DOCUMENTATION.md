# PMS Generator — Complete Technical Documentation

> **Project:** Piping Material Specification (PMS) Generator
> **Stack:** FastAPI · Python 3 · SQLite · openpyxl
> **Standards:** ASME B31.3 · ASME B16.5-2020 · ASME B36.10M · ASME B36.19M · ASME B16.20 · NACE MR0175 · API 6A

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Project Structure](#2-project-structure)
3. [7-Step Wizard Flow](#3-7-step-wizard-flow)
4. [Stage 1 — PMS Spec Code Generation](#4-stage-1--pms-spec-code-generation)
5. [Stage 2 — Wall Thickness Calculation](#5-stage-2--wall-thickness-calculation)
6. [Stage 3 — Schedule Selection](#6-stage-3--schedule-selection)
7. [Stage 4 — P-T Rating Table](#7-stage-4--p-t-rating-table)
8. [Stage 5 — Material Selection](#8-stage-5--material-selection)
9. [Stage 6 — Flange, Gasket & Bolting](#9-stage-6--flange-gasket--bolting)
10. [Stage 7 — Valve Selection & VDS Tags](#10-stage-7--valve-selection--vds-tags)
11. [Excel PMS Sheet Generation](#11-excel-pms-sheet-generation)
12. [Database & Dashboard](#12-database--dashboard)
13. [Reference Data Tables](#13-reference-data-tables)
14. [Complete Data Flow Diagram](#14-complete-data-flow-diagram)
15. [Worked Example — A1LN (150#, CS-LT, NACE)](#15-worked-example--a1ln-150-cs-lt-nace)

---

## 1. System Overview

The PMS Generator is a web application that automates the creation of Piping Material Specification documents per industry engineering standards. It takes user inputs (pressure class, material, service conditions) and calculates:

- Required wall thickness per **ASME B31.3 Equation 3a**
- Pipe schedule selection per **ASME B36.10M / B36.19M**
- Pressure-Temperature ratings per **ASME B16.5-2020 (Metric)**
- Material selection for pipe, fittings, flanges, bolting, and valves
- VDS (Valve Data Sheet) tag codes
- Completed Excel PMS sheet (openpyxl)
- Persistent storage in SQLite database

---

## 2. Project Structure

```
pms-generator/
│
├── api/
│   ├── app.py                    # FastAPI application entry point
│   └── routers/
│       ├── calculations.py       # Core calculation endpoints
│       ├── components.py         # Fittings / flanges / valve API
│       ├── pms.py                # Excel generation + DB save
│       ├── specs.py              # Dashboard CRUD API
│       └── validation.py         # Validation endpoints
│
├── src/
│   ├── thickness_calc_module.py  # ASME B31.3 wall thickness formula
│   ├── schedule_selection_module.py  # ASME B36.10M schedule picker
│   ├── flanges_module.py         # ASME B16.5 flange / gasket / bolting
│   ├── valve_module.py           # VDS tag generation
│   ├── pms_code_module.py        # 3-part PMS code builder & validator
│   ├── spec_code_module.py       # Legacy spec code lookup
│   └── pms_generator.py          # Excel sheet builder (openpyxl)
│
├── data/
│   └── reference_data.py         # ALL reference tables (stress, dimensions, ratings)
│
├── db/
│   ├── database.py               # SQLAlchemy engine + migration runner
│   ├── models.py                 # ORM models (SavedSpec)
│   └── seed.py                   # Initial DB seed
│
├── static/
│   ├── js/app.js                 # Frontend wizard logic
│   └── js/dashboard.js           # Dashboard table + stats
│
├── templates/
│   ├── index.html                # 7-step wizard UI
│   └── dashboard.html            # Saved specs dashboard
│
├── output/                       # Generated Excel files
├── pms_generator.db              # SQLite database
└── PMS_GENERATOR_DOCUMENTATION.md  # This file
```

---

## 3. 7-Step Wizard Flow

```
Step 1 → PMS Code Selection      (Pressure Rating + Material + CA + Service)
Step 2 → P-T Rating Table        (ASME B16.5 metric lookup)
Step 3 → Wall Thickness & Sched  (ASME B31.3 Eq. 3a for all NPS sizes)
Step 4 → Fittings                (MOC selection per material grade)
Step 5 → Flanges, Gaskets, Bolts (ASME B16.5 class + ASME B16.20 gasket)
Step 6 → Valve Selection         (VDS tag generation per size range)
Step 7 → Review & Download       (Excel generation + SQLite save)
```

Each step's result is stored in the `App.data` JavaScript object and sent as a single JSON payload when the Excel is requested.

---

## 4. Stage 1 — PMS Spec Code Generation

**Files:** `src/pms_code_module.py`, `data/reference_data.py`

### 4.1 Code Format

```
[Part 1] [Part 2] [Part 3]
   A        1       LN
   ↑        ↑       ↑
Pressure  Material  Optional
 Rating   + CA     Modifier
```

**Example codes:**

| Code | Meaning |
|------|---------|
| `A1` | 150#, CS, 3mm CA, General Service |
| `A1LN` | 150#, CS-LT, 3mm CA, Low Temp + NACE |
| `B2` | 300#, CS, 6mm CA, Corrosive |
| `D9` | 600#, SS316, No CA |
| `A1N` | 150#, CS, 3mm CA, NACE service only |

---

### 4.2 Part 1 — Pressure Rating Letter

**Function:** `auto_suggest_part1(design_pressure_psig)`

Algorithm: Walk ordered class list, return **first class whose psig ≥ design pressure**.

```python
ordered = [
    ("A", 150), ("B", 300), ("D", 600), ("E", 900),
    ("F", 1500), ("G", 2500), ("J", 5000), ("K", 10000),
]
# Note: "C" is intentionally skipped to avoid confusion with tubing modifier
# "T" = Tubing (no fixed pressure)
```

| Code | Class | Max Pressure |
|------|-------|-------------|
| A | 150# | 285 psig (ambient) |
| B | 300# | 740 psig |
| D | 600# | 1,480 psig |
| E | 900# | 2,220 psig |
| F | 1,500# | 3,705 psig |
| G | 2,500# | 6,170 psig |
| J | 5,000# | 5,000 psig (API 6A) |
| K | 10,000# | 10,000 psig (API 6A) |
| T | Tubing | Defined by Part 3 (A/B/C) |

---

### 4.3 Part 2 — Material + Corrosion Allowance Number

**Function:** `auto_suggest_part2(material_grade, corrosion_allowance_mm)`

Direct lookup in `PMS_GRADE_TO_PART2` dictionary using key `(grade, ca_mm)`.
If no exact match → finds nearest CA for the same grade.

**Mapping examples:**

| Key | Code | Description |
|-----|------|-------------|
| `("A106 Gr.B", 0.0)` | 3 | CS, No CA |
| `("A106 Gr.B", 1.5)` | 1 | CS, 1.5mm CA, General |
| `("A106 Gr.B", 3.0)` | 1 | CS, 3.0mm CA |
| `("A106 Gr.B", 6.0)` | 2 | CS, 6.0mm CA, Corrosive |
| `("A333 Gr.6", 3.0)` | 1 | CS-LT, 3.0mm CA |
| `("A312 TP316", 0.0)` | 9 | SS316, No CA |
| `("A335 P11", 1.5)` | varies | Alloy P11 |

---

### 4.4 Part 3 — Optional Modifier

**Function:** `auto_suggest_part3(material_grade, mdmt_f, part1_code)`

```python
# Auto-suggest logic:
if material_grade in {"A333 Gr.6"}:   # Low-temp grades list
    return "L"

if mdmt_f is not None and mdmt_f < -20:
    return "L"

# Otherwise: no modifier needed
```

**Modifier options:**

| Modifier | Meaning | Applies To |
|----------|---------|------------|
| `L` | Low Temperature Service | Non-tubing |
| `N` | NACE MR0175 Sour Service | Non-tubing |
| `LN` | Low Temp + NACE (combined) | Non-tubing |
| `A` | 125 barg tubing pressure | Tubing (Part1=T) |
| `B` | 200 barg tubing pressure | Tubing (Part1=T) |
| `C` | 325 barg tubing pressure | Tubing (Part1=T) |

**Validation rules:**
- `LN` is valid; `NL` is **rejected** (L must precede N)
- `A/B/C` only valid when Part1 = `T`
- `L/N/LN` rejected when Part1 = `T`
- Non-metallic materials do not require `N` (warning issued)

---

### 4.5 Suggestion Engine

`get_suggestions(part1, part2, part3)` generates up to 3 alternative codes:
- If no Part3 → suggests `N`, `L`, and `LN` variants
- If Part3=`L` → suggests adding `N` → `LN`
- If Part3=`N` → suggests adding `L` → `LN`
- Also suggests higher-CA variant of same material type

---

## 5. Stage 2 — Wall Thickness Calculation

**File:** `src/thickness_calc_module.py`
**Standard:** ASME B31.3, Equation 3a (Internal Pressure)

### 5.1 Formula

```
t = (P × D) / (2 × (S × E + P × Y)) + c
```

| Variable | Description | Typical Value |
|----------|-------------|---------------|
| `P` | Design pressure (psig) | User input |
| `D` | Pipe outside diameter (inches) | From ASME B36.10M |
| `S` | Allowable stress at design temp (psi) | Interpolated from Table A-1 |
| `E` | Weld joint efficiency factor | Seamless = 1.0 |
| `Y` | Yield coefficient | 0.4 (ferrous, < 900°F) |
| `c` | Corrosion allowance (inches) | User input ÷ 25.4 |

---

### 5.2 Allowable Stress Interpolation

**Function:** `interpolate_stress(material_grade, design_temp_f)`

```python
# Step 1: Convert °F to °C
design_temp_c = (design_temp_f - 32) × 5 / 9

# Step 2: Clamp to table boundaries
if design_temp_c <= temps[0]:  return S[temps[0]]
if design_temp_c >= temps[-1]: return S[temps[-1]]

# Step 3: Linear interpolation between bracketing points
fraction = (T_design - T1) / (T2 - T1)
S = S1 + fraction × (S2 - S1)
```

**Allowable stress table — A106 Gr.B (psi):**

| Temp (°C) | Stress (psi) |
|-----------|-------------|
| -29 | 20,000 |
| 38 | 20,000 |
| 93 | 20,000 |
| 149 | 20,000 |
| 204 | 20,000 |
| 260 | 20,000 |
| 316 | 18,900 |
| 343 | 18,200 |
| 371 | 17,300 |
| 399 | 15,600 |
| 427 | 13,000 |
| 454 | 10,800 |
| 482 | 8,700 |

**Allowable stress table — A333 Gr.6 (CS-LT, psi):**

| Temp (°C) | Stress (psi) |
|-----------|-------------|
| **-46** | **20,000** ← extended low temp |
| -29 | 20,000 |
| 38 | 20,000 |
| 149 | 20,000 |
| 204 | 20,000 |
| 260 | 20,000 |
| 316 | 18,900 |
| 343 | 18,200 |

**Allowable stress table — A312 TP316 (SS, psi):**

| Temp (°C) | Stress (psi) |
|-----------|-------------|
| -198 | 20,000 |
| 149 | 19,000 |
| 204 | 17,500 |
| 260 | 16,300 |
| 316 | 15,300 |
| 427 | 14,100 |
| 538 | 13,300 |
| 649 | 9,800 |

---

### 5.3 Step-by-Step Thickness Calculation

```python
# 1. Get stress
S = interpolate_stress("A333 Gr.6", 392)   # 200°C = 392°F → ~16,025 psi

# 2. Get OD from B36.10M
D = 6.625"   # NPS 6"

# 3. Apply formula (pressure component only)
t_calc = (285 × 6.625) / (2 × (16025 × 1.0 + 285 × 0.4))
       = 1888.125 / (2 × 16139)
       = 1888.125 / 32278
       = 0.0585"

# 4. Add corrosion allowance (3mm = 0.1181")
t_min = 0.0585 + 0.1181 = 0.1766"

# 5. Apply 12.5% mill tolerance
t_nominal = 0.1766 / (1 - 0.125) = 0.1766 / 0.875 = 0.2019"  = 5.13 mm

# 6. Schedule number (informational only)
sch_no = round(1000 × 285 / 16025) = 18
```

---

### 5.4 Joint Efficiency Factors (ASME B31.3 Table 326.1)

| Joint Type | E Factor |
|------------|----------|
| Seamless | **1.0** |
| DSAW (Double Submerged Arc Weld) | **1.0** |
| ERW (Electric Resistance Weld) | **0.85** |
| SAW (Submerged Arc Weld) | **0.85** |
| Furnace Butt Weld | **0.60** |

---

## 6. Stage 3 — Schedule Selection

**File:** `api/routers/calculations.py` → `full_schedule_table()`
**Standard:** ASME B36.10M (CS) / ASME B36.19M (SS)

### 6.1 Dimension Table — ASME B36.10M (inches)

| NPS | OD (in) | Sch 40 WT | Sch 80 / XS WT | Sch 160 WT | XXS WT |
|-----|---------|-----------|-----------------|------------|--------|
| 0.5 | 0.840 | 0.109 | 0.147 | 0.188 | 0.294 |
| 0.75 | 1.050 | 0.113 | 0.154 | 0.219 | 0.308 |
| 1 | 1.315 | 0.133 | 0.179 | 0.250 | 0.358 |
| 1.5 | 1.900 | 0.145 | 0.200 | 0.281 | 0.400 |
| 2 | 2.375 | 0.154 | 0.218 | 0.344 | 0.436 |
| 3 | 3.500 | 0.216 | 0.300 | 0.438 | 0.600 |
| 4 | 4.500 | 0.237 | 0.337 | 0.531 | 0.674 |
| 6 | 6.625 | 0.280 | 0.432 | 0.719 | 0.864 |
| 8 | 8.625 | 0.322 | 0.500 | 0.906 | 0.875 |
| 10 | 10.750 | 0.365 | **0.500 (XS)** | 1.125 | — |
| 12 | 12.750 | 0.406 | **0.500 (XS)** | 1.312 | — |
| 14 | 14.000 | 0.438 | **0.500 (XS)** | 1.406 | — |
| 16 | 16.000 | 0.500 | **0.500 (XS)** | 1.594 | — |
| 18 | 18.000 | 0.562 | **0.500 (XS)** | 1.781 | — |
| 20 | 20.000 | 0.594 | **0.500 (XS)** | 1.969 | — |
| 24 | 24.000 | 0.688 | **0.500 (XS)** | 2.344 | — |
| 30 | 30.000 | 0.625 | **0.500 (XS)** | — | — |

> **XS definition:** For NPS ≤ 8" → XS = Sch 80 (same WT). For NPS ≥ 10" → XS = **0.500"** fixed.

---

### 6.2 Standard OD Values (mm) — ASME B36.10M Direct Lookup

These values are looked up from `STANDARD_OD_MM` — never computed by multiplication (avoids rounding drift like `12.75 × 25.4 = 323.85` vs standard `323.9 mm`):

| NPS | OD (mm) | NPS | OD (mm) |
|-----|---------|-----|---------|
| 0.5 | 21.3 | 12 | 323.9 |
| 0.75 | 26.7 | 14 | 355.6 |
| 1 | 33.4 | 16 | 406.4 |
| 1.25 | 42.2 | 18 | 457.0 |
| 1.5 | 48.3 | 20 | 508.0 |
| 2 | 60.3 | 22 | 559.0 |
| 3 | 88.9 | 24 | 610.0 |
| 4 | 114.3 | 26 | 660.0 |
| 6 | 168.3 | 28 | 711.0 |
| 8 | 219.1 | 30 | 762.0 |
| 10 | 273.1 | 36 | 914.4 |

---

### 6.3 Per-NPS Schedule Algorithm

For every NPS size in the table:

```python
# Step 1: Pressure-based minimum thickness
t_req_in = (P × od_in) / (2 × (S×E + P×Y))

# Step 2: Add CA + mechanical allowance + mill tolerance
t_min_calc_in = (t_req_in + c_in + m_in) / (1 - mill_tol)   # mill_tol = 0.125

# Step 3: Determine service minimum (if applicable)
has_service_min = is_nace OR is_low_temp OR ("corrosive"/"sour"/"h2s"/"flare"/"acid" in service)

if has_service_min:
    if nps <= 1.5:
        min_svc_wt = schedules.get("160")    # or "XXS" if 160 unavailable
    elif nps >= 2.0:
        min_svc_wt = schedules.get("XS")

# Step 4: Effective minimum = the larger of the two
t_min_effective = max(t_min_calc_in, min_svc_wt)

# Step 5: Pick first schedule (ascending WT order) where WT >= t_min_effective
for sch, wt in sorted(schedules.items(), key=lambda x: x[1]):
    if wt >= t_min_effective:
        selected_sch = sch
        selected_wt  = wt
        break

# Step 6: Enforce service label preference (e.g., "XS" not "80" when same WT)
if abs(selected_wt - min_svc_wt) < 0.001:
    selected_sch = service_min_label   # "XS" or "160"
```

---

### 6.4 Minimum Schedule Rules for NACE / Low Temp / Corrosive Service

| Condition | NPS Range | Min Schedule | Rationale |
|-----------|-----------|-------------|-----------|
| NACE / LT / Corrosive | ≤ 1.5" | **Sch 160** | Industry standard small bore minimum |
| NACE / LT / Corrosive | 0.5" only | **XXS** (labelled 160) | Sch 160 WT insufficient at ½" |
| NACE / LT / Corrosive | ≥ 2" | **XS** (Extra Strong) | Industry standard large bore minimum |
| Standard service | All | Pressure-calc based | No floor applied |

**Service keywords that trigger the minimum:**
`"corrosive"`, `"sour"`, `"h2s"`, `"flare"`, `"acid"`

---

### 6.5 MAWP Back-Calculation

After selecting a schedule, the system verifies it by calculating the **Maximum Allowable Working Pressure**:

```python
# Net effective thickness after deductions
t_eff = selected_wt × (1 - 0.125) - c_in - m_in

# Reverse ASME B31.3 Eq. 3a
MAWP_psig = (2 × S × E × t_eff) / (od_in - 2 × Y × t_eff)
MAWP_barg = MAWP_psig × 0.0689476

# Margin above design pressure
margin_pct = ((MAWP_psig / P) - 1) × 100

# Utilisation ratio
util_pct = (P / MAWP_psig) × 100
```

**Output per row:**

| Field | Description |
|-------|-------------|
| `nps` | Nominal pipe size |
| `od_mm` | Outside diameter (mm) |
| `schedule` | Selected schedule name |
| `wt_nom_mm` | Nominal wall thickness (mm) |
| `t_req_mm` | Required thickness, pressure only (mm) |
| `t_min_mm` | Minimum after CA + mill tol (mm) |
| `t_eff_mm` | Effective net thickness after all deductions (mm) |
| `mawp_barg` | Max allowable working pressure (barg) |
| `margin_pct` | Pressure margin % above design |
| `util_pct` | % utilisation of MAWP |
| `status` | `OK` or `FAIL` |

---

## 7. Stage 4 — P-T Rating Table

**File:** `src/pms_generator.py` → `get_pt_rating_pairs()`
**Standard:** ASME B16.5-2020 METRIC Edition (Tables 2-1.1 and 2-2.3)

### 7.1 Why METRIC Tables Are Used Directly

ASME B16.5 publishes separate **Imperial** (°F / psig) and **Metric** (°C / bar) editions with **different temperature breakpoints**. Converting from Imperial introduces rounding errors:

| Imperial Breakpoint | Converted to °C | ASME B16.5 Metric Breakpoint |
|--------------------|-----------------|-----------------------------|
| -20°F | -28.9°C | **-29°C** |
| 100°F | 37.8°C | **38°C** |
| 200°F | 93.3°C | ❌ Not in metric table — uses **50°C and 100°C** |
| 300°F | 148.9°C | **150°C** |

The system uses `FLANGE_RATINGS_CS_METRIC` / `FLANGE_RATINGS_SS_METRIC` directly.

---

### 7.2 CS Group 1.1 Metric P-T Table (ASME B16.5-2020)

| Temp (°C) | 150# (bar) | 300# (bar) | 600# (bar) | 900# (bar) | 1500# (bar) | 2500# (bar) |
|-----------|-----------|-----------|-----------|-----------|------------|------------|
| -29 | **19.6** | 51.0 | 102.1 | 153.1 | 255.5 | 425.4 |
| 38 | **19.6** | 51.0 | 102.1 | 153.1 | 255.5 | 425.4 |
| 50 | 19.2 | 50.1 | 100.0 | 150.1 | 250.2 | 417.1 |
| 100 | 17.7 | 46.6 | 93.2 | 139.6 | 232.7 | 387.8 |
| 150 | 15.8 | 45.1 | 90.7 | 135.8 | 226.2 | 377.1 |
| 200 | 13.8 | 43.8 | 87.6 | 131.0 | 218.5 | 364.1 |
| 250 | 12.1 | 41.4 | 82.7 | 123.8 | 206.5 | 344.1 |
| 300 | 10.2 | 37.9 | 75.5 | 113.1 | 188.6 | 314.4 |
| 350 | 8.6 | 36.9 | 74.1 | 111.0 | 185.1 | 308.6 |
| 400 | 6.5 | 34.8 | 69.6 | 104.1 | 173.8 | 289.6 |
| 425 | 5.5 | 28.3 | 56.9 | 85.2 | 142.0 | 236.5 |

---

### 7.3 Display Pair Compression Logic

```python
pairs = [(-29, 19.6), (38, 19.6), (50, 19.2), (100, 17.7), (150, 15.8), (200, 13.8), ...]

# If first two pairs have same pressure → merge with material min temp
if pairs[0][1] == pairs[1][1]:
    low_t = min(material_min_temp, pairs[0][0])
    #   CS (A106):  min_temp = -29°C → low_t = -29
    #   CS-LT (A333 Gr.6): min_temp = -45°C → low_t = -45

    display_pairs[0] = (f"{low_t} to {pairs[1][0]}", pairs[0][1])
    # → ("-45 to 38", 19.6)

# Limit to 5 pairs for Excel layout
display_pairs = display_pairs[:5]
```

**Material minimum design temperatures:**

| Material | Min Design Temp |
|----------|----------------|
| CS (A106 Gr.B) | -29°C |
| CS-LT (A333 Gr.6) | **-45°C** |
| SS (A312 TP316) | -196°C |
| SS (A312 TP304) | -198°C |

---

### 7.4 Hydrotest Pressure

```
Hydrotest (barg) = Ambient P-T Rating × 1.5

For CS 150#: 19.6 × 1.5 = 29.4 barg
For CS 300#: 51.0 × 1.5 = 76.5 barg
For CS 600#: 102.1 × 1.5 = 153.2 barg
```

---

## 8. Stage 5 — Material Selection

**File:** `src/pms_generator.py`

### 8.1 Effective Material Type

```python
eff_mat = material_type                        # e.g. "CS"
if material_type == "CS" and is_low_temp:
    eff_mat = "CS-LT"                          # overrides to low-temp grade
```

---

### 8.2 Pipe MOC

| Eff. Material | Seamless (NPS ≤ 16") | Welded EFW (NPS ≥ 18") |
|--------------|----------------------|------------------------|
| CS | ASTM A 106 Gr. B | ASTM A 672 Gr. B60 Class 12 |
| CS-LT | ASTM A 333 Gr.6 | ASTM A 671 CC60 Class 22 |
| SS | ASTM A 312 TP316 | ASTM A 358 TP316 Class 1 |
| Alloy | ASTM A 335 P11 | ASTM A 691 1-1/4 Cr |

**Seamless/Welded split point:** NPS ≥ 18" switches to EFW (Electric Fusion Welded).
- NPS 0.5–16" → Seamless, `SMLS`
- NPS 18–30" → EFW, `100% RT` required

---

### 8.3 Fitting MOC (ASME B16.9)

| Pipe Grade | Fitting Grade | Standard |
|-----------|--------------|---------|
| A106 Gr.B | A234 WPB | ASME B16.9 |
| A333 Gr.6 | **A420 WPL6** | ASME B16.9 |
| A312 TP316 | A403 WP316 | ASME B16.9 |
| A335 P11 | A234 WP11 | ASME B16.9 |
| A335 P22 | A234 WP22 | ASME B16.9 |

Weldolets per **MSS SP-97**, same MOC as pipe.

---

### 8.4 Flange MOC (ASME B16.5)

| Eff. Material | Flange Grade | Standard |
|--------------|-------------|---------|
| CS | ASTM A 105 | ASME B16.5 |
| CS-LT | ASTM A 350 Gr. LF2 | ASME B16.5 |
| SS | ASTM A 182 F316/F316L | ASME B16.5 |
| Alloy | ASTM A 182 F11 | ASME B16.5 |

Spectacle blinds per **ASME B16.48**, same MOC as flange.

---

### 8.5 Bolting Materials

| Condition | Stud Bolts | Nuts | Coating |
|-----------|-----------|------|---------|
| CS Standard | A193 B7 | A194 2H | None |
| CS-LT Standard | A320 L7 | A194 4 | None |
| **NACE Service** | **A320 L7M** | **A194 7ML** | **XYLAN** |
| SS | A193 B8 | A194 8 | None |
| Alloy | A193 B7 | A194 2H | None |

> **NACE override:** When `is_nace = True`, bolting always uses L7M/7ML with XYLAN coating regardless of the base material type.

---

## 9. Stage 6 — Flange, Gasket & Bolting

**File:** `src/flanges_module.py`
**Standard:** ASME B16.5 (flanges), ASME B16.20 (gaskets)

### 9.1 Flange Class Selection

```python
def select_flange_rating(design_pressure_psig, design_temp_f, material_type):

    # Choose table: FLANGE_RATINGS_CS or FLANGE_RATINGS_SS
    ratings = FLANGE_RATINGS_CS   # for CS, CS-LT, Alloy

    # Find temperature row: round UP to nearest table temperature
    for t in sorted(ratings.keys()):   # [-20, 100, 200, 300, 400, 500, 600, 650, 700, 750, 800]
        if t >= design_temp_f:
            rating_temp = t
            break

    # Find minimum class whose rating >= design pressure
    for cls in [150, 300, 400, 600, 900, 1500, 2500, 5000, 10000]:
        if ratings[rating_temp][cls] >= design_pressure_psig:
            return cls   # Selected class
```

---

### 9.2 Face Type Selection

```python
if flange_class <= 600:
    face_type   = "RF"   # Raised Face
    face_finish = "125-250 AARH"
else:
    face_type   = "RTJ"  # Ring Type Joint
    face_finish = "Per ASME B16.5"
```

| Class | Face Type | Finish |
|-------|----------|--------|
| 150# | Raised Face (RF) | 125–250 AARH, Serrated |
| 300# | Raised Face (RF) | 125–250 AARH, Serrated |
| 600# | Raised Face (RF) | 125–250 AARH, Serrated |
| 900# | Ring Type Joint (RTJ) | Per ASME B16.5 |
| 1500# | Ring Type Joint (RTJ) | Per ASME B16.5 |
| 2500# | Ring Type Joint (RTJ) | Per ASME B16.5 |

---

### 9.3 Gasket Selection (ASME B16.20)

| Eff. Material | Type | Inner Ring | Filler | Spec |
|--------------|------|-----------|--------|------|
| CS | Spiral Wound | CS | Graphite | ASME B16.20 |
| CS-LT | Spiral Wound | CS | Graphite | ASME B16.20 |
| SS | Spiral Wound | SS304 | Graphite/PTFE | ASME B16.20 |
| Alloy | Spiral Wound | Alloy Steel | Graphite | ASME B16.20 |

---

## 10. Stage 7 — Valve Selection & VDS Tags

**File:** `src/valve_module.py`

### 10.1 VDS Tag Format

```
[Type][Design][Seat][Spec Code][End Conn]
  GA     Y      M     A1LN       R
  ↑      ↑      ↑       ↑        ↑
Gate  Screw  Metal   PMS code  Raised
      &Yoke  seat              Face
```

Result: `GAYMA1LNR`

---

### 10.2 Component Codes

**Type Codes:**

| Valve Type | Code |
|-----------|------|
| Ball | `BL` |
| Butterfly | `BF` |
| Gate | `GA` |
| Globe | `GL` |
| Check | `CH` |
| Needle | `NE` |
| DBB (Double Block & Bleed) | `DB` |

**Design Codes:**

| Valve Type | Code | Meaning |
|-----------|------|---------|
| Ball | `R` | Reduced Bore |
| Butterfly | `W` | Wafer |
| Gate | `Y` | Screw & Yoke |
| Globe | `Y` | Screw & Yoke |
| Check | `P` | Piston |
| Needle | `I` | Inline Straight |
| DBB | `M` | Modular |

**Seat Codes:**

| Seat Material | Code |
|--------------|------|
| PTFE / RPTFE / EPDM | `T` |
| PEEK | `P` |
| 13Cr / Stellite / Metal | `M` |

**End Connection Codes:**

| End Connection | Code |
|---------------|------|
| Raised Face (RF) / Flanged | `R` |
| Ring Type Joint (RTJ) | `J` |
| Flat Face | `F` |
| Hub / Grayloc | `H` |
| NPT / Screwed / Socket Weld | `T` |

---

### 10.3 Valve Materials by Material Type

**CS:**

| Type | Body | Trim | Seat |
|------|------|------|------|
| Gate | A216 WCB | 13Cr/Stellite | 13Cr |
| Globe | A216 WCB | 13Cr/Stellite | 13Cr |
| Check | A216 WCB | 13Cr | 13Cr |
| Ball | A216 WCB | SS316 | PTFE/RPTFE |
| Needle | A105 | SS316 | PEEK |

**CS-LT:**

| Type | Body | Trim | Seat |
|------|------|------|------|
| Gate | A352 LCB | 13Cr/Stellite | 13Cr |
| Globe | A352 LCB | 13Cr/Stellite | 13Cr |
| Check | A352 LCB | 13Cr | 13Cr |
| Ball | A352 LCB | SS316 | PTFE/RPTFE |
| Needle | A350 LF2 | SS316 | PEEK |

**SS:**

| Type | Body | Trim | Seat |
|------|------|------|------|
| Gate | A351 CF8M | Stellite | Stellite |
| Globe | A351 CF8M | Stellite | Stellite |
| Check | A351 CF8M | SS316 | SS316 |
| Ball | A351 CF8M | SS316 | PTFE/RPTFE |
| Needle | A182 F316 | SS316 | PEEK |

---

### 10.4 End Connection by Size and Class

| Class | NPS ≤ 1.5" (Small) | NPS ≥ 2" (Large) |
|-------|-------------------|------------------|
| 150# | Screwed NPT / Socket Weld | Flanged RF |
| 300# | Socket Weld | Flanged RF |
| 600# | Socket Weld / Butt Weld | Flanged RF / Butt Weld |
| 900# | Butt Weld | Flanged RF / Butt Weld |
| 1500# | Butt Weld | Flanged RTJ / Butt Weld |
| 2500# | Butt Weld | Flanged RTJ |

---

### 10.5 VDS Tags in Excel — Size-Based Split

```python
# Small bore (NPS 0.5–1.5"): Socket/Screwed → end code = "T"
# Large bore (NPS 2"–30"):   Flanged RF     → end code = "R"

tag_small = generate_vds_code("Gate", "13Cr", "A1LN", "Screwed (NPT) / Socket Weld")
# = "GA" + "Y" + "M" + "A1LN" + "T" = "GAYMA1LNT"

tag_large = generate_vds_code("Gate", "13Cr", "A1LN", "Flanged RF")
# = "GA" + "Y" + "M" + "A1LN" + "R" = "GAYMA1LNR"
```

In the Excel sheet:
- Cols B–E (NPS 0.5–1.5"): shows `GAYMA1LNT`
- Cols F–U (NPS 2"–30"):   shows `GAYMA1LNR`

---

## 11. Excel PMS Sheet Generation

**File:** `src/pms_generator.py`
**Library:** openpyxl

### 11.1 Sheet Layout

| Rows | Section |
|------|---------|
| 1 | Company / Document Header |
| 2–3 | PMS Code, Piping Class, Material, C.A., Mill Tol, Sheet No. |
| 4–6 | Design Code, Service, Branch Chart |
| 7–9 | P-T Rating (5 pairs + Hydrotest) |
| 10–18 | Pipe Data (Code, Size, OD, Sch, WT, Type, MOC, Ends) |
| 19–27 | Fittings Data (Type, MOC, Elbow, Tee, Reducer, Cap, Plug, Weldolet) |
| 28–31 | Flange (MOC, Face, Type) |
| 32–34 | Spectacle Blind / Spacer Blinds |
| 35–38 | Bolts / Nuts / Gaskets |
| 39–46 | Valves (Rating, Ball, Gate, Globe, Check) |
| 47–54 | Notes |

### 11.2 Column Layout (20 NPS sizes)

```
Col A    = Labels (Code, Size, MOC, etc.)
Cols B–U = 20 NPS sizes (0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30)
```

### 11.3 Seamless / Welded Split

- Cols B–N (NPS 0.5"–16"): Seamless pipe
- Cols O–U (NPS 18"–30"): EFW (Electric Fusion Welded) pipe

### 11.4 Mill Tolerance

Displayed as **12.5%** in header row (Row 3, merged cols 16–18).

---

## 12. Database & Dashboard

**Files:** `db/models.py`, `api/routers/pms.py`, `api/routers/specs.py`
**Database:** SQLite (`pms_generator.db`)

### 12.1 SavedSpec Table Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment |
| `project_name` | TEXT | From metadata |
| `doc_number` | TEXT | Document number |
| `revision` | TEXT | Revision (default "0") |
| `spec_code` | TEXT (indexed) | e.g. `A1LN` |
| `material_grade` | TEXT | e.g. `A333 Gr.6` |
| `material_type` | TEXT | `CS`, `CS-LT`, `SS`, `Alloy` |
| `pipe_size` | TEXT | NPS string |
| `design_pressure_barg` | REAL | Design pressure (metric) |
| `design_temp_c` | REAL | Design temperature (°C) |
| `corrosion_allowance` | REAL | CA in mm |
| `flange_class` | TEXT | e.g. `150` |
| `service` | TEXT | Service description |
| `is_nace` | INTEGER | 0 or 1 |
| `is_low_temp` | INTEGER | 0 or 1 |
| `design_pressure` | REAL | Legacy (psig) |
| `design_temp` | REAL | Legacy (°F) |
| `excel_filename` | TEXT | Generated file name |
| `pms_data_json` | TEXT | **Full JSON of all wizard steps** |
| `created_at` | DATETIME | Auto-set |
| `updated_at` | DATETIME | Auto-updated |

### 12.2 Save Flow

```
POST /api/generate_pms
  ├── Generate Excel file → output/PMS_A1LN_YYYYMMDD_HHMMSS.xlsx
  ├── Extract engineering fields from JSON payload
  ├── INSERT INTO saved_specs (all columns)
  └── Return { success, filename, saved_to_db, db_error }
```

### 12.3 Dashboard API

| Endpoint | Method | Returns |
|----------|--------|---------|
| `/api/specs` | GET | All saved specs (DB query, newest first) |
| `/api/specs/{id}` | GET | Single spec with full `pms_data` JSON |
| `/api/specs/{id}` | DELETE | Remove from DB |
| `/api/download/{filename}` | GET | Serve Excel file (checks file exists) |

Dashboard also reports:
- `file_exists: true/false` — whether the Excel file is still on disk
- Download button is greyed out if file is missing

### 12.4 Zero Mock Data

All dashboard statistics and table rows come from live SQLite queries via SQLAlchemy ORM. No hardcoded or mock data anywhere.

---

## 13. Reference Data Tables

### 13.1 Corrosion Allowance Advisory

| Fluid | Min CA (mm) | Max CA (mm) | Notes |
|-------|-----------|-----------|-------|
| Process Water | 1.5 | 2.0 | Treated water, mild |
| Cooling Water | 1.5 | 3.0 | Open loop higher |
| Seawater | 3.0 | 6.0 | Highly corrosive |
| Steam | 0.0 | 1.5 | Erosion concern |
| Condensate | 1.5 | 3.0 | CO₂ corrosion |
| Crude Oil | 1.5 | 3.0 | H₂S / CO₂ dependent |
| Natural Gas | 1.0 | 1.5 | |
| Caustic | 1.5 | 3.0 | CS susceptible > 50% |
| Acid | 3.0 | 6.0 | Material dependent |
| Instrument Air | 0.0 | 0.0 | No corrosion |
| Hydrogen | 0.0 | 1.0 | HIC/SOHIC check for CS |

### 13.2 Unit Conversions Used

| Conversion | Formula |
|-----------|---------|
| °F → °C | `(°F - 32) × 5/9` |
| psig → bar | `psig × 0.0689476` |
| inches → mm | `inches × 25.4` |
| mm → inches | `mm / 25.4` |

---

## 14. Complete Data Flow Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║  USER INPUT (Step 1)                                                ║
║  ┌─────────────┐  ┌──────────────┐  ┌────────┐  ┌──────────────┐  ║
║  │ Part1: "A"  │  │ Part2: "1"   │  │ Part3: │  │ Service:     │  ║
║  │ 150# Class  │  │ CS, 3mm CA   │  │ "LN"   │  │ Flare/Corr.  │  ║
║  └─────────────┘  └──────────────┘  └────────┘  └──────────────┘  ║
║                          ↓                                          ║
║              PMS Code: A1LN                                         ║
║              Material: CS-LT (A333 Gr.6)                           ║
║              CA: 3.0mm | is_nace=True | is_low_temp=True            ║
╚══════════════════════════╦═══════════════════════════════════════════╝
                           ▼
╔══════════════════════════════════════════════════════════════════════╗
║  STEP 2 — ALLOWABLE STRESS                                          ║
║  Grade: A333 Gr.6 | Design Temp: 200°C = 392°F                     ║
║  Table: {-46:20000, -29:20000, ..., 316:18900, 343:18200}          ║
║  Interpolate: 392°F → ~16,025 psi                                   ║
╚══════════════════════════╦═══════════════════════════════════════════╝
                           ▼
╔══════════════════════════════════════════════════════════════════════╗
║  STEP 3 — ASME B31.3 Eq. 3a (per NPS size)                         ║
║                                                                      ║
║  For each NPS in ["0.5", "0.75", "1", "1.5", "2", ..., "30"]:      ║
║                                                                      ║
║  t_req = (P × D) / (2 × (S×E + P×Y))    ← pressure only           ║
║  t_min = (t_req + c + m) / (1 - 0.125)  ← + CA + mill tol         ║
╚══════════════════════════╦═══════════════════════════════════════════╝
                           ▼
╔══════════════════════════════════════════════════════════════════════╗
║  STEP 4 — SERVICE MINIMUM OVERRIDE                                  ║
║                                                                      ║
║  has_service_min = TRUE (NACE + LowTemp + "flare" in service)       ║
║                                                                      ║
║  NPS 0.5" → 1.5": floor = Sch 160 WT                               ║
║  NPS 2" → 30":    floor = XS WT                                     ║
║                                                                      ║
║  t_effective = MAX(t_min_calc, t_service_floor)                     ║
╚══════════════════════════╦═══════════════════════════════════════════╝
                           ▼
╔══════════════════════════════════════════════════════════════════════╗
║  STEP 5 — SCHEDULE SELECTION (B36.10M)                              ║
║                                                                      ║
║  Sort schedules ascending by WT                                      ║
║  Pick first where WT ≥ t_effective                                  ║
║  Prefer service label ("XS" / "160") when WT matches               ║
║                                                                      ║
║  Result: Sch 160 for NPS ≤1.5" | XS for NPS ≥2"                   ║
╚══════════════════════════╦═══════════════════════════════════════════╝
                           ▼
╔══════════════════════════════════════════════════════════════════════╗
║  STEP 6 — MAWP VERIFICATION                                         ║
║                                                                      ║
║  t_eff = selected_WT × 0.875 − CA − m                               ║
║  MAWP  = (2×S×E×t_eff) / (D − 2×Y×t_eff)                          ║
║  Margin% = (MAWP/P − 1) × 100                                       ║
╚══════════════════════════╦═══════════════════════════════════════════╝
                           ▼
╔══════════════════════════════════════════════════════════════════════╗
║  STEP 7 — P-T RATING (ASME B16.5 Metric)                           ║
║                                                                      ║
║  CS 150# metric table:                                              ║
║  −45 to 38°C → 19.6 bar | 50°C → 19.2 | 100°C → 17.7             ║
║  150°C → 15.8 | 200°C → 13.8                                        ║
║                                                                      ║
║  Hydrotest = 19.6 × 1.5 = 29.4 barg                                ║
╚══════════════════════════╦═══════════════════════════════════════════╝
                           ▼
╔══════════════════════════════════════════════════════════════════════╗
║  STEP 8 — MATERIAL SELECTION                                         ║
║                                                                      ║
║  Pipe (≤16"):   ASTM A 333 Gr.6 (Seamless)                         ║
║  Pipe (≥18"):   ASTM A 671 CC60 Cl.22 (EFW, 100% RT)              ║
║  Fittings:      ASTM A 420 WPL6 (ASME B16.9)                       ║
║  Flanges:       ASTM A 350 Gr. LF2 (ASME B16.5)                    ║
║  Studs:         A320 L7M + XYLAN (NACE override)                   ║
║  Nuts:          A194 7ML + XYLAN (NACE override)                   ║
║  Gaskets:       Spiral Wound CS/Graphite (ASME B16.20)             ║
╚══════════════════════════╦═══════════════════════════════════════════╝
                           ▼
╔══════════════════════════════════════════════════════════════════════╗
║  STEP 9 — VDS TAGS (per size range)                                 ║
║                                                                      ║
║  Format: [Type][Design][Seat][SpecCode][EndConn]                    ║
║  NPS ≤1.5" (Socket/NPT):  GAYMA1LNT | BLRTA1LNT                   ║
║  NPS ≥2"   (Flanged RF):  GAYMA1LNR | BLRTA1LNR                   ║
╚══════════════════════════╦═══════════════════════════════════════════╝
                           ▼
╔══════════════════════════════════════════════════════════════════════╗
║  STEP 10 — OUTPUT                                                    ║
║                                                                      ║
║  Excel:    output/PMS_A1LN_YYYYMMDD_HHMMSS.xlsx (openpyxl)         ║
║  Database: INSERT INTO saved_specs (21 columns + full JSON)         ║
║  Response: { success, filename, saved_to_db }                       ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 15. Worked Example — A1LN (150#, CS-LT, NACE)

### Inputs
| Parameter | Value |
|-----------|-------|
| PMS Code | A1LN |
| Pressure Class | 150# |
| Material | CS-LT (A333 Gr.6) |
| Design Pressure | 10 barg = 145 psig |
| Design Temperature | 38°C = 100°F |
| Corrosion Allowance | 3.0 mm = 0.1181" |
| Mill Tolerance | 12.5% |
| Joint Type | Seamless (E = 1.0) |
| NACE | Yes |
| Low Temperature | Yes |
| Service | Flare, Corrosive HC |

### Allowable Stress
```
Grade: A333 Gr.6 | Temp: 100°F = 37.8°C
Clamp to -46°C boundary → S = 20,000 psi
```

### Wall Thickness — NPS 6" as Example
```
P = 145 psig | D = 6.625" | S = 20,000 | E = 1.0 | Y = 0.4 | c = 0.1181"

t_req  = (145 × 6.625) / (2 × (20000 + 145×0.4))
       = 960.625 / 40116 = 0.02394"

t_min  = (0.02394 + 0.1181) / 0.875 = 0.1623" (4.12 mm)

Service floor (NPS 6 ≥ 2" → XS):
  XS for NPS 6 = 0.432" (10.97 mm) >> 0.1623"

t_effective = max(0.1623, 0.432) = 0.432"
Selected schedule = XS (0.432" / 10.97 mm)

MAWP:
  t_eff = 0.432 × 0.875 − 0.1181 = 0.2601"
  MAWP  = (2 × 20000 × 0.2601) / (6.625 − 0.2081) = 10404 / 6.417 = 1621 psig = 111.8 barg
  Margin = ((1621/145) − 1) × 100 = 1018%   ← schedule driven by service rule, not pressure
```

### P-T Rating
| Temperature | Max Pressure |
|-------------|-------------|
| -45 to 38°C | **19.6 barg** |
| 50°C | 19.2 barg |
| 100°C | 17.7 barg |
| 150°C | 15.8 barg |
| 200°C | 13.8 barg |
| **Hydrotest** | **29.4 barg** |

### Full Schedule Table Output
| NPS | OD (mm) | Schedule | WT (mm) | MAWP (barg) |
|-----|---------|----------|---------|------------|
| 0.5 | 21.3 | 160 | 4.78 | very high |
| 0.75 | 26.7 | 160 | 5.56 | very high |
| 1 | 33.4 | 160 | 6.35 | very high |
| 1.5 | 48.3 | 160 | 7.14 | very high |
| 2 | 60.3 | XS | 5.54 | high |
| 3 | 88.9 | XS | 7.62 | high |
| 4 | 114.3 | XS | 8.56 | high |
| 6 | 168.3 | XS | 10.97 | 111.8 |
| 8 | 219.1 | XS | 12.70 | high |
| 10 | 273.1 | XS | 12.70 | high |
| 12 | 323.9 | XS | 12.70 | high |
| 14–30 | varies | XS | 12.70 | high |

### VDS Tags
| Valve | NPS 0.5–1.5" | NPS 2–30" |
|-------|-------------|-----------|
| Ball | BLRTA1LNT | BLRTA1LNR |
| Gate | GAYMA1LNT | GAYMA1LNR |
| Globe | GLYMA1LNT | GLYMA1LNR |
| Check | CHPMA1LNT | CHPMA1LNR |

---

*Documentation generated from source code at `/Users/mac/Documents/rajeev projects/pms-generator`*
*Standards referenced: ASME B31.3, ASME B16.5-2020, ASME B36.10M, ASME B36.19M, ASME B16.20, ASME B16.9, ASME B16.48, MSS SP-97, NACE MR0175, API 6A*
