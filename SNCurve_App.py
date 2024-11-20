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

if plot_type == "Guided Plot":
    # Groove Type Selection
    st.markdown("### Select Groove Type")
    groove_type = st.radio("Choose groove type:", ["AW", "GF"], horizontal=True)

    # Thickness input
    st.markdown("### Plate Thickness")
    plate_thickness = st.number_input(
        "Enter the plate thickness (mm):", min_value=1, max_value=100, step=1, value=25
    )

    # Standards and Environment Table
    st.markdown("### Select Standard and Environment")
    st.write("Click any cell to filter curves.")

    # Table Data
    standards = ["DNV", "BS", "EC"]
    versions = ["2021", "2024", "const", "var", ""]  # Last cell empty for merged EC
    environments = ["Air", "Prot", "Corr"]

    # Filters
    active_filters = {"standard": None, "version": None, "environment": None}

    def apply_filter(key, value):
        if active_filters[key] == value:
            active_filters[key] = None  # Toggle off
        else:
            active_filters[key] = value  # Toggle on

    # Table Rows
    header_row = st.columns(len(standards) + 1)
    header_row[0].markdown("")  # Empty top-left cell
    for idx, standard in enumerate(standards):
        if header_row[idx + 1].button(standard):
            apply_filter("standard", standard)

    second_row = st.columns(len(versions) + 1)
    second_row[0].markdown("")  # Empty cell for left column
    for idx, version in enumerate(versions):
        if idx == len(versions) - 1:  # Merge the last column for EC
            second_row[idx + 1].markdown("**EC**", unsafe_allow_html=True)
        elif second_row[idx + 1].button(version):
            apply_filter("version", version)

    # Main Rows (Environment Rows)
    for env in environments:
        row = st.columns(len(standards) + 1)
        row[0].markdown(f"**{env}**")  # First column: environment
        for idx, standard in enumerate(standards):
            if versions[idx]:  # Only create cells for standards with versions
                for version in versions[:len(versions) - 1]:  # Exclude the merged EC cell
                    curve_filter = f"{standard} {version} {env} {groove_type}"
                    if row[idx + 1].button(f"{standard} {version} {env}"):
                        apply_filter("environment", curve_filter)
            else:  # Handle EC (no versions)
                curve_filter = f"{standard} {env} {groove_type}"
                if row[idx + 1].button(f"{standard} {env}"):
                    apply_filter("environment", curve_filter)

    # Filter and Display Matching Curves
    if st.button("Apply Filters and Plot"):
        filtered_curves = sn_curves
        for key, filter_val in active_filters.items():
            if filter_val:
                filtered_curves = [
                    curve for curve in filtered_curves
                    if filter_val.lower() in curve.name.lower()
                ]

        if filtered_curves:
            fig, ax = plt.subplots(figsize=(10, 6))
            for curve in filtered_curves:
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
    st.markdown("### Custom Plot Configuration")
    st.write("Select multiple curves from the tables below.")

    # Tables for AW and GF
    st.markdown("#### AW Curves")
    aw_curves = [
        curve for curve in sn_curves if "aw" in curve.name.lower()
    ]
    selected_aw = st.multiselect(
        "Select AW curves:",
        options=[curve.name for curve in aw_curves]
    )

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
                min_value=1, max_value=100, step=1
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
