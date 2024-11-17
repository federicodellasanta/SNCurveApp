import SNCurve as sn
import matplotlib.pyplot as plt

curve_comp = sn.curve_comp
sn_curves = sn.sn_curves

# Prompt user for S-N curve comparison
print("The available S-N curve comparisons are: ")
for i, x in enumerate(curve_comp, 1):
    print(f"{i}. {x}")
custom = sn.get_valid_integer("Type the number of the corresponding S-N curves you want to display or type 0 for a customized comparison: ", 0, len(curve_comp))


plt.figure(figsize=(10, 6))

if 1 <= custom <= len(curve_comp):
    selected_comp = curve_comp[custom - 1]
    keywords = selected_comp.split()
    sn_curves = [
        curve for curve in sn_curves 
        if all(keyword in curve.name for keyword in keywords)  # Ensure all keywords are in curve.name
    ]
    T_input = sn.get_valid_float("Enter the plate thickness (mm): ")
    for curve in sn_curves:
        Nf_vals, S_vals = curve.generate_points(T_input)
        print(curve.name)
        print(Nf_vals)
        print(S_vals)
        plt.loglog(Nf_vals, S_vals, label=f"{curve.name} (T={int(T_input)} mm)")
elif custom == 0:
    print("The available S-N curves are the followings:")
    for i, curve in enumerate(sn_curves, 1):
        print(f"{i}. {curve.name}")
    custom_list = sn.get_valid_int_list("Type the numbers corresponding to the S-N curves you want to display separated by a space: ")
    sn_curves = [sn_curves[i - 1] for i in custom_list]
    for curve in sn_curves:
        T_input = sn.get_valid_float(f"Enter the plate thickness (mm) for {curve.name}: ")
        Nf_vals, S_vals = curve.generate_points(T_input)
        print(curve.name)
        print(Nf_vals)
        print(S_vals)
        plt.loglog(Nf_vals, S_vals, label=f"{curve.name} (T={int(T_input)} mm)")
plt.xlabel("Fatigue Life (Cycles)")
plt.ylabel("Stress Range (MPa)")
plt.title("S-N Curves from international standards")
plt.legend()
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.show()