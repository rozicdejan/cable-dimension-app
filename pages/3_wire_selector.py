# app.py
import math
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Voltage Drop & Cable Sizing",
    page_icon="🔌",
    layout="centered"
)

# -----------------------------
# Constants & helpers
# -----------------------------
# Resistivity at 20°C (Ohm·mm²/m)
RESISTIVITY = {
    "Copper (Cu)": 0.0175,
    "Aluminum (Al)": 0.0282,
}

# Temperature coefficient of resistance (per °C)
TEMP_COEFF = {
    "Copper (Cu)": 0.00393,
    "Aluminum (Al)": 0.00403,
}

# Common metric sizes (mm²) you can actually buy
METRIC_STEPS = [0.5, 0.75, 1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400]

def resistivity_at_temp(material: str, temp_c: float) -> float:
    """Return Ohm·mm²/m at given temperature."""
    rho20 = RESISTIVITY[material]
    alpha = TEMP_COEFF[material]
    return rho20 * (1 + alpha * (temp_c - 20.0))

def awg_to_area_mm2(awg: float) -> float:
    """
    Compute cross-sectional area (mm²) from AWG size (can be integer or like -1 for 1/0).
    AWG formula: d(inch) = 0.005 * 92^((36-AWG)/39)
    """
    # Handle 1/0..4/0 input via negatives: 1/0 -> -1, 2/0 -> -2, etc.
    if awg <= 0:
        # Map -1 -> 1/0 = 0 AWG, -2 -> 2/0, etc.
        # Convert to an equivalent "gauge index" that fits formula: 0 AWG = 0, 00 = -1 etc.
        # We'll map: -1 => "0 AWG", -2 => "00 AWG" (aka 2/0) ...
        # The formula expects a numeric AWG, so approximate using known areas instead.
        # To stay precise, use a small lookup for 0..4/0:
        zero_lookup = {0: 53.5,  # 0 AWG
                       -1: 67.4, # 00 AWG (2/0)
                       -2: 85.0, # 000 AWG (3/0)
                       -3: 107.0 # 0000 AWG (4/0)
                      }
        key = int(awg)  # e.g., -1, -2, -3
        if key == 0:
            return zero_lookup[0]
        return zero_lookup.get(key, 107.0)
    # Standard AWG via formula
    d_inch = 0.005 * (92 ** ((36 - awg) / 39.0))
    d_m = d_inch * 0.0254
    area = math.pi * (d_m ** 2) / 4.0  # m²
    return area * 1e6  # mm²

def build_awg_table():
    rows = []
    # 24 AWG down to 4 AWG, plus 2, 1, 1/0..4/0
    for g in range(24, 3, -1):
        rows.append({"AWG": g, "Area_mm2": awg_to_area_mm2(g)})
    rows += [
        {"AWG": 3, "Area_mm2": awg_to_area_mm2(3)},
        {"AWG": 2, "Area_mm2": awg_to_area_mm2(2)},
        {"AWG": 1, "Area_mm2": awg_to_area_mm2(1)},
        {"AWG": "1/0", "Area_mm2": 53.5},
        {"AWG": "2/0", "Area_mm2": 67.4},
        {"AWG": "3/0", "Area_mm2": 85.0},
        {"AWG": "4/0", "Area_mm2": 107.0},
    ]
    df = pd.DataFrame(rows)
    return df.sort_values(by="Area_mm2", ascending=True).reset_index(drop=True)

AWG_TABLE = build_awg_table()

def pick_metric_size(area_req: float) -> float:
    for s in METRIC_STEPS:
        if s >= area_req:
            return s
    return METRIC_STEPS[-1]

def pick_awg(area_req: float):
    # Find the smallest AWG area >= area_req
    matches = AWG_TABLE[AWG_TABLE["Area_mm2"] >= area_req]
    if len(matches) == 0:
        return "≥ 4/0", AWG_TABLE.iloc[-1]["Area_mm2"]
    row = matches.iloc[0]
    return row["AWG"], row["Area_mm2"]

# -----------------------------
# UI
# -----------------------------
st.title("🔌 Voltage Drop & Cable Sizing (DC)")
st.caption("Compute loop resistance, voltage drop, wire loss, and recommended conductor size (mm² & AWG).")

with st.sidebar:
    st.header("Inputs")
    V = st.number_input("Supply voltage (V)", min_value=1.0, value=24.0, step=1.0)
    one_way_len_m = st.number_input("One-way cable length (m)", min_value=0.1, value=10.0, step=0.5)
    material = st.selectbox("Conductor material", list(RESISTIVITY.keys()), index=0)
    temp_c = st.number_input("Conductor temperature (°C)", value=30.0, step=1.0)
    n_parallel = st.number_input("Parallel conductors per leg", min_value=1, value=1, step=1,
                                 help="Number of conductors in parallel for +V (and same for return).")

    st.markdown("---")
    st.subheader("Load")
    mode = st.radio("Provide", ["Power (W)", "Current (A)"], horizontal=True)
    if mode == "Power (W)":
        P_load = st.number_input("Load power (W)", min_value=0.0, value=96.0, step=1.0)
        I = P_load / V if V > 0 else 0.0
    else:
        I = st.number_input("Load current (A)", min_value=0.0, value=4.0, step=0.1)

    st.markdown("---")
    drop_pct_allow = st.number_input("Max allowed voltage drop (%)", min_value=0.1, value=3.0, step=0.1)

