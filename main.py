import streamlit as st
import pandas as pd
import numpy as np

# Streamlit app configuration
st.set_page_config(page_title="Electrical Engineering Calculator", layout="wide")

# Cache data to optimize performance
@st.cache_data
def load_table_data():
    table_data_1 = {
        "Cross-sectional area (mm²)": [1, 1.5, 2.5, 4, 6, 10, 16],
        "Method 100# (A) (above a plasterboard ceiling)": [13, 16, 21, 27, 34, 45, 57],
        "Method 101# (A) (above a plasterboard ceiling, exceeding 100mm)": [10.5, 13, 17, 22, 27, 36, 46],
        "Method 102# (A) (in a stud wall with thermal insulation)": [13, 15, 20, 26, 32, 42, 53],
        "Method 103# (A) (in a stud wall with cable touching inner wall)": [8, 10, 13.5, 17.5, 23, 30, 38],
        "Method A* (A) (enclosed in conduit)": [11.5, 14, 18, 23, 29, 38, 47],
        "Method B* (A) (enclosed in conduit on a wall)": [13, 16.5, 21, 27, 35, 46, 58],
        "Method C* (A) (clipped direct)": [16, 20, 27, 35, 47, 64, 85],
        "Voltage drop (mV/A/m)": [44, 29, 18, 11, 7.3, 4.4, 2.8]
    }
    table_12_1_data = {
        "Nominal cross-section (mm²)": [0.08, 0.14, 0.25, 0.34, 0.5, 0.75, 1.0, 1.5, 2.5, 4],
        "A: Single-core (Current rating in A)": [3, 4.5, 7, 8, 12, 15, 19, 24, 32, 42],
        "B: Multi-core (2 cores, Current rating in A)": ["-", "-", "-", "-", 3, 6, 10, 16, 22, 32],
        "B: Multi-core (3 cores, Current rating in A)": ["-", "-", "-", "-", 3, 6, 10, 16, 20, 25],
        "C: Multi-core excl. (2 or 3 cores, Current rating in A)": [2, 3, 4.5, 5, 9, 12, 15, 18, 24, 34],
        "D: Multi-core rubber-sheathed (3 cores, Current rating in A)": ["-", "-", "-", "-", "-", "-", "-", 23, 30, 41],
        "D: Special single-core (Current rating in A)": ["-", "-", "-", "-", "-", "-", "-", 30, 41, 55]
    }
    table_12_2_data = {
        "Ambient temperature (°C)": [30, 40, 50, 60, 70, 80],
        "60°C (Conversion factor)": [1.00, 0.82, 0.58, "-", "-", "-"],
        "70°C (Conversion factor)": [1.00, 0.87, 0.71, 0.50, "-", "-"],
        "80°C (Conversion factor)": [1.00, 0.89, 0.77, 0.63, 0.45, "-"],
        "85°C (Conversion factor)": [1.00, 0.90, 0.79, 0.67, 0.52, 0.41],
        "90°C (Conversion factor)": [1.00, 0.91, 0.82, 0.71, 0.58, "-"]
    }
    table_12_3_data = {
        "Number of cores under load": [5, 7, 10, 14, 24],
        "Conversion factor (Installation in the open air)": [0.75, 0.65, 0.55, 0.50, 0.40],
        "Conversion factor (Installation underground)": [0.70, 0.60, 0.45, 0.45, 0.35]
    }
    return table_data_1, table_12_1_data, table_12_2_data, table_12_3_data

# Load table data
table_data_1, table_12_1_data, table_12_2_data, table_12_3_data = load_table_data()

# Material resistivity (ohm·m) and other constants
materials = {"Copper": 1.68e-8, "Aluminum": 2.82e-8}
cable_sizes_mm2 = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]
installation_methods = {
    "Method 100# (above a plasterboard ceiling)": 0,
    "Method 101# (above a plasterboard ceiling, exceeding 100mm)": 1,
    "Method 102# (in a stud wall with thermal insulation)": 2,
    "Method 103# (in a stud wall with cable touching inner wall)": 3,
    "Method A* (enclosed in conduit)": 4,
    "Method B* (enclosed in conduit on a wall)": 5,
    "Method C* (clipped direct)": 6
}

