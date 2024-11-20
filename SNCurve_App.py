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
    versions = [["2021", "2024"], ["const", "var"], [""]]  # Empty cell for EC
    environments = ["Air", "Prot", "Corr"]

    # Create Table as a Grid
    grid = [[""] + standards]
    grid.append([""] + [" / ".join(versions[i]) if versions[i] else "" for i in range(len(standards))])
    for env in environments:
        row = [env]
        for i, standard in enumerate(standards):
            if versions[i]:
                for version in versions[i]:
                    row.append(f"{standard} {version} {env}".strip())
            else:
                row.append(f"{standard} {env}".strip())  # EC has no version
        grid.append(row)

    # Render Table with Buttons
    for row_idx, row in enumerate(grid):
        cols = st.columns(len(row))
        for col_idx, cell in enumerate(row):
            if row_idx == 0:  # Header row
                cols[col_idx].markdown(f"**{cell}**")
            elif row_idx == 1:  # Versions
                cols[col_idx].markdown(f"*{cell}*" if cell else "")
            else:  # Environment rows
                if col_idx == 0:
                    cols[col_idx].markdown(f"**{cell}**")
                else:
                    if cell:  # Only create a button for valid cells
                        if cols[col_idx].button(cell):
                            # Apply filters and generate plot
                            filters = cell.split()
                            selected_curves = [
                                curve for curve in sn_curves
                                if all(keyword.lower() in curve.name.lower() for keyword in filters + [groove_type.lower()])
                            ]
                            if selected_curves:
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
