def lpm_from_cfm(CFM, LbyG, rho_air, rho_liq):
    """
    lpm_from_cfm  Calculates liquid flow rate (LPM) for given CFM and L/G ratio
    Inputs:
      CFM      - Airflow rate (ft³/min)
      LbyG     - Liquid-to-Gas mass ratio (dimensionless)
      rho_air  - Air density (kg/m³)
      rho_liq  - Liquid density (kg/m³)
    Output:
      Q_LPM    - Liquid flow rate (LPM)
    """
    # Convert air flow to m³/s
    Q_air = CFM * 0.000471947

    # Air mass flow rate (kg/s)
    m_air = rho_air * Q_air

    # Liquid mass flow rate (kg/s)
    m_liq = LbyG * m_air

    # Liquid volumetric flow rate (m³/s)
    Q_liq_m3s = m_liq / rho_liq

    # Convert to LPM
    Q_LPM = Q_liq_m3s * 1000.0 * 60.0

    # Display results
    print('Liquid Flow Rate = %.2f LPM' % Q_LPM)
    return Q_LPM
