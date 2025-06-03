import streamlit as st
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Streamlit app configuration
st.set_page_config(
    page_title="Ohm's Law Calculator (EU)", 
    page_icon="⚡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stNumberInput > div > div > input {
        background-color: #f0f2f6;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #ff6b6b;
        box-shadow: 0 0 8px rgba(255, 107, 107, 0.3);
    }
    
    .stSelectbox > div > div > div {
        background-color: #f0f2f6;
        border-radius: 8px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .calculation-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #ff6b6b;
        margin: 1rem 0;
    }
    
    .formula-section {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with callbacks
@st.cache_data
def get_default_values():
    return {
        "resistance": 80.0,
        "current": 0.0,
        "voltage": 230.0,
        "power": 0.0,
        "voltage_standard": "L-N (230V)"
    }

def initialize_session_state():
    defaults = get_default_values()
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Calculation functions (cached for performance)
@st.cache_data
def calculate_ohms_law(resistance, current, voltage, power, is_three_phase):
    """Calculate missing values based on Ohm's law"""
    inputs = {
        "resistance": resistance,
        "current": current,
        "voltage": voltage,
        "power": power
    }
    
    non_zero_inputs = {k: v for k, v in inputs.items() if v > 0.0}
    
    if len(non_zero_inputs) < 2:
        return None, "Please enter at least two non-zero values"
    
    if len(non_zero_inputs) > 2:
        return None, "Please enter exactly two values (set others to 0)"
    
    try:
        results = dict(inputs)
        input_keys = list(non_zero_inputs.keys())
        
        if is_three_phase:
            # Three-phase calculations
            if "resistance" in input_keys and "voltage" in input_keys:
                v_ln = voltage / math.sqrt(3)
                results["current"] = v_ln / resistance
                results["power"] = 3 * (v_ln ** 2) / resistance
                
            elif "resistance" in input_keys and "current" in input_keys:
                v_ln = current * resistance
                results["voltage"] = v_ln * math.sqrt(3)
                results["power"] = 3 * (current ** 2) * resistance
                
            elif "resistance" in input_keys and "power" in input_keys:
                v_ln = math.sqrt(power * resistance / 3)
                results["voltage"] = v_ln * math.sqrt(3)
                results["current"] = v_ln / resistance
                
            elif "voltage" in input_keys and "current" in input_keys:
                v_ln = voltage / math.sqrt(3)
                results["resistance"] = v_ln / current
                results["power"] = math.sqrt(3) * voltage * current
                
            elif "voltage" in input_keys and "power" in input_keys:
                results["current"] = power / (math.sqrt(3) * voltage)
                v_ln = voltage / math.sqrt(3)
                results["resistance"] = (v_ln ** 2) * 3 / power
                
            elif "current" in input_keys and "power" in input_keys:
                results["voltage"] = power / (math.sqrt(3) * current)
                v_ln = results["voltage"] / math.sqrt(3)
                results["resistance"] = v_ln / current
        else:
            # Single-phase/DC calculations
            if "resistance" in input_keys and "voltage" in input_keys:
                results["current"] = voltage / resistance
                results["power"] = (voltage ** 2) / resistance
                
            elif "resistance" in input_keys and "current" in input_keys:
                results["voltage"] = current * resistance
                results["power"] = (current ** 2) * resistance
                
            elif "resistance" in input_keys and "power" in input_keys:
                results["voltage"] = math.sqrt(power * resistance)
                results["current"] = math.sqrt(power / resistance)
                
            elif "voltage" in input_keys and "current" in input_keys:
                results["resistance"] = voltage / current
                results["power"] = voltage * current
                
            elif "voltage" in input_keys and "power" in input_keys:
                results["resistance"] = (voltage ** 2) / power
                results["current"] = power / voltage
                
            elif "current" in input_keys and "power" in input_keys:
                results["resistance"] = power / (current ** 2)
                results["voltage"] = power / current
                
        return results, None
        
    except (ZeroDivisionError, ValueError) as e:
        return None, f"Calculation error: {str(e)}"

def create_results_visualization(results, is_three_phase):
    """Create a visual representation of the results"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Voltage (V)', 'Current (A)', 'Resistance (Ω)', 'Power (W)'),
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}]]
    )
    
    # Color scheme
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
    values = [results['voltage'], results['current'], results['resistance'], results['power']]
    units = ['V', 'A', 'Ω', 'W']
    
    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    
    for i, (value, unit, color, pos) in enumerate(zip(values, units, colors, positions)):
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=value,
                title={'text': f"{unit}"},
                gauge={
                    'axis': {'range': [None, value * 1.5]},
                    'bar': {'color': color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, value * 0.5], 'color': "lightgray"},
                        {'range': [value * 0.5, value], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': value * 0.9
                    }
                }
            ),
            row=pos[0], col=pos[1]
        )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        title_text=f"Electrical Parameters ({'Three-Phase AC' if is_three_phase else 'Single-Phase/DC'})",
        title_x=0.5
    )
    
    return fig

# Main UI
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #2c3e50; margin-bottom: 0;'>⚡ Ohm's Law Calculator</h1>
        <p style='color: #7f8c8d; font-size: 1.1rem;'>EU Standard | Fast & Interactive</p>
    </div>
    """, unsafe_allow_html=True)

