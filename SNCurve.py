import numpy as np
import matplotlib.pyplot as plt

class SNCurve:
    def __init__(self, name, m_list, q_list, c, breakpoints_S=None, breakpoints=None, teff=False):
        """
        Initialize the S-N curve object.

        Parameters:
        - name: Name of the S-N curve
        - q_list: List of intercepts (one per segment)
        - m_list: List of slopes (one per segment)
        - c: Thickness correction exponent
        - breakpoints: List of changes in slope (Nf or S values, depending on breakpoints_S)
        - breakpoints_S: List of booleans to indicate if each breakpoint is S (True) or Nf (False)
        - teff: Boolean, True if DNV thickness correction applies
        """
        self.name = name
        self.m_list = m_list
        self.q_list = q_list
        self.c = c
        self.breakpoints = breakpoints or []
        self.breakpoints_S = breakpoints_S if breakpoints_S is not None else [False] * len(self.breakpoints)
        self.teff = teff

    def compute_teff(self, T):
        """
        Compute effective thickness (T_eff) based on DNV rules.

        Parameters:
        - T: Input thickness (mm)

        Returns:
        - T_eff: Effective thickness (mm)
        """
        if T < 25:
            return 25
        if self.teff:
            return T if T < 32.5 else 15.98 + 0.51 * T
        return T

    def calculate_stress(self, Nf, T):
        """
        Calculate stress range (S) for a given fatigue life (Nf) and thickness (T).

        Parameters:
        - Nf: Fatigue life (cycles)
        - T: Thickness of the plate (mm)

        Returns:
        - S: Stress range (MPa)
        """
        T_eff = self.compute_teff(T)

        # Determine which segment applies
        segment = 0
        for i, bp in enumerate(self.breakpoints):
            if self.breakpoints_S[i]:
                bp = 10 ** (self.q_list[i] - self.m_list[i] * np.log10(bp))
            if Nf < bp:
                break
            segment = i + 1

        # Use corresponding q and m for the segment
        q, m = self.q_list[segment], self.m_list[segment]
        if m != 0:
            S_corrected = 10 ** ((q - np.log10(Nf)) / m)
        else:
            S_corrected = 10 ** q
        S = S_corrected / (T_eff / 25) ** self.c
        return S

    def generate_points(self, T):
        """
        Generate stress-life points for the curve, including default and breakpoint values.

        Parameters:
        - T: Thickness of the plate (mm)

        Returns:
        - Nf_values, S_values: Arrays of fatigue life and stress range values
        """
        # Default Nf_values points
        Nf_values = [1e4, 1e9]
        T_eff = self.compute_teff(T)
        
        # Include breakpoints if specified
        if self.breakpoints:
            Nf_converted = []
            for i, breakpoint in enumerate(self.breakpoints):
                if self.breakpoints_S[i]:  # If it's a stress value, convert it to Nf
                    q, m = self.q_list[i], self.m_list[i]
                    log_Nf = q - m * np.log10(breakpoint)
                    Nf_converted.append(10 ** log_Nf)
                else:  # If it's an Nf value, directly add it to Nf_values
                    Nf_converted.append(breakpoint)
            Nf_values.extend(Nf_converted)
            Nf_values = sorted(Nf_values)  # Sort Nf_values in ascending order

        # Calculate corresponding stress values
        S_values = [self.calculate_stress(Nf, T) for Nf in Nf_values]
        return np.array(Nf_values), np.array(S_values)

# Functions to check the input of the user

def get_valid_integer(prompt, min_value=None, max_value=None):
    """
    Prompt the user for a valid integer input.

    Parameters:
    - prompt: The input prompt string
    - min_value: Minimum acceptable value (optional)
    - max_value: Maximum acceptable value (optional)

    Returns:
    - A valid integer
    """
    while True:
        try:
            value = int(input(prompt))
            if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                print(f"Please enter a value between {min_value} and {max_value}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")