# Initialize session state for user preferences
if "material" not in st.session_state:
    st.session_state.material = "Copper"
if "ambient_temp" not in st.session_state:
    st.session_state.ambient_temp = 30

# Functions
@st.cache_data
def calculate_resistance(length, cross_section, material):
    resistivity = materials[material]
    resistance = (resistivity * length) / (cross_section * 1e-6)  # Convert mm² to m²
    return resistance

@st.cache_data
def calculate_voltage_drop(current, resistance, is_three_phase=False, power_factor=0.8):
    if is_three_phase:
        return np.sqrt(3) * current * resistance * power_factor
    return current * resistance

@st.cache_data
def calculate_required_area(voltage_drop, current, length, material, is_three_phase=False, power_factor=0.8):
    resistivity = materials[material]
    if is_three_phase:
        area = (np.sqrt(3) * resistivity * current * length * power_factor) / (voltage_drop * 1e-6)
    else:
        area = (2 * resistivity * current * length) / (voltage_drop * 1e-6)
    return area

@st.cache_data
def get_current_rating(cross_section, num_cores, installation_method_idx):
    if cross_section not in table_data_1["Cross-sectional area (mm²)"]:
        return float('inf')
    method_keys = list(installation_methods.keys())
    method_ratings = [table_data_1[key][table_data_1["Cross-sectional area (mm²)"].index(cross_section)] for key in method_keys]
    base_rating = method_ratings[installation_method_idx]
    
    # Adjust for number of cores (using Table 12-3)
    core_factors = {2: 1.00, 3: 1.00, 5: 0.75, 7: 0.65, 10: 0.55, 14: 0.50, 24: 0.40}
    core_factor = core_factors.get(num_cores, 1.00)
    return base_rating * core_factor

# Sidebar menu
st.sidebar.title("Electrical Calculator")
option = st.sidebar.selectbox("Choose Calculation", [
    "Cable Resistance",
    "Cable Chooser",
    "Reference Table",
    "Cable Dimensioning Guide",
    "Additional Reference Tables",
    "Glossary"
])

# Cable Resistance Calculator
if option == "Cable Resistance":
    st.title("Cable Resistance Calculator")
    st.write("Calculate the resistance of a cable based on its length, cross-sectional area, and material.")
    
    col1, col2 = st.columns(2)
    with col1:
        length = st.number_input("Cable Length (meters)", min_value=0.1, value=100.0, step=0.1, help="Length of the cable in meters. Must be positive.")
        if length <= 0:
            st.error("Cable length must be greater than 0.")
    with col2:
        cross_section = st.selectbox("Cross-Sectional Area (mm²)", cable_sizes_mm2)
        material = st.selectbox("Conductor Material", list(materials.keys()), index=list(materials.keys()).index(st.session_state.material))
        st.session_state.material = material
    
    if st.button("Calculate Resistance"):
        resistance = calculate_resistance(length, cross_section, material)
        st.success(f"Cable Resistance: {resistance:.6f} ohms")