# Input section with real-time calculation
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### ⚙️ Configuration")
    
    voltage_standard = st.selectbox(
        "Voltage Standard",
        ["L-N (230V)", "L-L (400V)"],
        index=0 if st.session_state.voltage_standard == "L-N (230V)" else 1,
        help="L-N: Single-phase/DC | L-L: Three-phase AC"
    )
    
    # Auto-update voltage when standard changes
    if voltage_standard != st.session_state.voltage_standard:
        default_voltage = 230.0 if voltage_standard == "L-N (230V)" else 400.0
        if abs(st.session_state.voltage - (230.0 if st.session_state.voltage_standard == "L-N (230V)" else 400.0)) < 0.01:
            st.session_state.voltage = default_voltage
        st.session_state.voltage_standard = voltage_standard

with col2:
    st.markdown("### 🔄 Quick Actions")
    
    col_reset, col_calc = st.columns(2)
    
    with col_reset:
        if st.button("🔄 Reset", use_container_width=True):
            defaults = get_default_values()
            for key, value in defaults.items():
                st.session_state[key] = value
            st.rerun()
    
    with col_calc:
        auto_calc = st.checkbox("Auto Calculate", value=True, help="Calculate automatically when values change")

# Input fields with dynamic styling
st.markdown("### 📊 Electrical Parameters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    resistance = st.number_input(
        "🔧 Resistance (Ω)",
        min_value=0.0,
        value=st.session_state.resistance,
        step=0.1,
        format="%.2f",
        help="Resistance per phase"
    )

with col2:
    current = st.number_input(
        "⚡ Current (A)",
        min_value=0.0,
        value=st.session_state.current,
        step=0.1,
        format="%.2f",
        help="Current per phase"
    )

with col3:
    voltage = st.number_input(
        "🔋 Voltage (V)",
        min_value=0.0,
        value=st.session_state.voltage,
        step=0.1,
        format="%.2f",
        help="Line voltage"
    )

with col4:
    power = st.number_input(
        "💡 Power (W)",
        min_value=0.0,
        value=st.session_state.power,
        step=0.1,
        format="%.2f",
        help="Total power"
    )

# Real-time calculation
is_three_phase = voltage_standard == "L-L (400V)" and abs(voltage - 400.0) < 0.01

if auto_calc:
    results, error = calculate_ohms_law(resistance, current, voltage, power, is_three_phase)
else:
    results, error = None, None
    if st.button("🧮 Calculate", use_container_width=True):
        results, error = calculate_ohms_law(resistance, current, voltage, power, is_three_phase)

# Display results
if error:
    st.error(f"❌ {error}")
elif results:
    # Update session state
    st.session_state.update(results)
    
    # Results visualization
    st.markdown("### 📈 Results")
    
    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("Voltage", results['voltage'], "V", "🔋"),
        ("Current", results['current'], "A", "⚡"),
        ("Resistance", results['resistance'], "Ω", "🔧"),
        ("Power", results['power'], "W", "💡")
    ]
    
    for col, (name, value, unit, icon) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem;">{icon}</div>
                <div class="metric-value">{value:.2f}</div>
                <div class="metric-label">{name} ({unit})</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Interactive gauge visualization
    fig = create_results_visualization(results, is_three_phase)
    st.plotly_chart(fig, use_container_width=True)
    
    # Power relationship chart
    st.markdown("### 📊 Power vs Current Relationship")
    
    # Generate data for power curve
    currents = [i * 0.1 for i in range(1, 101)]  # 0.1 to 10A
    if results['resistance'] > 0:
        powers = [i**2 * results['resistance'] for i in currents]
        
        fig_power = go.Figure()
        fig_power.add_trace(go.Scatter(
            x=currents, 
            y=powers,
            mode='lines',
            name='P = I²R',
            line=dict(color='#ff6b6b', width=3)
        ))
        
        # Mark current operating point
        fig_power.add_trace(go.Scatter(
            x=[results['current']], 
            y=[results['power']],
            mode='markers',
            name='Operating Point',
            marker=dict(color='#4ecdc4', size=12, symbol='star')
        ))
        
        fig_power.update_layout(
            title="Power vs Current Curve",
            xaxis_title="Current (A)",
            yaxis_title="Power (W)",
            height=300,
            showlegend=True
        )
        
        st.plotly_chart(fig_power, use_container_width=True)

# Collapsible formula reference
with st.expander("📚 Formula Reference", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### Single-Phase/DC Formulas
        **Ohm's Law:**
        - V = I × R
        - I = V / R  
        - R = V / I
        
        **Power Formulas:**
        - P = V × I
        - P = V² / R
        - P = I² × R
        """)
    
    with col2:
        st.markdown("""
        #### Three-Phase AC Formulas
        **Power (unity power factor):**
        - P = √3 × V_LL × I
        - P = 3 × V_LN² / R
        
        **Relationships:**
        - V_LL = √3 × V_LN
        - I = V_LN / R
        """)

# Footer
st.markdown("""
---
<div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
    <small>⚡ Enhanced Ohm's Law Calculator | Built with Streamlit & Plotly</small>
</div>
""", unsafe_allow_html=True)
