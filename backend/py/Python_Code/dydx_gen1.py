import numpy as np
from vapor_pressure_salts import vapor_pressure_salts

def dydx_gen1(x_g, T_s, T_a, rh_a, salts, M_salts_ratio, p):
    # Computes slope dy/dx for multi-salt solutions
    delta = 0.001  # perturbation step

    mass_fracs_left = np.maximum(x_g - delta, 0.0) * M_salts_ratio
    mass_fracs_right = np.maximum(x_g + delta, 0.0) * M_salts_ratio

    _, _, w_left, _, _ = vapor_pressure_salts(T_s, T_a, rh_a, salts, mass_fracs_left, p)
    _, _, w_right, _, _ = vapor_pressure_salts(T_s, T_a, rh_a, salts, mass_fracs_right, p)

    y_left = w_left / (1.0 + w_left)
    y_right = w_right / (1.0 + w_right)

    # Slope calculation (kept sign consistent with MATLAB variant)
    slope = (y_right - y_left) / (-2.0 * delta)
    return slope
