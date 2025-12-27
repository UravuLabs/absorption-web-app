
import numpy as np

def bilinear_interpolation(df, T, RH):
    temps = np.sort(df['T_C'].unique())
    rhs = np.sort(df['RH_percent'].unique())

    T1 = temps[temps <= T].max()
    T2 = temps[temps >= T].min()
    RH1 = rhs[rhs <= RH].max()
    RH2 = rhs[rhs >= RH].min()

    Q11 = df[(df.T_C == T1) & (df.RH_percent == RH1)].water_absorbed_kg_per_hr.values[0]
    Q12 = df[(df.T_C == T1) & (df.RH_percent == RH2)].water_absorbed_kg_per_hr.values[0]
    Q21 = df[(df.T_C == T2) & (df.RH_percent == RH1)].water_absorbed_kg_per_hr.values[0]
    Q22 = df[(df.T_C == T2) & (df.RH_percent == RH2)].water_absorbed_kg_per_hr.values[0]

    return (
        Q11 * (T2 - T) * (RH2 - RH) +
        Q21 * (T - T1) * (RH2 - RH) +
        Q12 * (T2 - T) * (RH - RH1) +
        Q22 * (T - T1) * (RH - RH1)
    ) / ((T2 - T1) * (RH2 - RH1))
