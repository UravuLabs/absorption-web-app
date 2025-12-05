def solution_density(T_C, salts, mass_fracs):
    # Pure water density (kg/m³) using Kell's 1975 equation
    rho_w = 1000.0 * (1.0 - ((T_C + 288.9414) / (508929.2 * (T_C + 68.12963))) * (T_C - 3.9863)**2)

    # Salt-specific density increments at ~20°C (kg/m³ per unit mass fraction)
    density_increments = {
        'LiCl': 500.0,   # approx increment per 100% mass fraction
        'CaCl2': 800.0,
        'MgCl2': 750.0,
        'CaNO32': 600.0
    }

    # Adjust for temperature (simplified: density decreases ~0.25% per °C above 20°C)
    temp_factor = 1.0 - 0.00025 * (T_C - 20.0)

    # Add contributions
    delta_rho = 0.0
    for i, salt_name in enumerate(salts):
        if salt_name in density_increments:
            delta_rho += density_increments[salt_name] * mass_fracs[i]

    rho = rho_w + delta_rho * temp_factor
    return rho
