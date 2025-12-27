import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EPW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "epw_files")

# Map city names to EPW files
CITY_TO_EPW = {
    "Exmouth": "AUS_WA_Exmouth-RAAF.Learmonth.943020_TMYx.epw",
    "Kalgoorlie-Boulder": "AUS_WA_Kalgoorlie-Boulder.AP.946370_TMYx.2004-2018.epw",
    "Marble Bar": "AUS_WA_Marble.Bar.953170_TMYx.epw",
    "Port Hedland": "AUS_WA_Port.Hedland.Intl.AP.943120_TMYx.2004-2018.epw",
    "New Delhi": "IND_DL_New.Delhi-Safdarjung.AP.421820_TMYx.2004-2018.epw",
    "Bengaluru": "IND_KA_Bengaluru.432950_TMYx.epw",
    "Solapur": "IND_MH_Solapur.431170_TMYx.epw",
    "Perth": "AUS_WA.Perth.946100_IWEC.epw"
}

MASTER_DATASET = "master_absorption_dataset.csv"

MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

# Load master dataset
master_df = pd.read_csv(MASTER_DATASET)

@app.route("/")
def index():
    return render_template("index.html", cities=list(CITY_TO_EPW.keys()), months=list(MONTHS.keys()))

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    city = data.get("city")
    month_name = data.get("month")

    if city not in CITY_TO_EPW:
        return jsonify({"error": "Invalid city"}), 400
    if month_name not in MONTHS:
        return jsonify({"error": "Invalid month"}), 400

    month_num = MONTHS[month_name]
    epw_file = CITY_TO_EPW[city]
    epw_path = os.path.join(EPW_DIR, epw_file)

    if not os.path.exists(epw_path):
        return jsonify({"error": f"EPW file not found for city {city}"}), 400

    # Load EPW file
    epw = pd.read_csv(epw_path, skiprows=8, header=None)
    epw.columns = [
        "year", "month", "day", "hour", "minute", "data_source", "dry_bulb_C",
        "dew_point_C", "relative_humidity", "atmos_pressure", "extrater_horizontal_radiation",
        "extrater_direct_normal_radiation", "horz_infrared_radiation_intensity", "global_horizontal_radiation",
        "direct_normal_radiation", "diffuse_horizontal_radiation", "global_horizontal_illumination",
        "direct_normal_illumination", "diffuse_horizontal_illumination", "zenith_luminance",
        "wind_direction", "wind_speed", "total_sky_cover", "opaque_sky_cover", "visibility",
        "ceiling_height", "present_weather_observation", "present_weather_codes", "precipitable_water",
        "aerosol_optical_depth", "snow_depth", "days_since_last_snowfall", "albedo", "liquid_precipitation_depth",
        "liquid_precipitation_quantity"
    ]

    # Filter for selected month
    epw_month = epw[epw["month"] == month_num].copy()

    # Prepare arrays to store results
    water_absorbed_list = []
    selected_cfm_list = []

    # Map each hour's temperature & RH to closest row in master dataset
    for _, row in epw_month.iterrows():
        temp = row["dry_bulb_C"]
        rh = row["relative_humidity"]

        # Find closest row
        diffs = (master_df["T_C"] - temp).abs() + (master_df["RH_percent"] - rh).abs()
        closest_idx = diffs.idxmin()
        closest_row = master_df.loc[closest_idx]

        water_absorbed_list.append(closest_row["water_absorbed_kg_per_hr"])
        selected_cfm_list.append(closest_row["selected_cfm"])

    epw_month["water_absorbed_kg_per_hr"] = water_absorbed_list
    epw_month["selected_cfm"] = selected_cfm_list

    avg_temperature_C = epw_month["dry_bulb_C"].mean()
    avg_rh_percent = epw_month["relative_humidity"].mean()
    avg_water_absorbed_per_hr = epw_month["water_absorbed_kg_per_hr"].mean()
    monthly_water_absorbed = epw_month["water_absorbed_kg_per_hr"].sum()  # Sum over all hours

    output = {
        "avg_temperature_C": round(avg_temperature_C, 2),
        "avg_rh_percent": round(avg_rh_percent, 2),
        "water_absorbed_kg_per_hr": round(avg_water_absorbed_per_hr, 3),
        "monthly_water_absorbed": round(monthly_water_absorbed, 2),
        "selected_cfm": selected_cfm_list  # hourly
    }

    return jsonify(output)

if __name__ == "__main__":
    app.run(debug=True)