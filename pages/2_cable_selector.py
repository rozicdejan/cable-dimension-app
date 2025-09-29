import streamlit as st
import pandas as pd

# ==========================
# Raw Data from Table 12-1
# ==========================
data = [
    # mm² , A(col A-1), A(col B-2), A(col B-3), A(col C-2or3), A(col D-3), A(col D-1)
    [0.08, 1.5, None, None, 1, None, None],
    [0.14, 3, None, None, 2, None, None],
    [0.25, 5, None, None, 4, None, None],
    [0.34, 8, None, None, 6, None, None],
    [0.5, 12, 3, 3, 9, None, None],
    [0.75, 15, 6, 6, 12, None, None],
    [1.0, 19, 10, 10, 15, None, None],
    [1.5, 24, 16, 16, 18, 23, 30],
    [2.5, 32, 25, 20, 26, 30, 41],
    [4, 42, 32, 25, 34, 41, 55],
    [6, 54, 40, None, 44, 53, 70],
    [10, 73, 63, None, 61, 74, 98],
    [16, 98, None, None, 82, 99, 132],
    [25, 129, None, None, 108, 131, 176],
    [35, 158, None, None, 135, 162, 218],
    [50, 198, None, None, 168, 202, 276],
    [70, 245, None, None, 207, 250, 347],
    [95, 292, None, None, 250, 301, 416],
    [120, 344, None, None, 292, None, 488],
    [150, 391, None, None, 335, None, 566],
    [185, 448, None, None, 382, None, 644],
    [240, 528, None, None, 453, None, 775],
    [300, 608, None, None, 523, None, 898],
    [400, 726, None, None, None, None, None],
    [500, 830, None, None, None, None, None],
]

columns = [
    "Nominal Cross Section (mm²)",
    "A (1 conductor)",
    "B (2 conductors)",
    "B (3 conductors)",
    "C (2 or 3 conductors)",
    "D (3 conductors)",
    "D (1 conductor)",
]

df = pd.DataFrame(data, columns=columns)

# ==========================
# Streamlit UI
# ==========================
st.set_page_config(page_title="Cable Sizing Tool", layout="wide")

st.title("⚡ Cable Sizing Tool (Table 12-1)")

st.sidebar.header("Input Parameters")
required_current = st.sidebar.number_input("Required current (A)", min_value=0.1, value=20.0, step=0.1)

cable_category = st.sidebar.selectbox(
    "Cable / Lead Category",
    ["A (Single core)", "B (Multicore for home/portable)", "C (Multicore excl. home/portable)", "D (Heavy duty rubber)"],
)

if cable_category.startswith("A"):
    column_choice = "A (1 conductor)"
elif cable_category.startswith("B"):
    method = st.sidebar.radio("Method", ["2 conductors", "3 conductors"])
    column_choice = "B (2 conductors)" if method == "2 conductors" else "B (3 conductors)"
elif cable_category.startswith("C"):
    column_choice = "C (2 or 3 conductors)"
else:  # D
    method = st.sidebar.radio("Method", ["1 conductor", "3 conductors"])
    column_choice = "D (1 conductor)" if method == "1 conductor" else "D (3 conductors)"

st.subheader("📊 Power Rating Table (DIN VDE 0298-4)")
st.dataframe(df.set_index("Nominal Cross Section (mm²)"))

# ==========================
# Calculation
# ==========================
valid_df = df[["Nominal Cross Section (mm²)", column_choice]].dropna()
suitable = valid_df[valid_df[column_choice] >= required_current]

if not suitable.empty:
    min_size = suitable.iloc[0]["Nominal Cross Section (mm²)"]
    ampacity = suitable.iloc[0][column_choice]
    st.success(f"✅ Minimum required cross section: **{min_size} mm²** (ampacity {ampacity} A)")
else:
    st.error("No suitable cable size found in this table for the given current.")

