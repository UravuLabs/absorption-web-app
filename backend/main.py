
from fastapi import FastAPI
import runpy, base64
import matplotlib.pyplot as plt
import io

app = FastAPI()

@app.post("/simulate")
def simulate(location: str, lpm: float, cfm: float):
    # sequential execution
    seq = [
        "svp_1.py","air_density.py","humrat.py","solution_density.py",
        "vapor_pressure_salts.py","dydx_gen1.py","absorption_step.py",
        "run_hour_simulation.py","lpm_from_cfm.py","auto_select_cfm.py",
        "absolute_humidity.py","main_absorption_simulation.py"
    ]
    globals_dict={}
    for f in seq:
        runpy.run_path(f, init_globals=globals_dict)

    # expect outputs in globals
    water = globals_dict.get("hourly_water_absorption")
    ah = globals_dict.get("absolute_humidity")

    # plot
    fig, ax1 = plt.subplots()
    ax1.plot(water)
    ax2 = ax1.twinx()
    ax2.plot(ah)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()

    return {"water": water, "ah": ah, "plot": img_b64}
