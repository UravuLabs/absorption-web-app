import numpy as np
from vapor_pressure_salts import vapor_pressure_salts
from absorption_step import absorption_step

def run_hour_simulation(cfm, lpm,
                        T_a, rh_a,
                        M_sol_initial, M_salts, salts, x_salts, t_final):

    dt = 1
    time_steps = int(t_final * 60)

    M_sol = M_sol_initial
    water_vec = np.zeros(time_steps)
    T_s = T_a + 2

    for t in range(time_steps):
        total_x = np.sum(M_salts) / M_sol
        # p used as struct in MATLAB, use dict here
        p = {'M_sol': M_sol}

        p_sol, p_v, w_sol, w_air, rho_sol = vapor_pressure_salts(
            T_s, T_a, rh_a, salts, x_salts, p)

        water_abs = absorption_step(cfm, lpm, rho_sol, total_x,
                                    T_a, rh_a, T_s, salts, M_salts, p)

        if water_abs < 0:
            water_abs = 0

        water_vec[t] = water_abs
        M_sol = M_sol + water_abs

    total_abs = np.sum(water_vec)

    return total_abs
