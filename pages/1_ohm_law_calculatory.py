import streamlit as st
import math

# Streamlit app configuration
st.set_page_config(page_title="Ohm's Law Calculator", page_icon="⚡️")

# Title and description
st.title("Ohm's Law Calculator")
st.write("Calculate DC Power (Watts), Voltage (Volts), Current (Amps), or Resistance (Ohms) by entering any two values.")

# Initialize input fields
resistance = st.number_input("Resistance (R) in ohms (Ω)", min_value=0.0, value=80.0, step=0.1, format="%.2f")
current = st.number_input("Current (I) in amps (A)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
voltage = st.number_input("Voltage (V) in volts (V)", min_value=0.0, value=230.0, step=0.1, format="%.2f")
power = st.number_input("Power (P) in watts (W)", min_value=0.0, value=0.0, step=0.1, format="%.2f")

# Calculate button
if st.button("Calculate"):
    # Count how many inputs are provided (non-zero)
    inputs = [resistance, current, voltage, power]
    non_zero_inputs = sum(1 for x in inputs if x > 0)

    if non_zero_inputs != 2:
        st.error("Please enter exactly two non-zero values to calculate the others.")
    else:
        try:
            # Initialize result dictionary with input values
            results = {"Resistance (Ω)": resistance, "Current (A)": current, "Voltage (V)": voltage, "Power (W)": power}

            # Calculations based on provided inputs
            if resistance > 0 and voltage > 0 and current == 0 and power == 0:
                current = voltage / resistance  # I = V / R
                power = (voltage ** 2) / resistance  # P = V² / R
                results["Current (A)"] = current
                results["Power (W)"] = power

            elif resistance > 0 and current > 0 and voltage == 0 and power == 0:
                voltage = current * resistance  # V = I * R
                power = (current ** 2) * resistance  # P = I² * R
                results["Voltage (V)"] = voltage
                results["Power (W)"] = power

            elif resistance > 0 and power > 0 and voltage == 0 and current == 0:
                voltage = math.sqrt(power * resistance)  # V = √(P * R)
                current = math.sqrt(power / resistance)  # I = √(P / R)
                results["Voltage (V)"] = voltage
                results["Current (A)"] = current

            elif voltage > 0 and current > 0 and resistance == 0 and power == 0:
                resistance = voltage / current  # R = V / I
                power = voltage * current  # P = V * I
                results["Resistance (Ω)"] = resistance
                results["Power (W)"] = power

            elif voltage > 0 and power > 0 and resistance == 0 and current == 0:
                resistance = (voltage ** 2) / power  # R = V² / P
                current = power / voltage  # I = P / V
                results["Resistance (Ω)"] = resistance
                results["Current (A)"] = current

            elif current > 0 and power > 0 and resistance == 0 and voltage == 0:
                resistance = power / (current ** 2)  # R = P / I²
                voltage = power / current  # V = P / I
                results["Resistance (Ω)"] = resistance
                results["Voltage (V)"] = voltage

            else:
                st.error("Invalid combination of inputs. Please provide exactly two non-zero values.")
                st.stop()

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
