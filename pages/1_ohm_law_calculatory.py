import streamlit as st
import math

# Streamlit app configuration
st.set_page_config(page_title="Ohm's Law Calculator (EU)", page_icon="⚡️")

# Initialize session state defaults
def initialize_session_state():
    defaults = {
        "resistance": 80.0,
        "current": 0.0,
        "voltage": 230.0,
        "power": 0.0,
        "voltage_standard": "L-N (230V)",
        "reset_key": 0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Title and description
st.title("Ohm's Law Calculator (EU)")
st.write("Calculate Power (Watts), Voltage (Volts), Current (Amps), or Resistance (Ohms) by entering any two non-zero values. Select EU voltage standard (L-N: 230V for single-phase/DC, L-L: 400V for three-phase AC).")

# Voltage standard selection
voltage_standard = st.selectbox(
    "Select Voltage Standard",
    ["L-N (230V)", "L-L (400V)"],
    index=0 if st.session_state.voltage_standard == "L-N (230V)" else 1,
    key=f"voltage_standard_{st.session_state.reset_key}"
)

# Update voltage based on standard change (only if voltage matches previous standard's default)
default_voltage = 230.0 if voltage_standard == "L-N (230V)" else 400.0
if voltage_standard != st.session_state.voltage_standard:
    if abs(st.session_state.voltage - (230.0 if st.session_state.voltage_standard == "L-N (230V)" else 400.0)) < 0.01:
        st.session_state.voltage = default_voltage
    st.session_state.voltage_standard = voltage_standard

# Input fields
resistance = st.number_input(
    "Resistance (R) in ohms (Ω) per phase",
    min_value=0.0,
    value=st.session_state.resistance,
    step=0.1,
    format="%.2f",
    key=f"resistance_{st.session_state.reset_key}"
)
current = st.number_input(
    "Current (I) in amps (A) per phase",
    min_value=0.0,
    value=st.session_state.current,
    step=0.1,
    format="%.2f",
    key=f"current_{st.session_state.reset_key}"
)
voltage = st.number_input(
    "Voltage (V) in volts (V)",
    min_value=0.0,
    value=st.session_state.voltage,
    step=0.1,
    format="%.2f",
    key=f"voltage_{st.session_state.reset_key}"
)
power = st.number_input(
    "Power (P) in watts (W)",
    min_value=0.0,
    value=st.session_state.power,
    step=0.1,
    format="%.2f",
    key=f"power_{st.session_state.reset_key}"
)

# Reset button
if st.button("Reset"):
    st.session_state.resistance = 80.0
    st.session_state.current = 0.0
    st.session_state.voltage = 230.0
    st.session_state.power = 0.0
    st.session_state.voltage_standard = "L-N (230V)"
    st.session_state.reset_key += 1
    st.rerun()

# Calculate button
if st.button("Calculate"):
    # Count non-zero inputs (ignore 0.0)
    inputs = {
        "Resistance (Ω)": resistance,
        "Current (A)": current,
        "Voltage (V)": voltage,
        "Power (W)": power
    }
    non_zero_inputs = [(key, value) for key, value in inputs.items() if value > 0.0]

    if len(non_zero_inputs) != 2:
        st.error("Please enter exactly two non-zero values to calculate the others.")
    else:
        try:
            # Initialize result dictionary
            results = {
                "Resistance (Ω)": resistance,
                "Current (A)": current,
                "Voltage (V)": voltage,
                "Power (W)": power
            }
            input_keys = [key for key, _ in non_zero_inputs]

            # Determine if three-phase (L-L: 400V) or single-phase/DC (L-N: 230V or other)
            is_three_phase = voltage_standard == "L-L (400V)" and abs(voltage - 400.0) < 0.01

            if is_three_phase:
                # Three-phase calculations (assuming unity power factor, cos(φ) = 1)
                if "Resistance (Ω)" in input_keys and "Voltage (V)" in input_keys:
                    v_ln = voltage / math.sqrt(3)  # Line-to-neutral voltage
                    results["Current (A)"] = v_ln / resistance  # I = V_LN / R
                    results["Power (W)"] = 3 * (v_ln ** 2) / resistance  # P = 3 * (V_LN² / R)

                elif "Resistance (Ω)" in input_keys and "Current (A)" in input_keys:
                    v_ln = current * resistance  # V_LN = I * R
                    results["Voltage (V)"] = v_ln * math.sqrt(3)  # V_LL = V_LN * √3
                    results["Power (W)"] = 3 * (current ** 2) * resistance  # P = 3 * (I² * R)

                elif "Resistance (Ω)" in input_keys and "Power (W)" in input_keys:
                    v_ln = math.sqrt(power * resistance / 3)  # V_LN = √(P * R / 3)
                    results["Voltage (V)"] = v_ln * math.sqrt(3)  # V_LL = V_LN * √3
                    results["Current (A)"] = v_ln / resistance  # I = V_LN / R

                elif "Voltage (V)" in input_keys and "Current (A)" in input_keys:
                    v_ln = voltage / math.sqrt(3)  # V_LN = V_LL / √3
                    results["Resistance (Ω)"] = v_ln / current  # R = V_LN / I
                    results["Power (W)"] = math.sqrt(3) * voltage * current  # P = √3 * V_LL * I

                elif "Voltage (V)" in input_keys and "Power (W)" in input_keys:
                    results["Current (A)"] = power / (math.sqrt(3) * voltage)  # I = P / (√3 * V_LL)
                    v_ln = voltage / math.sqrt(3)  # V_LN = V_LL / √3
                    results["Resistance (Ω)"] = (v_ln ** 2) * 3 / power  # R = (V_LN² * 3) / P

                elif "Current (A)" in input_keys and "Power (W)" in input_keys:
                    results["Voltage (V)"] = power / (math.sqrt(3) * current)  # V_LL = P / (√3 * I)
                    v_ln = results["Voltage (V)"] / math.sqrt(3)  # V_LN = V_LL / √3
                    results["Resistance (Ω)"] = v_ln / current  # R = V_LN / I

            else:
                # Single-phase/DC calculations
                if "Resistance (Ω)" in input_keys and "Voltage (V)" in input_keys:
                    results["Current (A)"] = voltage / resistance  # I = V / R
                    results["Power (W)"] = (voltage ** 2) / resistance  # P = V² / R

                elif "Resistance (Ω)" in input_keys and "Current (A)" in input_keys:
                    results["Voltage (V)"] = current * resistance  # V = I * R
                    results["Power (W)"] = (current ** 2) * resistance  # P = I² * R

                elif "Resistance (Ω)" in input_keys and "Power (W)" in input_keys:
                    results["Voltage (V)"] = math.sqrt(power * resistance)  # V = √(P * R)
                    results["Current (A)"] = math.sqrt(power / resistance)  # I = √(P / R)

                elif "Voltage (V)" in input_keys and "Current (A)" in input_keys:
                    results["Resistance (Ω)"] = voltage / current  # R = V / I
                    results["Power (W)"] = voltage * current  # P = V * I

                elif "Voltage (V)" in input_keys and "Power (W)" in input_keys:
                    results["Resistance (Ω)"] = (voltage ** 2) / power  # R = V² / P
                    results["Current (A)"] = power / voltage  # I = P / V

                elif "Current (A)" in input_keys and "Power (W)" in input_keys:
                    results["Resistance (Ω)"] = power / (current ** 2)  # R = P / I²
                    results["Voltage (V)"] = power / current  # V = P / I

            # Update session state to reflect calculated values in input fields
            st.session_state.resistance = results["Resistance (Ω)"]
            st.session_state.current = results["Current (A)"]
            st.session_state.voltage = results["Voltage (V)"]
            st.session_state.power = results["Power (W)"]

            # Display results
            st.success(f"Calculated Values ({'Three-Phase AC' if is_three_phase else 'Single-Phase/DC'}):")
            for key, value in results.items():
                st.write(f"{key}: {value:.2f}")

        except ZeroDivisionError:
            st.error("Error: Division by zero. Please check your input values.")
        except ValueError:
            st.error("Error: Invalid calculation (e.g., negative value under square root). Please check your inputs.")

# Add formulas for reference
st.subheader("Ohm's Law and Power Formulas")
st.markdown("""
### Single-Phase/DC Formulas:
**Ohms calculations:**
- R = V / I
- R = V² / P
- R = P / I²

**Amps calculations:**
- I = V / R
- I = P / V
- I = √(P / R)

**Volts calculations:**
- V = I × R
- V = P / I
- V = √(P × R)

**Watts calculations:**
- P = V × I
- P = V² / R
- P = I² × R

### Three-Phase AC Formulas (L-L: 400V, assuming unity power factor):
**Power calculation:**
- P = √3 × V_LL × I
- P = 3 × (V_LN² / R), where V_LN = V_LL / √3
- P = 3 × I² × R

**Current calculation:**
- I = P / (√3 × V_LL)
- I = V_LN / R, where V_LN = V_LL / √3

**Voltage calculation (line-to-line):**
- V_LL = P / (√3 × I)
- V_LL = √(P × R / 3) × √3

**Resistance calculation:**
- R = (V_LN² × 3) / P
- R = V_LN / I, where V_LN = V_LL / √3
""")