# Cable Chooser
elif option == "Cable Chooser":
    st.title("Cable Chooser")
    st.write("Select a cable size based on voltage drop, current, length, and installation conditions.")
    
    col1, col2 = st.columns(2)
    with col1:
        current = st.number_input("Current (amperes)", min_value=0.1, value=10.0, step=0.1, help="Current flowing through the cable in amperes.")
        if current <= 0:
            st.error("Current must be greater than 0.")
        length = st.number_input("Cable Length (meters)", min_value=0.1, value=100.0, step=0.1, help="Length of the cable in meters.")
    with col2:
        max_voltage_drop = st.number_input("Max Allowable Voltage Drop (volts)", min_value=0.1, value=5.0, step=0.1, help="Typically 3-5% of supply voltage (e.g., 12V for 400V system).")
        material = st.selectbox("Conductor Material", list(materials.keys()), index=list(materials.keys()).index(st.session_state.material))
        st.session_state.material = material
    
    # Environmental and Installation Factors
    st.subheader("Environmental and Installation Factors")
    col3, col4 = st.columns(2)
    with col3:
        ambient_temp = st.selectbox("Ambient Temperature (°C)", [30, 40, 50, 60], index=[30, 40, 50, 60].index(st.session_state.ambient_temp), help="Temperature of the surrounding environment.")
        st.session_state.ambient_temp = ambient_temp
        num_cores = st.selectbox("Number of Cores Under Load", [2, 3, 5, 7, 10, 14, 24], help="Number of cores carrying current.")
    with col4:
        installation_method = st.selectbox("Installation Method", list(installation_methods.keys()), help="Method of cable installation affecting current rating.")
        is_three_phase = st.checkbox("Three-Phase System", value=False, help="Check if the system is three-phase AC.")
        power_factor = st.number_input("Power Factor (for three-phase)", min_value=0.1, max_value=1.0, value=0.8, step=0.1) if is_three_phase else 0.8
    
    # Reduction factors
    temp_factors_80C = {30: 1.00, 40: 0.89, 50: 0.77, 60: 0.63}
    core_factors_open_air = {2: 1.00, 3: 1.00, 5: 0.75, 7: 0.65, 10: 0.55, 14: 0.50, 24: 0.40}
    temp_factor = temp_factors_80C.get(ambient_temp, 1.00)
    core_factor = core_factors_open_air.get(num_cores, 1.00)
    
    show_steps = st.checkbox("Show Calculation Steps", value=False)
    
    if st.button("Choose Cable"):
        if current <= 0 or length <= 0 or max_voltage_drop <= 0:
            st.error("All inputs must be greater than 0.")
        else:
            # Adjust current for reduction factors
            adjusted_current = current / (temp_factor * core_factor)
            
            if show_steps:
                st.write(f"**Step 1:** Base current: {current:.2f} A")
                st.write(f"**Step 2:** Apply temperature factor ({temp_factor} for {ambient_temp}°C): {current / temp_factor:.2f} A")
                st.write(f"**Step 3:** Apply core factor ({core_factor} for {num_cores} cores): {adjusted_current:.2f} A")
            
            required_area = calculate_required_area(max_voltage_drop, current, length, material, is_three_phase, power_factor)
            suitable_cables = [size for size in cable_sizes_mm2 if size >= required_area]
            
            if suitable_cables:
                recommended_size = min(suitable_cables)
                resistance = calculate_resistance(length, recommended_size, material)
                actual_voltage_drop = calculate_voltage_drop(current, resistance, is_three_phase, power_factor)
                
                # Check current rating
                method_idx = installation_methods[installation_method]
                base_rating = get_current_rating(recommended_size, num_cores, method_idx)
                adjusted_rating = base_rating * temp_factor * core_factor
                
                if show_steps:
                    st.write(f"**Step 4:** Required cross-sectional area: {required_area:.2f} mm²")
                    st.write(f"**Step 5:** Recommended cable size: {recommended_size} mm²")
                    st.write(f"**Step 6:** Base current rating ({installation_method}): {base_rating:.2f} A")
                    st.write(f"**Step 7:** Adjusted current rating: {adjusted_rating:.2f} A")
                
                if adjusted_current > adjusted_rating:
                    st.warning(f"Warning: Adjusted current ({adjusted_current:.2f} A) exceeds the cable's adjusted rating ({adjusted_rating:.2f} A) for {recommended_size} mm².")
                
                # Voltage drop percentage
                percentage = (actual_voltage_drop / max_voltage_drop) * 100
                color = "green" if percentage <= 80 else "orange" if percentage <= 100 else "red"
                st.markdown(f"**Actual Voltage Drop:** <span style='color:{color}'>{actual_voltage_drop:.2f} V ({percentage:.1f}% of max)</span>", unsafe_allow_html=True)
                
                st.success(f"Recommended Cable Size: {recommended_size} mm²")
                st.write(f"Calculated Resistance: {resistance:.6f} ohms")
                
                # Voltage drop chart
                lengths = np.arange(10, 101, 10)
                drops = []
                for size in [1.5, 2.5, 4]:
                    r = calculate_resistance(lengths, size, material)
                    v_drop = calculate_voltage_drop(current, r, is_three_phase, power_factor)
                    drops.append(v_drop)
                
                chart_data = {
                    "type": "line",
                    "data": {
                        "labels": list(map(str, lengths)),
                        "datasets": [
                            {"label": "1.5 mm²", "data": list(drops[0]), "borderColor": "#FF6384", "fill": False},
                            {"label": "2.5 mm²", "data": list(drops[1]), "borderColor": "#36A2EB", "fill": False},
                            {"label": "4 mm²", "data": list(drops[2]), "borderColor": "#FFCE56", "fill": False}
                        ]
                    },
                    "options": {
                        "plugins": {
                            "title": {"display": True, "text": "Voltage Drop vs. Cable Length"}
                        },
                        "scales": {
                            "x": {"title": {"display": True, "text": "Cable Length (m)"}},
                            "y": {"title": {"display": True, "text": "Voltage Drop (V)"}}
                        }
                    }
                }
                st.write("**Voltage Drop Comparison Across Lengths**")
                st.markdown(f"<div style='color: black;'>Line chart showing voltage drop increasing with cable length for different cable sizes.</div>", unsafe_allow_html=True)
                st.chart(chart_data)
            else:
                st.error("No suitable cable size found. Increase allowable voltage drop or reduce current/length.")

