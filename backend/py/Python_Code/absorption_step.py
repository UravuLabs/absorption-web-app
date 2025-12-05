import numpy as np
from dydx_gen1 import dydx_gen1
from vapor_pressure_salts import vapor_pressure_salts
from humrat import humrat
from svp_1 import svp_1

def absorption_step(cfm, lpm, rho_sol, x_total, T_a, rh_a, T_s, salts, M_salts, p):

    # Air density (approx)
    rho_a = 1.164  # kg/m³

    # Geometry
    n_sides = 2
    B_c = n_sides * 0.3175
    H_c = 2.0
    L_c = 2.0
    A_a = H_c * B_c       # Air cross-section m²
    A_s = L_c * B_c       # Solution cross-section m²
    A_t = 300.0           # Specific surface area m²/m³
    N_rack = 1.0
    M_w = 18.02           # kg/kmol

    # Air-side mass flow and flux
    m_a = cfm * 0.02832 / 60.0 * rho_a  # kg/s
    G_a = m_a / (A_a * N_rack)

    # Solution-side mass flow and flux
    m_s_i = rho_sol * lpm / (1000.0 * 60.0)  # kg/s
    G_s = m_s_i / (A_s * N_rack)

    # Mass transfer coefficients (whole solution correlation)
    k_s = (0.042 * G_s**0.63 * np.exp(-0.00115 * T_s) * np.exp(0.0064 * x_total) * G_a**0.074) * M_w / A_t
    k_a = (0.142 * G_s**0.2 * np.exp(0.00088 * T_a) * G_a**0.71) * M_w / A_t

    # Onda effective area
    mu_s = 0.009  # Pa·s
    sigma_s = 0.072
    sigma_c = 0.033
    d_p = 1.0 / (A_t * L_c * A_a)
    v_s = G_s / rho_sol
    Re_s = rho_sol * v_s * d_p / mu_s
    Fr_s = v_s / np.sqrt(9.81 * d_p)
    We_s = rho_sol * d_p * v_s**2 / sigma_s
    A_p = A_t * L_c * A_a
    A_e = N_rack * A_p * (1.0 - np.exp(-1.45 * (sigma_c / sigma_s)**0.75 * Re_s**0.1 * Fr_s**-0.05 * We_s**0.2))

    # Inlet air humidity ratio
    p_v_sat = svp_1(T_a + 273.15) * rh_a
    P_kpa3 = p_v_sat / 1000.0
    w_a = humrat(rh_a, T_a + 273.16)  # kg water/kg dry air

    y_a_i = w_a / (1.0 + w_a)

    # Iteration parameters
    tolerance = 1e-2
    error = 0.2
    x_o_guess = x_total

    # Relative proportion of each salt
    M_salts_ratio = M_salts / np.sum(M_salts)

    while error > tolerance:
        # Average concentration
        x_avg = (x_total + x_o_guess) / 2.0

        # Current salt mass fractions (each salt)
        mass_fracs_current = x_avg * M_salts_ratio

        # Equilibrium slope
        slope = dydx_gen1(x_avg, T_s, T_a, rh_a, salts, M_salts_ratio, p)

        # Overall mass transfer coefficient
        ko_a = 1.0 / (1.0 / k_a + slope / k_s)

        # Film humidity ratio from new model
        p_sat_des, p_sat_a, w_film, _, _ = vapor_pressure_salts(T_s, T_a, rh_a, salts, mass_fracs_current, p)
        y_film = w_film  # already in kg/kg

        # Vapor absorbed
        m_v = ko_a * A_e * (y_a_i - y_film)

        # Update outlet concentration
        m_s_out = m_s_i + m_v
        x_o_new = (x_total * m_s_i) / m_s_out

        error = abs(x_o_new - x_o_guess)
        x_o_guess = x_o_new

    # Final water absorbed
    water_absorbed = m_v
    return water_absorbed
