import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from geopy.geocoders import Nominatim
from model.main_absorption_simulation import run_absorption_simulation
from services.weather import load_weather_by_location

# ---- FastAPI App ----
app = FastAPI(title="Water Absorption API", version="1.0.0")

# ---- CORS Middleware ----
origins = [
    "https://musical-jelly-d9a6cc.netlify.app",  # Netlify frontend
    "http://localhost:5173"  # optional for local testing
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Environment Token ----
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")  # set this on Render

# ---- Request Model ----
class SimulationRequest(BaseModel):
    location: str
    month: int  # 1-12
    cfm: float | None = None
    lpm: float | None = None
    auto_mode: bool = True
    M_sol_initial: float = 500.0
    t_final: int = 1

# ---- Geolocator ----
geolocator = Nominatim(user_agent="water_absorption_app")

# ---- Simulation Endpoint ----
@app.post("/simulate")
def simulate(
    req: SimulationRequest, 
    authorization: str = Header(None)
):
    # ---- Bearer Token Validation ----
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1]
    if token != API_BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Convert location to lat/lon
        loc = geolocator.geocode(req.location)
        if not loc:
            raise HTTPException(status_code=400, detail="Location not found")

        # Load weather data
        weather_df = load_weather_by_location(loc.latitude, loc.longitude)
        if weather_df.empty:
            raise HTTPException(status_code=400, detail="Weather data unavailable")

        # Run simulation
        results = run_absorption_simulation(
            weather_df=weather_df,
            M_sol_initial=req.M_sol_initial,
            t_final=req.t_final,
            user_cfm=req.cfm,
            user_lpm=req.lpm,
            auto_mode=req.auto_mode
        )

        hourly = np.array(results["hourly_absorption"])
        monthly = hourly.reshape(12, -1).sum(axis=1)

        return {
            "monthly_water_absorption": monthly.tolist(),
            "hourly_water_absorption": hourly.tolist(),
            "cfm_used": results["cfm_used"],
            "total_water_absorbed": results["total_water_absorbed"]
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
