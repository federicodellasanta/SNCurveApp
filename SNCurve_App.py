import SNCurve as sn
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
from io import BytesIO

# Introductory Section
st.title("S-N Curve Analysis")

st.markdown("### Acronyms")
st.markdown("""
- **Standards**:
  - DNV-RP-C203-2021 (DNV 2021)
  - DNV-RP-C203-2024 (DNV 2024)
  - BS 7608:2014+A1:2015 under constant (BS const) or variable (BS var) amplitude loading
  - EN 1993-1-9:2005:E (EC)
- **Groove Types**:
  - In as welded conditions (AW)
  - Ground flush (GF)
- **Environments**:
  - Air
  - Seawater with cathodic protection (prot)
  - Seawater without cathodic protection (corr)
""")

# Dropdown for Plot Type Selection
st.markdown("### Choose Plot Type")
plot_type = st.radio("Select plot type:", ["Guided Plot", "Custom Plot"], horizontal=True)

sn_curves = sn.sn_curves

# Thickness input
st.markdown("### Plate Thickness")
plate_thickness = st.number_input(
    "Enter the plate thickness (mm):", min_value=1, max_value=100, step=1, value=25
)

if plot_type == "Guided Plot":
    # Groove Type Selection
    st.markdown("### Select Groove Type")
    groove_type = st.radio("Choose groove type:", ["AW", "GF"], horizontal=True)

    # Standards Table with Buttons
    st.markdown("### Select Standard and Environment")
    st.write("Click a button to filter curves.")

    # Table Configuration
    standards = ["DNV", "BS", "EC"]
    versions = [["2021", "2024"], ["const", "var"], [""]]
    environments = ["Air", "Prot", "Corr"]

    # Table Rendering
    for i, standard in enumerate(standards):
        st.markdown(f"#### {standard}")
        columns = st.columns(len(environments) if versions[i] else 1)
        for j, version in enumerate(versions[i]):
            for k, env in enumerate(environments):
                with columns[k]:
                    button_label = f"{standard} {version} {env}".strip()
                    if st.button(button_label):
                        # Apply filters based on button clicked
                        selected_curves = [
                            curve for curve in sn_curves
                            if all(keyword in curve.name.lower() for keyword in [standard.lower(), version.lower(), env.lower(), groove_type.lower()])
                        ]
                        if selected_curves:
                            # Generate and Display Plot
                            fig, ax = plt.subplots(figsize=(10, 6))
                            for curve in selected_curves:
                                Nf_vals, S_vals = curve.generate_points(plate_thickness)
                                ax.loglog(Nf_vals, S_vals, label=f"{curve.name} (T={int(plate_thickness)} mm)")

                            ax.set_xlabel("Fatigue Life (Cycles)")
                            ax.set_ylabel("Stress Range (MPa)")
                            ax.set_title("S-N Curves")
                            ax.legend()
                            ax.grid(True, which="both", linestyle="--", linewidth=0.5)

                            # Save as SVG
                            buf = BytesIO()
                            fig.savefig(buf, format="svg")
                            buf.seek(0)
                            svg_data = buf.getvalue().decode("utf-8")
                            st.markdown(f'<div>{svg_data}</div>', unsafe_allow_html=True)
                            
                            plt.close(fig)
                        else:
                            st.error("No curves match your selection.")

elif plot_type == "Custom Plot":
    # Tables for Custom Selection
    st.markdown("### Custom Plot Configuration")
    st.write("Select multiple curves from the tables below.")

    # Table for AW
    st.markdown("#### AW Curves")
    aw_curves = [
        curve for curve in sn_curves if "aw" in curve.name.lower()
    ]
    selected_aw = st.multiselect(
        "Select AW curves:",
        options=[curve.name for curve in aw_curves]
    )

    # Table for GF
    st.markdown("#### GF Curves")
    gf_curves = [
        curve for curve in sn_curves if "gf" in curve.name.lower()
    ]
    selected_gf = st.multiselect(
        "Select GF curves:",
        options=[curve.name for curve in gf_curves]
    )

    selected_curves = selected_aw + selected_gf

    if selected_curves:
        st.markdown("### Plate Thickness for Each Curve")
        thickness_inputs = {
            curve: st.number_input(
                f"Enter thickness for {curve}:", 
                min_value=1, max_value=100, step=1, value=plate_thickness
            ) 
            for curve in selected_curves
        }

        if st.button("Generate Custom Plot"):
            # Generate and Display Plot
            fig, ax = plt.subplots(figsize=(10, 6))
            for curve_name in selected_curves:
                curve = next(curve for curve in sn_curves if curve.name == curve_name)
                T_input = thickness_inputs[curve_name]
                Nf_vals, S_vals = curve.generate_points(T_input)
                ax.loglog(Nf_vals, S_vals, label=f"{curve.name} (T={int(T_input)} mm)")

            ax.set_xlabel("Fatigue Life (Cycles)")
            ax.set_ylabel("Stress Range (MPa)")
            ax.set_title("S-N Curves")
            ax.legend()
            ax.grid(True, which="both", linestyle="--", linewidth=0.5)
            
            # Save as SVG
            buf = BytesIO()
            fig.savefig(buf, format="svg")
            buf.seek(0)
            svg_data = buf.getvalue().decode("utf-8")
            st.markdown(f'<div>{svg_data}</div>', unsafe_allow_html=True)
            
            plt.close(fig)
