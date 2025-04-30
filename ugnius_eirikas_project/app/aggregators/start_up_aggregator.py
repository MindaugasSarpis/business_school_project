import os
import json
import aiohttp
from fastapi import HTTPException
import pandas as pd

from fastapi.encoders import jsonable_encoder
from datetime import datetime
from pyproj import Transformer

from app.environment import AGG_DATA_FILE, CAR_MAKERS, DATA_FOLDER, FILE_URL, INC_PER_MONTH_DATA_FILE, INCIDENTS_FILE, INTOXICATED_DRIVERS, INTOXICATED_DRIVERS_MONTH, MAP_DATA, STATS_FILE

# Ensure the data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

def filter_incidents(data):
    """Filter out incidents that occurred before 2023."""
    filtered_data = [incident for incident in data if datetime.strptime(incident["dataLaikas"], "%Y-%m-%d %H:%M").year >= 2023]
    return filtered_data

async def download_data():
    """Download the incidents JSON file if it doesn't exist and filter data."""
    if not os.path.exists(INCIDENTS_FILE):
        print("Data file not found. Downloading...")
        async with aiohttp.ClientSession() as session:
            async with session.get(FILE_URL) as response:
                if response.status == 200:
                    raw_data = await response.text()
                    try:
                        data = json.loads(raw_data)
                        filtered_data = filter_incidents(data)
                        
                        with open(INCIDENTS_FILE, "w", encoding="utf-8") as f:
                            json.dump(filtered_data, f, indent=2, ensure_ascii=False)
                        
                        print(f"Data file downloaded and filtered successfully. {len(filtered_data)} incidents retained.")
                    except json.JSONDecodeError:
                        print("Failed to parse JSON data.")
                else:
                    print(f"Failed to download data. Status code: {response.status}")


def check_file_exists(file_path):
    """Check if a file exists."""
    if not os.path.exists(INCIDENTS_FILE):
        print(f"Error: {INCIDENTS_FILE} not found")
        return

def compute_stats():
    """Compute and save accident statistics."""
    check_file_exists(INCIDENTS_FILE)
    try:
        df = pd.read_json(INCIDENTS_FILE)
        # Ensure required columns exist
        if "zuvusiuSkaicius" not in df.columns or "suzeistuSkaicius" not in df.columns:
            print("Error: Required columns not found in data")
            return
        total_deaths = int(df["zuvusiuSkaicius"].sum())
        total_injured = int(df["suzeistuSkaicius"].sum())
        total_accidents = len(df)
        total_hit_run = 0
        if "eismoDalyviai" in df.columns:
            for driver_list in df["eismoDalyviai"].dropna():
                for driver in driver_list:
                    if isinstance(driver, dict) and driver.get("kategorija") == "Automobilio vairuotojas":
                        if driver.get("pasisalino") == "Taip":
                            total_hit_run += 1
        stats = {
            "data": [
                {"statistic": "Total deaths", "value": total_deaths},
                {"statistic": "Total injured", "value": total_injured},
                {"statistic": "Total accidents", "value": total_accidents},
                {"statistic": "Total hit and run accidents", "value": total_hit_run},
            ]
        }
        # Save statistics to JSON file
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)
        print("Statistics calculated and saved.")
    except Exception as e:
        print(f"Error calculating statistics: {e}")

