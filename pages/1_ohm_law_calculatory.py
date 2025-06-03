import streamlit as st
import math

# Streamlit app configuration
st.set_page_config(page_title="Ohm's Law Calculator (EU)", page_icon="⚡️")

# Initialize session state for input fields and voltage standard
if 'resistance' not in st.session_state:
    st.session_state.resistance = 80.0
if 'current' not in st.session_state:
    st.session_state.current = 0.0
if 'voltage' not in st.session_state:
    st.session_state.voltage = 230.0
if 'power' not in st.session_state:
    st.session_state.power = 0.0
if 'voltage_standard' not in st.session_state:
    st.session_state.voltage_standard = "L-N (230V)"

# Title and description
st.title("Ohm's Law Calculator (EU)")
st.write("Calculate DC Power (Watts), Voltage (Volts), Current (Amps), or Resistance (Ohms) by entering any two non-zero values. Select EU voltage standard (L-N: 230V or L-L: 400V).")

# Voltage standard selection
voltage_standard = st.selectbox("Select Voltage Standard", ["L-N (230V)", "L-L (400V)"], index=0 if st.session_state.voltage_standard == "L-N (230V)" else 1, key="voltage_standard")
default_voltage = 230.0 if voltage_standard == "L-N (230V)" else 400.0

# Update voltage in session state if standard changes (only if voltage is the default for the previous standard)
if voltage_standard != st.session_state.voltage_standard:
    if abs(st.session_state.voltage - (230.0 if st.session_state.voltage_standard == "L-N (230V)" else 400.0)) < 0.01:
        st.session_state.voltage = default_voltage
    st.session_state.voltage_standard = voltage_standard

# Input fields
resistance = st.number_input("Resistance (R) in ohms (Ω)", min_value=0.0, value=st.session_state.resistance, step=0.1, format="%.2f", key="resistance")
current = st.number_input("Current (I) in amps (A)", min_value=0.0, value=st.session_state.current, step=0.1, format="%.2f", key="current")
voltage = st.number_input("Voltage (V) in volts (V)", min_value=0.0, value=st.session_state.voltage, step=0.1, format="%.2f", key="voltage")
power = st.number_input("Power (P) in watts (W)", min_value=0.0, value=st.session_state.power, step=0.1, format="%.2f", key="power")

# Reset button
if st.button("Reset"):
    st.session_state.resistance = 80.0
    st.session_state.current = 0.0
    st.session_state.voltage = 230.0
    st.session_state.power = 0.0
    st.session_state.voltage_standard = "L-N (230V)"
    st.experimental_rerun()

# Calculate button
if st.button("Calculate"):
    # Count non-zero inputs (ignore 0.0)
    inputs = {"Resistance (Ω)": resistance, "Current (A)": current, "Voltage (V)": voltage, "Power (W)": power}
    non_zero_inputs = [(key, value) for key, value in inputs.items() if value > 0.0]
    
    if len(non_zero_inputs) != 2:
        st.error("Please enter exactly two non-zero values to calculate the others.")
    else:
        try:
            # Initialize result dictionary
            results = {"Resistance (Ω)": resistance, "Current (A)": current, "Voltage (V)": voltage, "Power (W)": power}
            input_keys = [key for key, _ in non_zero_inputs]

            # Calculations based on provided inputs
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

            else:
                st.error("Invalid combination of inputs. Please provide exactly two non-zero values.")
                st.stop()

            # Update session state with calculated values
            st.session_state.resistance = results["Resistance (Ω)"]
            st.session_state.current = results["Current (A)"]
            st.session_state.voltage = results["Voltage (V)"]
            st.session_state.power = results["Power (W)"]

            # Display results
            st.success("Calculated Values:")
            for key, value in results.items():
                st.write(f"{key}: {value:.2f}")

        except ZeroDivisionError:
            st.error("Error: Division by zero. Please check your input values.")
        except ValueError:
            st.error("Error: Invalid calculation (e.g., negative value under square root). Please check your inputs.")

# Add formulas for reference
st.subheader("Ohm's Law and Power Formulas")
st.markdown("""
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
""")
