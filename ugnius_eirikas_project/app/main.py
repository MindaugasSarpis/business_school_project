import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from aggregators.start_up_aggregator import aggregate_accidents_by_month, aggregate_car_types, aggregate_intoxicated_drivers, aggregate_intoxicated_drivers_by_month, aggregate_line_chart, aggregate_map_data, compute_stats, download_data
from environment import CAR_MAKERS, DATA_FOLDER, INC_PER_MONTH_DATA_FILE, INTOXICATED_DRIVERS_MONTH, MAP_DATA, STATS_FILE
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ensure the data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)



@app.on_event("startup")
async def startup_event():
    """Run tasks before FastAPI starts."""
import logging
logging.basicConfig(level=logging.INFO)

@app.on_event("startup")
async def startup_event():
    logging.info("Startup: downloading data...")
    await download_data()
    logging.info("Startup: computing stats...")
    compute_stats()
    logging.info("Startup: aggregating line chart...")
    aggregate_line_chart()
    logging.info("Startup: aggregating accidents by month...")
    aggregate_accidents_by_month()
    logging.info("Startup: aggregating car types...")
    aggregate_car_types()
    logging.info("Startup: aggregating intoxicated drivers...")
    aggregate_intoxicated_drivers()
    logging.info("Startup: aggregating intoxicated drivers by month...")
    aggregate_intoxicated_drivers_by_month()
    logging.info("Startup: aggregating map data...")
    aggregate_map_data()
    logging.info("Startup: done!")


def load_json(filename: str):
    filepath = os.path.join(filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/")
def read_root():
    return {"message": "Traffic incidents API is running"}

@app.get("/api/stats")
def get_stats():
    """Returns aggregated map data from precomputed JSON."""
    return JSONResponse(content=load_json(STATS_FILE))

@app.get("/api/accidents_by_month")
def get_accidents_by_month():
    """Returns aggregated incidents per month from precomputed JSON."""
    return JSONResponse(content=load_json(INC_PER_MONTH_DATA_FILE))

@app.get("/api/carType")
def get_car_types():
    """Returns aggregated incidents per month from precomputed JSON."""
    return JSONResponse(content=load_json(CAR_MAKERS))

@app.get("/api/intoxicatedDrivers")
def get_intoxicated_drivers():
    """Returns aggregated incidents per month from precomputed JSON."""
    return JSONResponse(content=load_json(INTOXICATED_DRIVERS_MONTH))

@app.get("/api/mapData")
def get_intoxicated_drivers():
    """Returns aggregated incidents per month from precomputed JSON."""
    return JSONResponse(content=load_json(MAP_DATA))