def aggregate_line_chart():
    """Return data for two line charts: total accidents and total deaths, and save to a file."""
    check_file_exists(INCIDENTS_FILE)

    try:
        # Load the data
        df = pd.read_json(INCIDENTS_FILE)

        # Ensure 'dataLaikas' is in datetime format
        df['dataLaikas'] = pd.to_datetime(df['dataLaikas'], errors='coerce')

        # Sort by 'dataLaikas'
        df = df.sort_values(by='dataLaikas')

        # Group by date
        df['date'] = df['dataLaikas'].dt.date
        accidents_by_date = df.groupby('date').size()  # Total accidents per day
        deaths_by_date = df.groupby('date')['zuvusiuSkaicius'].sum()  # Total deaths per day

        # Prepare the data for the charts
        accidents_data = accidents_by_date.reset_index(name='total_accidents')
        deaths_data = deaths_by_date.reset_index(name='total_deaths')

        # Convert to list of dicts (for easy JSON formatting)
        accidents_list = accidents_data.to_dict(orient='records')
        deaths_list = deaths_data.to_dict(orient='records')
  
        # Save aggregated data to JSON file
        aggregated_data = jsonable_encoder({
            "accidents": accidents_list,
            "deaths": deaths_list
        })
            
        with open(AGG_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(aggregated_data, f, indent=4, ensure_ascii=False)

        print("Aggregated data saved successfully.")

    except Exception as e:
        print(f"Error in aggregate_line_chart: {e}")

def aggregate_accidents_by_month():
    """Return data for two line charts: total accidents and total deaths, and save to a file."""
    check_file_exists(INCIDENTS_FILE)
    try:
        # Load the data
        df = pd.read_json(INCIDENTS_FILE)

        # Ensure 'dataLaikas' is a datetime column
        df['dataLaikas'] = pd.to_datetime(df['dataLaikas'], errors='coerce')

        # Filter out rows with invalid or missing 'dataLaikas'
        df = df.dropna(subset=['dataLaikas'])

        # Group by year and month, then count the number of accidents
        df['year_month'] = df['dataLaikas'].dt.to_period('M')  # Create a period column for Year-Month
        accidents_per_month = df.groupby('year_month').size()  # Count accidents per month

        # Convert the period to a string for easier handling in the response
        accidents_per_month = accidents_per_month.reset_index(name='total_accidents')
        accidents_per_month['year_month'] = accidents_per_month['year_month'].astype(str)
        # accidents_per_month =(accidents_per_month.to_dict(orient='records'))

        deaths_per_month = df.groupby('year_month')['zuvusiuSkaicius'].sum()  # Sum deaths per month
        # Convert the period to a string for easier handling in the response
        deaths_per_month = deaths_per_month.reset_index(name='total_deaths')
        deaths_per_month['year_month'] = deaths_per_month['year_month'].astype(str)
        data =jsonable_encoder( {
            "accidents": accidents_per_month.to_dict(orient='records'),
            "deaths": deaths_per_month.to_dict(orient='records')
        })
        with open(INC_PER_MONTH_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Aggregated data saved successfully.")
    except Exception as e:
        print(f"Error in aggregate_line_chart: {e}")

def aggregate_car_types():
    """Return data for two line charts: total accidents and total deaths, and save to a file."""
    check_file_exists(INCIDENTS_FILE)

    try:
        # Load the data
        df = pd.read_json(INCIDENTS_FILE)

        # Ensure 'eismoTranspPreimone' is a list and extract the 'marke' for each entry
        df['marke'] = df['eismoTranspPreimone'].apply(lambda x: x[0]['marke'] if isinstance(x, list) and len(x) > 0 else None)

        # Group by car brand ('marke') and calculate total accidents and total deaths
        car_types_accidents = df.groupby('marke').size()  # Total accidents per car brand
        car_types_deaths = df.groupby('marke')['zuvusiuSkaicius'].sum()  # Total deaths per car brand

        # Filter out items with total accidents or total deaths equal to 0
        car_types_accidents = car_types_accidents[car_types_accidents > 0]
        car_types_deaths = car_types_deaths[car_types_deaths > 0]

        # Get top 10 accidents and deaths
        accidents_top = car_types_accidents.nlargest(10)  # Top 10 accidents
        deaths_top = car_types_deaths.nlargest(10)  # Top 10 deaths

        # Prepare the data for the response
        car_types_data =  {
            "accidents": car_types_accidents.reset_index(name='total_accidents').to_dict(orient='records'),
            "deaths": car_types_deaths.reset_index(name='total_deaths').to_dict(orient='records'),
            "accidents_top": accidents_top.reset_index(name='total_accidents').to_dict(orient='records'),
            "deaths_top": deaths_top.reset_index(name='total_deaths').to_dict(orient='records')
        }
        with open(CAR_MAKERS, "w", encoding="utf-8") as f:
            json.dump(car_types_data, f, indent=4, ensure_ascii=False)
        print("Aggregated data saved successfully.")
        
    except Exception as e:
        print(f"Error in aggregate_line_chart: {e}")
    
def aggregate_intoxicated_drivers():
    """Return data for two line charts: total accidents and total deaths, and save to a file."""
    check_file_exists(INCIDENTS_FILE)
    try:
        # Load the data
        df = pd.read_json(INCIDENTS_FILE)

        # Extract 'busena' for automobile drivers
        df['bukle'] = df['eismoDalyviai'].apply(lambda x: [
            driver['busena'] for driver in x
            if isinstance(driver, dict) and driver.get('kategorija') == "Automobilio vairuotojas" and 'busena' in driver
        ] if isinstance(x, list) else [])

        # Flatten the list safely
        intoxicated_drivers = [item for sublist in df['bukle'] if isinstance(sublist, list) for item in sublist]

        # Count the number of intoxicated drivers
        intoxicated_drivers_count = pd.Series(intoxicated_drivers).value_counts()

        # Prepare the data for saving
        intoxicated_data = intoxicated_drivers_count.reset_index()
        intoxicated_data.columns = ['condition', 'count']

        # Save to a file
        with open(INTOXICATED_DRIVERS, "w", encoding="utf-8") as f:
            intoxicated_data.to_json(f, orient="records", indent=4, force_ascii=False)

        print("Aggregated data for intoxicated drivers saved successfully.")

    except Exception as e:
        print(f"Error in aggregate intoxicated drivers: {e}")
def aggregate_intoxicated_drivers_by_month():
    """Return data for two line charts: total accidents and total deaths, and save to a file."""
    check_file_exists(INCIDENTS_FILE)
    try:
        # Load the data
        df = pd.read_json(INCIDENTS_FILE)

        # Ensure 'dataLaikas' is in datetime format
        df['dataLaikas'] = pd.to_datetime(df['dataLaikas'], errors='coerce')

        # Filter out invalid/missing dates
        df = df.dropna(subset=['dataLaikas'])

        # Extract 'busena' only for 'Automobilio vairuotojas'
        records = []
        for _, row in df.iterrows():
            year_month = row['dataLaikas'].strftime('%Y-%m')  # Format as YYYY-MM
            for driver in row['eismoDalyviai']:
                if isinstance(driver, dict) and driver.get('kategorija') == "Automobilio vairuotojas":
                    condition = driver.get('busena', "Nežinoma")  # Default to "Nežinoma" if missing
                    is_sober = 1 if condition == "Blaivus" else 0  # 1 if sober
                    is_intoxicated = 1 - is_sober  # 1 if intoxicated
                    records.append({'year_month': year_month, 'sober': is_sober, 'intoxicated': is_intoxicated})

        # Convert to DataFrame
        intoxicated_df = pd.DataFrame(records)
        if intoxicated_df.empty:
            return jsonable_encoder(([]))  # Return an empty list if no data is available
        # Aggregate the counts per month
        summary = intoxicated_df.groupby('year_month').sum().reset_index()
        # Rename columns for clarity
        summary = summary.rename(columns={'year_month': 'time', 'sober': 'sober_count', 'intoxicated': 'intoxicated_count'})

        
        with open(INTOXICATED_DRIVERS_MONTH, "w", encoding="utf-8") as f:
            summary.to_json(f, orient="records", indent=4, force_ascii=False)
        print("Aggregated data for intoxicated drivers saved successfully.")

    except Exception as e:
        print(f"Error in aggregate intoxicated drivers by month: {e}")


def transform_lks94_to_wgs84(x: float, y: float):
    """Transforms LKS94 coordinates to WGS84."""
    transformer = Transformer.from_crs("EPSG:3346", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lat, lon


def load_json(filename: str):
    filepath = os.path.join(filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def aggregate_map_data():
    """Reads aggregated JSON and extracts necessary properties, transforming coordinates."""
    try:
        raw_data = load_json(INCIDENTS_FILE)  # Assuming raw incidents file exists
        df = pd.DataFrame(raw_data)

        # Ensure 'dataLaikas' is in datetime format
        df["dataLaikas"] = pd.to_datetime(df["dataLaikas"], errors="coerce")
        df = df.dropna(subset=["dataLaikas"])  # Remove invalid dates

        # Transform coordinates
        df[["lat", "lon"]] = df.apply(
            lambda row: transform_lks94_to_wgs84(float(row["platuma"]), float(row["ilguma"])),
            axis=1, result_type="expand"
        )

        # Select only required columns
        aggregated_data = df[[
            "dataLaikas", "dalyviuSkaicius", "zuvusiuSkaicius", "suzeistuSkaicius", "tpSkaicius",
            "savivaldybe", "gatve", "leistinasGreitis", "lat", "lon"
        ]].copy()
        aggregated_data["namas"] = df.get("namas", "")  # Include 'namas' if available

        # Save aggregated data
        aggregated_data.to_json(MAP_DATA, orient="records", indent=4, force_ascii=False)
        print("Map data aggregated and saved successfully.")
    except Exception as e:
        print(f"Error in aggregating map data: {e}")

  
  
  