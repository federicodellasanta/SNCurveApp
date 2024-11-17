import SNCurve as sn
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
from io import BytesIO

# Streamlit app
st.title("S-N Curve Analysis")

# Dropdown for S-N curve comparison
curve_comp = sn.curve_comp
sn_curves = sn.sn_curves
st.write("S-N curve comparison options:")
for i, x in enumerate(curve_comp, 1):
    st.write(f"{i}. {x}")

# Custom selection logic
custom = st.number_input(
    "Type the number of the corresponding S-N curves you want to display, or type 0 for a customized comparison:", 
    min_value=0, max_value=len(curve_comp), step=1
)

# Logic for predefined or custom selection
if 1 <= custom <= len(curve_comp):
    # Predefined selection
    selected_comp = curve_comp[custom - 1]
    keywords = selected_comp.split()
    sn_curves_filtered = [
        curve for curve in sn_curves 
        if all(keyword in curve.name for keyword in keywords)
    ]
    
    # Store plate thickness inputs using session state
    thickness_input = {}
    for curve in sn_curves_filtered:
        thickness_input[curve.name] = st.number_input(
            f"Enter the plate thickness (mm) for {curve.name}:",
            min_value=1, step=1,
            key=f"thickness_{curve.name}"  # Make the input unique using curve name
        )

    if st.button("Generate Curve"):
        if sn_curves_filtered:
            # Create a figure and axis for plotting
            fig, ax = plt.subplots(figsize=(10, 6))
            for curve in sn_curves_filtered:
                # Use the thickness value stored in session state for this curve
                T_input = thickness_input[curve.name]
                Nf_vals, S_vals = curve.generate_points(T_input)
                ax.loglog(Nf_vals, S_vals, label=f"{curve.name} (T={int(T_input)} mm)")

            ax.set_xlabel("Fatigue Life (Cycles)")
            ax.set_ylabel("Stress Range (MPa)")
            ax.set_title("S-N Curves")
            ax.legend()
            ax.grid(True, which="both", linestyle="--", linewidth=0.5)
            
            # Save the plot as an SVG
            # You can save the plot to a BytesIO buffer to display in Streamlit
            buf = BytesIO()
            fig.savefig(buf, format="svg")
            buf.seek(0)

            # Display the SVG in Streamlit
            st.image(buf, use_column_width=True, output_format="SVG")
            
            plt.close(fig)  # Close the figure to avoid display issues
        else:
            st.error("No curves match your selection.")

elif custom == 0:
    # Custom selection
    st.write("Available S-N curves:")
    for i, curve in enumerate(sn_curves, 1):
        st.write(f"{i}. {curve.name}")
    
    custom_list = st.text_input(
        "Type the numbers corresponding to the S-N curves you want to display, separated by a space:"
    )

    # If custom curves are selected, store them in session state
    if custom_list:
        custom_indices = [int(x) - 1 for x in custom_list.split()]
        custom_curves = [sn_curves[i] for i in custom_indices]
        
        # Store thickness inputs dynamically based on custom curves selected
        if "thickness_inputs" not in st.session_state:
            st.session_state.thickness_inputs = {}

        for curve in custom_curves:
            if curve.name not in st.session_state.thickness_inputs:
                st.session_state.thickness_inputs[curve.name] = 1  # Default value for thickness

        # Display thickness inputs for selected custom curves
        for curve in custom_curves:
            st.session_state.thickness_inputs[curve.name] = st.number_input(
                f"Enter the plate thickness (mm) for {curve.name}:",
                min_value=1, step=1,
                key=f"thickness_{curve.name}"  # Make the input unique using curve name
            )

        if st.button("Generate Custom Curves"):
            fig, ax = plt.subplots(figsize=(10, 6))
            for curve in custom_curves:
                # Use the thickness value from session state
                T_input = st.session_state.thickness_inputs[curve.name]
                Nf_vals, S_vals = curve.generate_points(T_input)
                ax.loglog(Nf_vals, S_vals, label=f"{curve.name} (T={int(T_input)} mm)")

            ax.set_xlabel("Fatigue Life (Cycles)")
            ax.set_ylabel("Stress Range (MPa)")
            ax.set_title("S-N Curves")
            ax.legend()
            ax.grid(True, which="both", linestyle="--", linewidth=0.5)
            
            # Save the plot as an SVG
            buf = BytesIO()
            fig.savefig(buf, format="svg")
            buf.seek(0)

            # Display the SVG in Streamlit
            st.image(buf, use_column_width=True, output_format="SVG")
            
            plt.close(fig)  # Close the figure to avoid display issues
