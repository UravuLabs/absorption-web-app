import numpy as np

def absolute_humidity(T, RH):
    """
    absolute_humidity  Calculates absolute humidity in g/m³
    Inputs:
      T  - Air temperature in °C
      RH - Relative humidity in %
    Output:
      AH - Absolute humidity in g/m³
    """
    # Step 1: Saturation vapor pressure (Magnus formula, hPa)
    P_sat = 6.112 * np.exp((17.67 * T) / (T + 243.5))

    # Step 2: Actual vapor pressure (hPa)
    P_v = (RH / 100.0) * P_sat

    # Step 3: Absolute humidity (g/m³)
    AH = (216.7 * P_v) / (T + 273.15)

    return AH
