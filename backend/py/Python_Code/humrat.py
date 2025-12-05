from svp_1 import svp_1

def humrat(rh, t):
    """
    Humidity ratio W

    Inputs:
        rh - relative humidity (fraction, same as MATLAB input)
        t  - temperature in Kelvin

    Output:
        W - humidity ratio
    """

    p_sat = svp_1(t)
    p_v = rh * p_sat

    W = 0.62198 * (p_v) / (101325 - p_v)

    return W
