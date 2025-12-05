import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from absolute_humidity import absolute_humidity
from auto_select_cfm import auto_select_cfm

# ---------------------------------------------------------
# Step 1: Load Weather Data
# ---------------------------------------------------------
filename = r"C:\Users\DELL\AUS_WA.Perth.946100_IWEC.epw"

# EPW files have 8 header lines — skip 8, similar to MATLAB
weatherData = pd.read_csv(filename, skiprows=8, header=None, na_values=['9999', '999'])

start = 1
nData = 10

# MATLAB is 1-indexed, Python is 0-indexed
dbt = weatherData.iloc[start-1:nData, 6].values       # Var7
RH = weatherData.iloc[start-1:nData, 8].values / 100  # Var9
hours = np.arange(start, nData + 1)

# ---------------------------------------------------------
# Step 2: System Setup
# ---------------------------------------------------------
t_final = 60           # absorption duration per hour (minutes)
M_sol_initial = 500    # initial mass of solution

salts = ['CaCl2', 'LiCl', 'MgCl2', 'CaNO32']
x_salts = np.array([0.4, 0.0, 0.04, 0.12])
M_salts = M_sol_initial * x_salts

# ---------------------------------------------------------
# Step 3: Storage
# ---------------------------------------------------------
hourly_absorption = np.zeros(nData)
AH_values = np.zeros(nData)
cfm_used = np.zeros(nData)

print("\n--- Running 8760-hour Simulation with Auto CFM Selection ---\n")

# ---------------------------------------------------------
# Step 4: Run simulation for each hour
# ---------------------------------------------------------
for hr in range(start, nData + 1):
    idx = hr - 1

    T_a = dbt[idx]
    rh_a = RH[idx]

    # absolute humidity
    AH_values[idx] = absolute_humidity(T_a, rh_a * 100)

    # auto select CFM for this hour
    abs_hr, best_cfm = auto_select_cfm(T_a, rh_a,
                                       M_sol_initial, M_salts,
                                       salts, x_salts, t_final)

    hourly_absorption[idx] = abs_hr
    cfm_used[idx] = best_cfm

    print("Hour %4d | CFM = %5d | Absorbed = %.3f kg | AH = %.3f g/m3" %
          (hr, int(best_cfm), abs_hr, AH_values[idx]))

# ---------------------------------------------------------
# Step 5: Plot results
# ---------------------------------------------------------
plt.figure()
ax = plt.gca()
ax.plot(hours, hourly_absorption, 'b', linewidth=2, label='Water Absorption')
ax.set_ylabel('Water Absorbed (kg)')
ax.set_xlabel('Hour of Year')
ax.set_title('Hourly Water Absorption and Absolute Humidity')

ax2 = ax.twinx()
ax2.plot(hours, AH_values, 'r', linewidth=2, label='Absolute Humidity')
ax2.set_ylabel('Absolute Humidity (g/m³)')
ax.grid(True)
ax.legend(loc='upper left')

plt.figure()
plt.plot(hours, cfm_used, 'k', linewidth=2)
plt.xlabel('Hour of Year')
plt.ylabel('CFM Used')
plt.title('CFM Selection Profile')
plt.grid(True)

plt.show()
