import streamlit as st
import math

# Streamlit app configuration
st.set_page_config(page_title="Ohm's Law Calculator", page_icon="⚡️")

# Title and description
st.title("Ohm's Law Calculator")
st.write("Calculate DC Power (Watts), Voltage (Volts), Current (Amps), or Resistance (Ohms) by entering any two values.")

# Initialize input fields
resistance = st.number_input("Resistance (R) in ohms (Ω)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
current = st.number_input("Current (I) in amps (A)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
voltage = st.number_input("Voltage (V) in volts (V)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
power = st.number_input("Power (P) in watts (W)", min_value=0.0, value=0.0, step=0.1, format="%.2f")

# Calculate button
if st.button("Calculate"):
    # Count how many inputs are provided (non-zero)
    inputs = [resistance, current, voltage, power]
    non_zero_inputs = sum(1 for x in inputs if x > 0)

    if non_zero_inputs != 2:
        st.error("Please enter exactly two values to calculate the others.")
    else:
        try:
            # Initialize result dictionary
            results = {"Resistance (Ω)": resistance, "Current (A)": current, "Voltage (V)": voltage, "Power (W)": power}

            # Resistance calculations
            if resistance == 0 and voltage > 0 and current > 0:
                resistance = voltage / current
                results["Resistance (Ω)"] = resistance
            elif resistance == 0 and voltage > 0 and power > 0:
                resistance = (voltage ** 2) / power
                results["Resistance (Ω)"] = resistance
            elif resistance == 0 and power > 0 and current > 0:
                resistance = power / (current ** 2)
                results["Resistance (Ω)"] = resistance

            # Current calculations
            elif current == 0 and voltage > 0 and resistance > 0:
                current = voltage / resistance
                results["Current (A)"] = current
            elif current == 0 and power > 0 and voltage > 0:
                current = power / voltage
                results["Current (A)"] = current
            elif current == 0 and power > 0 and resistance > 0:
                current = math.sqrt(power / resistance)
                results["Current (A)"] = current

            # Voltage calculations
            elif voltage == 0 and current > 0 and resistance > 0:
                voltage = current * resistance
                results["Voltage (V)"] = voltage
            elif voltage == 0 and power > 0 and current > 0:
                voltage = power / current
                results["Voltage (V)"] = voltage
            elif voltage == 0 and power > 0 and resistance > 0:
                voltage = math.sqrt(power * resistance)
                results["Voltage (V)"] = voltage

            # Power calculations
            elif power == 0 and voltage > 0 and current > 0:
                power = voltage * current
                results["Power (W)"] = power
            elif power == 0 and voltage > 0 and resistance > 0:
                power = (voltage ** 2) / resistance
                results["Power (W)"] = power
            elif power == 0 and current > 0 and resistance > 0:
                power = (current ** 2) * resistance
                results["Power (W)"] = power

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
