import numpy as np
from air_density import air_density
from lpm_from_cfm import lpm_from_cfm
from run_hour_simulation import run_hour_simulation

def auto_select_cfm(T_a, rh_a, M_sol_initial, M_salts, salts, x_salts, t_final):
    # CFM levels to try (MATLAB: 10000:1000:40000)
    cfm_list = np.arange(10000, 40001, 1000)

    # Default initialization
    best_cfm = int(cfm_list[0])
    total_abs = 0

    for cfm in cfm_list:
        rho_a_air = air_density(T_a, rh_a * 100)
        # Convert cfm → lpm
        lpm = lpm_from_cfm(int(cfm), 1.2, rho_a_air, 1380)

        # Run 1-hour simulation
        total_abs = run_hour_simulation(int(cfm), lpm,
                                        T_a, rh_a,
                                        M_sol_initial, M_salts,
                                        salts, x_salts, t_final)

        # ---------------------------
        # NEW CORRECT LOGIC
        # ---------------------------
        # CASE 1: Absorption >= 80 (includes >100)
        if total_abs >= 80:
            best_cfm = int(cfm)
            return total_abs, best_cfm

        # CASE 2: Absorption < 80 -> continue to next CFM
        best_cfm = int(cfm)

    # If reached here: return last results
    return total_abs, best_cfm