# -----------------------------
# Calculations
# -----------------------------
loop_len_m = 2.0 * one_way_len_m  # out + return
rho_T = resistivity_at_temp(material, temp_c)  # Ohm·mm²/m
drop_allow_V = V * (drop_pct_allow / 100.0)

# For a given single-conductor area A_single, effective area per leg = n_parallel * A_single
# Required per-conductor area to meet drop:
# ΔV_allow >= I * R_loop = I * (rho_T * loop_len_m / (n_parallel * A_single))
# => A_single >= (rho_T * loop_len_m * I) / (n_parallel * ΔV_allow)
A_req_per_conductor = (rho_T * loop_len_m * max(I, 0.0)) / max(n_parallel * drop_allow_V, 1e-12)

metric_reco = pick_metric_size(A_req_per_conductor)
awg_reco, awg_reco_area = pick_awg(A_req_per_conductor)

# For reporting, compute performance for the recommended metric size:
A_eff_metric = metric_reco * n_parallel  # mm² per leg effective
R_loop_metric = rho_T * loop_len_m / max(A_eff_metric, 1e-12)  # Ohm
Vdrop_metric = I * R_loop_metric
P_loss_metric = (I ** 2) * R_loop_metric
V_load_metric = V - Vdrop_metric
drop_pct_metric = 100.0 * (Vdrop_metric / V) if V > 0 else 0.0

# And for the recommended AWG:
A_eff_awg = awg_reco_area * n_parallel
R_loop_awg = rho_T * loop_len_m / max(A_eff_awg, 1e-12)
Vdrop_awg = I * R_loop_awg
P_loss_awg = (I ** 2) * R_loop_awg
V_load_awg = V - Vdrop_awg
drop_pct_awg = 100.0 * (Vdrop_awg / V) if V > 0 else 0.0

# -----------------------------
# Output
# -----------------------------
st.subheader("Results")

col1, col2 = st.columns(2)
with col1:
    st.metric("Calculated load current (A)", f"{I:.3f}")
    st.metric("Allowed drop (V)", f"{drop_allow_V:.3f}")
    st.metric("Required area per conductor (mm²)", f"{A_req_per_conductor:.3f}")

with col2:
    st.metric("Loop length (m)", f"{loop_len_m:.3f}")
    st.metric("Material ρ @T (Ω·mm²/m)", f"{rho_T:.6f}")
    st.metric("Parallel per leg", f"{n_parallel}")

st.markdown("### Recommendation (Metric)")
st.write(f"**Use at least:** `{metric_reco} mm²` per conductor (with `{n_parallel}` in parallel per leg).")
st.table(pd.DataFrame([
    {"Item": "Loop resistance (Ω)", "Value": f"{R_loop_metric:.6f}"},
    {"Item": "Voltage drop (V)", "Value": f"{Vdrop_metric:.4f}"},
    {"Item": "Voltage drop (%)", "Value": f"{drop_pct_metric:.2f}%"},
    {"Item": "Wire I²R loss (W)", "Value": f"{P_loss_metric:.3f}"},
    {"Item": "Load voltage (V)", "Value": f"{V_load_metric:.3f}"},
]))

st.markdown("### Recommendation (AWG)")
st.write(f"**Closest AWG ≥ required area:** `{awg_reco}`  (area ≈ {awg_reco_area:.2f} mm²) per conductor, "
         f"with `{n_parallel}` in parallel per leg.")
st.table(pd.DataFrame([
    {"Item": "Loop resistance (Ω)", "Value": f"{R_loop_awg:.6f}"},
    {"Item": "Voltage drop (V)", "Value": f"{Vdrop_awg:.4f}"},
    {"Item": "Voltage drop (%)", "Value": f"{drop_pct_awg:.2f}%"},
    {"Item": "Wire I²R loss (W)", "Value": f"{P_loss_awg:.3f}"},
    {"Item": "Load voltage (V)", "Value": f"{V_load_awg:.3f}"},
]))

st.markdown("---")
with st.expander("Assumptions & Notes"):
    st.write("""
- **DC calculation**: \( \Delta V = I \cdot R_{\mathrm{loop}} \) and \( R_{\mathrm{loop}} = \\rho(T)\\,\\dfrac{2L}{A_{\mathrm{eff}}} \).
- \( \\rho(T) = \\rho_{20} \\cdot [1 + \\alpha (T-20)] \) using typical \(\\alpha\) for Cu/Al.
- Effective area per leg is **n_parallel × area_per_conductor**; both supply and return assumed same.
- Metric and AWG recommendations pick the **next available size** equal to or above the required area.
- Real installations should also consider **ampacity**, **insulation temperature rating**, **bundling**, and **standards** (IEC/NEC).
""")

st.caption("Tip: Set allowed drop to ~3% for distribution runs; tighten to 1–2% for sensitive loads.")