# Reference Table Display
elif option == "Reference Table":
    st.title("Current-Carrying Capacity and Voltage Drop Table")
    st.write("Reference table for current-carrying capacities and voltage drops at 30°C ambient and 70°C conductor operating temperature.")
    
    df = pd.DataFrame(table_data_1)
    st.dataframe(df, use_container_width=True)
    
    st.write("""
    **Notes:**
    - A*: For full installation method refer to Table 4A2 Installation Method 2 but for flat twin and earth cable.
    - B*: For full installation method refer to Table 4A2 Installation Method 20 but for flat twin and earth cable.
    - C*: For full installation method refer to Table 4A2 Installation Method 100.
    - 100#: For full installation method refer to Table 4A2 Installation Method 101.
    - 101#: For full installation method refer to Table 4A2 Installation Method 102.
    - 102#: For full installation method refer to Table 4A2 Installation Method 103.
    - 103#: For full installation method refer to Table 4A2 Installation Method 103.
    - Where a cable is to be fixed in a position such that it will not be covered with thermal insulation.
    - REGULATION 523.9, BS 5803-5: Appendix C: Avoidance of overheating of electric cables.
    - Building Regulations Approved Document B and Thermal Insulation: avoiding risks, BR 262, BRE 2001 ref.
    """)

# Cable Dimensioning Guide
elif option == "Cable Dimensioning Guide":
    st.title("Cable Dimensioning Guide")
    st.write("Guidance on current rating and dimensioning of cables, including standards, environmental influences, and an example calculation.")

    st.subheader("Current Rating and Dimensioning of Cables (LAPP)")
    st.write("""
    The dimensioning of nominal conductor cross-sections to obtain the current rating in relation to the load in uninterrupted operation is a very complex matter. When selecting, dimensioning, and using cables according to their intended purpose, various influencing factors must be taken into account in calculating the nominal conductor cross-section. These are generally normative provisions for the installation types, individual usage conditions, and operating states at the installation site.

    As a manufacturer of cables and other system-relevant products, for reasons of insurance law, LAPP is not permitted to interpret the diverse and customer-specific requirements. Accredited planning agencies must be involved here to confirm acceptance of the installation on the basis of official documents.

    Nevertheless, with this guide, we aim to support you by assisting in the safe use of our products.
    """)

    st.subheader("Standards")
    st.write("""
    The basis for calculating current loads and cross-sections of cables is the international standard **IEC 60364-5-52** (International Electrotechnical Commission). This standard deals with “Selection and erection of electrical equipment – wiring systems”. In Europe, this standard has been transposed into harmonisation document **HD 60364-5-52**, Electrical Installations of Buildings. In Germany, the original text of the HD has been adopted in **DIN VDE 0100-520**. In addition, national amendments not included in the original version of the HD have been added.

    The permissible current ratings and installation types were later combined in **DIN VDE 0298-4**. This therefore represents a mixture of national and international directives for Germany.

    **Please Note:** Different values may appear in other countries and regions due to differing national regulations. As a result, DIN VDE 0298-4 cannot be applied to other countries in general, but must be individually checked by the customer.

    For power distribution cables with a nominal voltage of 0.6/1 kV (e.g., NYY), **DIN VDE 0276-603** is the normative basis for calculating the current rating and the corresponding nominal conductor cross-section. This standard is based on European harmonisation document **HD 603** or the **IEC 60287** series.
    """)

    st.subheader("Environmental Influences and Reduction Factors")
    st.write("""
    **Temperature**

    - The **operating temperature** is the maximum permissible temperature at the conductor in uninterrupted operation (specified in the data sheet).
    - The **ambient temperature** is the temperature of the surrounding medium. The base load capacity for installation in air is an ambient temperature of +30°C.
    - **Please Note:** The ambient temperature must always be below the conductor temperature, otherwise there is no heat exchange.
    """)

    st.subheader("Influencing Factors")
    st.write("""
    - Overcrowding of cables and circuits
    - Number of loaded cores
    - Insulating compound
    - Voltage class
    - Ambient temperature differing from +30°C
    - Wound cables
    """)

    st.subheader("Example Cross-Section Calculation")
    st.write("""
    When determining a suitable nominal conductor cross-section, taking reduction factors into account, the operating current of the plant is taken as the starting point for calculation. You divide the operating current by the respective reduction factors. The result represents a fictitious current load, with which you select the next higher value in the table of basic current loads and thus arrive at an approximate nominal cable cross-section.

    **Given:**

    - **ÖLFLEX® CLASSIC 110** (Conductor temperature for permanent installation: 80°C)
    - **Installation type selected:** Permanent installation
    - **Operating current:** 10 A
    - **Number of cores under load:** 3
    - **Number of cables in installation pipe:** 3 (Table 12-6 factor 0.70)
    - **Differing ambient temperature:** 40°C (Table 12-2 factor 0.89)

    **Calculation:**

    10 Ampere ÷ 0.70 ÷ 0.89 = 16.1 Ampere (fictive)

    According to Table 12-1 (DIN VDE 0298-4 Table 11), this value of 16.1 Ampere (with 18 Ampere in the table) would result in a nominal cross-section of **1.5 mm²**.

    For a given cross-section, the reduction factors must be multiplied by the current rating of the nominal cross-section according to Table 12-1 (DIN VDE 0298-4 Table 11).

    **Please Note:** If single-core, touching, or bundled cables are overcrowded on surfaces, an additional reduction factor must be used before applying the reduction factors (DIN VDE 0298-4 Table 10).
    """)

