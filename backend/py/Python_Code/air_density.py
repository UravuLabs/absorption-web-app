import math

def air_density(T, RH):
    """
    Computes moist air density (kg/m³)

    Inputs:
        T  - Dry bulb temperature (°C)
        RH - Relative humidity (%)  e.g., 50 for 50%

    Output:
        rho_air - Air density (kg/m³)
    """

    # Constants
    R_d = 287.058      # Gas constant for dry air (J/kg·K)
    R_v = 461.495      # Gas constant for water vapor (J/kg·K)

    # Convert
    T_k = T + 273.15
    RH_frac = RH / 100.0

    # Saturation vapor pressure (Magnus, Pa)
    p_ws = 610.94 * math.exp(17.625 * T / (T + 243.04))

    # Actual vapor pressure
    p_w = RH_frac * p_ws

    # Atmospheric pressure (Pa)
    p_atm = 101325

    # Partial pressure of dry air
    p_dry = p_atm - p_w

    # Moist air density
    rho_air = (p_dry / (R_d * T_k)) + (p_w / (R_v * T_k))

    return rho_air
