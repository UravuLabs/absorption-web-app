import numpy as np
from solution_density import solution_density
from humrat import humrat
from svp_1 import svp_1

def vapor_pressure_salts(T_C, T_a, rh_a, salts, mass_fracs, p):
    """
    Vapor pressure calculation for multi-salt solution
    Returns: p_solution, p_v, w_sol, w_air, rho_sol
    """
    # ---------- Ion parameter table (ξ, α, β) ----------
    ionParams = {
        'Li': {'xi': 181.9875, 'alpha': -0.3409, 'beta': 0.0301},
        'Ca': {'xi': 363.7876, 'alpha': -0.6849, 'beta': 0.1039},
        'Cl': {'xi': -181.8698, 'alpha': 0.0639, 'beta': 0.0003},
        'Mg': {'xi': 363.6704, 'alpha': -0.6195, 'beta': 0.1039},
        'NO3': {'xi': -181.6861, 'alpha': 0.1082, 'beta': -0.0174},
    }

    # ---------- Salt dissociation & molar masses ----------
    saltData = {
        'LiCl': {'M': 42.39, 'ions': [('Li', 1), ('Cl', 1)]},
        'CaCl2': {'M': 110.98, 'ions': [('Ca', 1), ('Cl', 2)]},
        'MgCl2': {'M': 95.3, 'ions': [('Mg', 1), ('Cl', 2)]},
        'CaNO32': {'M': 164.088, 'ions': [('Ca', 1), ('NO3', 2)]},
    }

    # ---------- Step 1: Setup ----------
    T_K = T_C + 273.15
    mass_fracs = np.minimum(np.maximum(mass_fracs, 0.0), 0.999)
    massfrac_H2O = (1.0 - np.sum(mass_fracs))

    # ---------- Step 2: Molality for each ion ----------
    molality = {}
    for saltName, mf_salt in zip(salts, mass_fracs):
        saltInfo = saltData[saltName]
        # mol in 1 kg solution (1000 g basis)
        moles_salt = (mf_salt * p['M_sol'] * 1000.0) / saltInfo['M']

        for ionName, coeff in saltInfo['ions']:
            moles_ion = moles_salt * coeff
            kg_H2O = massfrac_H2O * p['M_sol']  # kg water
            # molality (mol/kg H2O)
            m_i = moles_ion / kg_H2O

            if ionName in molality:
                molality[ionName] = molality[ionName] + m_i
            else:
                molality[ionName] = m_i

    # ---------- Step 3: Compute sums ----------
    sum_xi_m = 0.0
    sum_alpha_beta = 0.0
    sum_m = 0.0

    for ion, m_i in molality.items():
        sum_m += m_i
        xi = ionParams[ion]['xi']
        alpha = ionParams[ion]['alpha']
        beta = ionParams[ion]['beta']

        sum_xi_m += xi * m_i
        sum_alpha_beta += (alpha * m_i**1.5 + beta * m_i**2)

    denominator = 1.0 + sum_xi_m
    temp_factor = (T_K / 273.15)**2
    ln_term = np.log(55.51 / (55.51 + sum_m))

    # ---------- Step 4: Pure water vapor pressure (Pa) ----------
    psat_w = (23.271 - (3879.198 / (T_K - 42.7356)))
    # Replace XSteam('psat_t',T_a)*1e5 with svp_1 (Pa)
    p_v = svp_1(T_a + 273.15)

    # ---------- Step 5: Solution vapor pressure ----------
    activity_term = ((1.0 / (denominator * temp_factor)) * (sum_alpha_beta))
    reduced_p = ((activity_term - 1.0) * ln_term)

    ln_p = psat_w - reduced_p
    p_solution = np.exp(ln_p)

    # Approximate solution humidity ratio (kg/kg dry air equivalent logic)
    P_kpa = (p_solution / 1000.0)

    # Use standard barometer 101.325 kPa (user comment in MATLAB suggests site-specific change)
    w_sol = (0.62198 * P_kpa / (101.325 - P_kpa))

    rho_sol = solution_density(T_C, salts, mass_fracs)

    w_air = humrat(rh_a, T_a + 273.15)

    return p_solution, p_v, w_sol, w_air, rho_sol