# Additional Reference Tables
elif option == "Additional Reference Tables":
    st.title("Additional Reference Tables")
    st.write("Reference tables for current ratings and conversion factors for different cable types, ambient temperatures, and number of cores under load.")

    st.subheader("Table 12-1: Current Ratings for Different Cable Types")
    st.write("Current ratings for single-core and multi-core cables with various insulation types, installed in the open air.")
    df_12_1 = pd.DataFrame(table_12_1_data)
    filter_category = st.selectbox("Filter by Category", ["All", "A", "B", "C", "D"])
    if filter_category != "All":
        filtered_df = df_12_1[[col for col in df_12_1.columns if filter_category in col or col == "Nominal cross-section (mm²)"]]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(df_12_1, use_container_width=True)
    st.write("""
    **Notes:**
    - 1) Current rating values for small conductor cross-sections taken from VDE 0891-1 (0.08 mm² to 0.34 mm²).
    - Categories:
      - A: Single-core cables (rubber, PVC, TPE insulation, heat-resistant)
      - B: Multi-core cables for domestic/handheld equipment (rubber, PVC, TPE insulation)
      - C: Multi-core cables excluding domestic/handheld equipment (rubber, PVC, TPE insulation, heat-resistant)
      - D: Multi-core rubber-sheathed cables (min. 0.6/1 kV) and special single-core cables (0.6/1 or 1.8/3 kV)
    """)

    # Current rating comparison chart
    selected_size = st.selectbox("Select Cross-Section for Comparison (mm²)", [1.0, 1.5, 2.5, 4])
    if selected_size in table_data_1["Cross-sectional area (mm²)"]:
        idx = table_data_1["Cross-sectional area (mm²)"].index(selected_size)
        ratings = {method: table_data_1[method][idx] for method in installation_methods.keys()}
        chart_data = {
            "type": "bar",
            "data": {
                "labels": list(installation_methods.keys()),
                "datasets": [{
                    "label": f"Current Rating for {selected_size} mm²",
                    "data": list(ratings.values()),
                    "backgroundColor": "#36A2EB"
                }]
            },
            "options": {
                "plugins": {
                    "title": {"display": True, "text": f"Current Rating Comparison for {selected_size} mm²"}
                },
                "scales": {
                    "y": {"title": {"display": True, "text": "Current Rating (A)"}}
                }
            }
        }
        st.write(f"**Current Rating Comparison for {selected_size} mm² Across Installation Methods**")
        st.markdown(f"<div style='color: black;'>Bar chart comparing current ratings for {selected_size} mm² cable across different installation methods.</div>", unsafe_allow_html=True)
        st.chart(chart_data)

    st.subheader("Table 12-2: Conversion Factors for Ambient Temperature")
    st.write("Conversion factors to be applied to the current rating values in Table 12-1 for ambient temperatures other than +30°C.")
    df_12_2 = pd.DataFrame(table_12_2_data)
    st.dataframe(df_12_2, use_container_width=True)
    st.write("""
    **Notes:**
    - Values are reference values taken from DIN VDE 0298 part 4, 2013-06, table 17.
    - Details of the maximum value in °C can be found in the “Technical data, temperature range for fixed or flexible installation” on the relevant product page in the catalogue.
    - For copyright reasons, only excerpts from DIN VDE 0298 part 4 can be mapped at this point.
    """)

    st.subheader("Table 12-3: Conversion Factors for Number of Cores Under Load")
    st.write("Conversion factors for several-core cables with conductor cross-sections up to 10 mm², for installation in the open air or underground.")
    df_12_3 = pd.DataFrame(table_12_3_data)
    st.dataframe(df_12_3, use_container_width=True)
    st.write("""
    **Notes:**
    - Values are reference values taken from DIN VDE 0298 part 4, 2013-06, table 26.
    - For copyright reasons, only excerpts from DIN VDE 0298 part 4 can be mapped at this point.
    """)

# Glossary
elif option == "Glossary":
    st.title("Glossary")
    st.write("Definitions of key electrical engineering terms used in this app.")
    
    st.subheader("Current Rating")
    st.write("The maximum current a cable can carry continuously without exceeding its temperature rating, as per standards like DIN VDE 0298-4.")
    
    st.subheader("Nominal Cross-Section")
    st.write("The cross-sectional area of a cable's conductor, typically in mm², used to determine its current-carrying capacity and resistance.")
    
    st.subheader("Reduction Factor")
    st.write("A factor applied to adjust the current rating of a cable based on environmental conditions (e.g., ambient temperature, number of cores), as per Table 12-2 and Table 12-3.")
    
    st.subheader("Voltage Drop")
    st.write("The reduction in voltage along the length of a cable due to its resistance, calculated as V_drop = I * R (single-phase) or V_drop = √3 * I * R * cos(φ) (three-phase).")

st.write("Note: Calculations assume single-phase AC or DC unless specified. For three-phase, adjustments are applied accordingly.")
