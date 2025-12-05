import math

def svp_1(T):
    """
    Saturation vapor pressure using the Goff & Gratch Equation (1946)

    Input:
        T  - Temperature on Kelvin scale

    Output:
        SVP - Saturation vapor pressure (Pa)
    """

    # Standard reference values
    Ts = 373.15      # steam point temperature (K)
    Ps = 101324.6    # standard atmospheric pressure at steam point (Pa)

    log10SVP = (
        -7.90298 * (Ts / T - 1)
        + 5.02808 * math.log10(Ts / T)
        - 1.3816e-7 * (10 ** (11.344 * (1 - T / Ts)) - 1)
        + 8.1328e-3 * (10 ** (3.49149 * (1 - Ts / T)) - 1)
        + math.log10(Ps)
    )

    SVP = 10 ** (log10SVP)

    return SVP