def get_valid_float(prompt):
    """
    Prompt the user for a valid float input.

    Parameters:
    - prompt: The input prompt string

    Returns:
    - A valid float
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def get_valid_int_list(prompt, max_value=None):
    """
    Prompt the user for a list of integers separated by spaces.

    Parameters:
    - prompt: The input prompt string
    - max_value: Maximum acceptable value for each integer (optional)

    Returns:
    - A list of valid integers
    """
    while True:
        try:
            values = [int(x) for x in input(prompt).split()]
            if max_value is not None and any(x < 1 or x > max_value for x in values):
                print(f"Please enter numbers between 1 and {max_value}.")
                continue
            return values
        except ValueError:
            print("Invalid input. Please enter a series of integers separated by spaces.")

# S-N curve definitions

sn_curves = [
    SNCurve(name="DNV 2021 GF (C1) air",
            q_list=[12.449, 16.081], m_list=[3, 5], 
            c=0.1, breakpoints=[1e7], teff=True),
    SNCurve(name="DNV 2021 GF (C1) prot",
            q_list=[12.049, 16.081], m_list=[3, 5], 
            c=0.1, breakpoints=[1e6], teff=True),
    SNCurve(name="DNV 2021/2024 GF (C1) corr",
            q_list=[11.972], m_list=[3], 
            c=0.15, teff=True),
    SNCurve(name="DNV 2021 AW (D) air",
            q_list=[12.164, 15.606], m_list=[3, 5], 
            c=0.2, breakpoints=[1e7], teff=True),
    SNCurve(name="DNV 2021 AW (D) prot",
            q_list=[11.764, 15.606], m_list=[3, 5], 
            c=0.2, breakpoints=[1e6], teff=True),
    SNCurve(name="DNV 2021/2024 AW (D and wind turbine) corr",
            q_list=[11.687], m_list=[3], 
            c=0.2, teff=True),
    SNCurve(name="DNV 2024 GF (C1) air",
            q_list=[13.473, 16.377], m_list=[3.5, 5], 
            c=0.1, breakpoints=[5e6], teff=True),
    SNCurve(name="DNV 2024 GF (C1) prot",
            q_list=[13.264, 16.377], m_list=[3.5, 5], 
            c=0.1, breakpoints=[1e6], teff=True),
    SNCurve(name="DNV 2024 AW (wind turbine) air",
            q_list=[13.043, 17.325], m_list=[3.45, 5.7], 
            c=0.2, breakpoints=[3e6], teff=True),
    SNCurve(name="DNV 2024 AW (wind turbine) prot",
            q_list=[12.645, 17.325], m_list=[3.45, 5.7], 
            c=0.2, breakpoints=[3e5], teff=True),
    SNCurve(name="BS const GF (C) air",
            q_list=[np.log10(4.23e13), 1.8932], m_list=[3.5, 0], 
            c=0, breakpoints=[1e7]),
    SNCurve(name="BS var GF (C) air",
            q_list=[np.log10(4.23e13), np.log10(1.47e16)], m_list=[3.5, 5], 
            c=0, breakpoints=[5e7]),
    SNCurve(name="BS const GF (C) prot",
            q_list=[np.log10(1.69e13), np.log10(2.92e16), 1.89308], m_list=[3.5, 5, 0], 
            c=0, breakpoints=[144, 1e7], breakpoints_S=[True, False]),
    SNCurve(name="BS var GF (C) prot",
            q_list=[np.log10(1.69e13), np.log10(2.92e16), np.log10(4.23e13), np.log10(1.47e16)], m_list=[3.5, 5, 3.5, 5], 
            c=0, breakpoints=[144, 1e7, 5e7], breakpoints_S=[True, False, False]),
    SNCurve(name="BS const/var GF (C) corr",
            q_list=[np.log10(1.41e13)], m_list=[3.5], 
            c=0),
    SNCurve(name="BS const AW (D) air",
            q_list=[np.log10(1.52e12), 1.72728], m_list=[3, 0], 
            c=0.2, breakpoints=[1e7]),
    SNCurve(name="BS var AW (D) air",
            q_list=[np.log10(1.52e12), np.log10(1.48e15)], m_list=[3, 5], 
            c=0.2, breakpoints=[5e7]),
    SNCurve(name="BS const AW (D) prot",
            q_list=[np.log10(6.08e11), np.log10(4.33e15), 1.72728], m_list=[3, 5, 0], 
            c=0.2, breakpoints=[84, 1e7], breakpoints_S=[True, False]),
    SNCurve(name="BS var AW (D) prot",
            q_list=[np.log10(6.08e11), np.log10(4.33e15), np.log10(1.52e12), np.log10(1.48e15)], m_list=[3, 5, 3, 5], 
            c=0.2, breakpoints=[84, 1e7, 5e7], breakpoints_S=[True, False, False]),
    SNCurve(name="BS const/var AW (D) corr",
            q_list=[np.log10(5.07e11)], m_list=[3], 
            c=0.2),
    SNCurve(name="EC GF (112) air", 
            q_list=[12.449, 16.282, 1.656], m_list=[3, 5, 0], 
            c=0.2, breakpoints=[5e6, 1e8]),
    SNCurve(name="EC AW (90) air", 
            q_list=[12.164, 15.807, 1.561], m_list=[3, 5, 0], 
            c=0.2, breakpoints=[5e6, 1e8]),
    SNCurve(name="New AW air", 
            q_list=[12.786], m_list=[3.37], 
            c=0)
]

# S-N curves comparisons

curve_comp = [
    "DNV 2021 GF",
    "DNV 2021 AW",
    "DNV 2024 GF",
    "DNV 2024 AW",
    "BS const GF",
    "BS const AW",
    "BS var GF",
    "BS var AW",
    "EC GF",
    "EC AW",
    "GF air",
    "AW air",
    "GF prot",
    "AW prot",
    "GF corr",
    "AW corr"
]