import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Load credentials
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

# Step 1: Get fresh access token
def get_access_token():
    response = requests.post(
        url="https://www.strava.com/api/v3/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
    )
    return response.json()["access_token"]

# Step 2: Fetch all activities
def fetch_all_activities(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    activities = []
    page = 1
    per_page = 30

    while True:
        url = f"https://www.strava.com/api/v3/athlete/activities?page={page}&per_page={per_page}"
        response = requests.get(url, headers=headers)
        data = response.json()

        if not data:
            break

        activities.extend(data)
        print(f"Fetched page {page} with {len(data)} activities.")
        page += 1

    return activities

# Step 3: Merge with existing file and keep only unique
def save_new_activities(new_data, path="Data/strava_activities.csv"):
    new_df = pd.json_normalize(new_data)

    # Read existing
    if os.path.exists(path):
        old_df = pd.read_csv(path)
        combined = pd.concat([new_df, old_df]).drop_duplicates(subset="id", keep="first")
    else:
        combined = new_df

    # Sort newest first
    combined["start_date"] = pd.to_datetime(combined["start_date"])
    combined = combined.sort_values("start_date", ascending=False)

    # Write fresh file
    combined.to_csv(path, index=False)
    print(f"✅ Saved updated activities to {path}")

# Run the full sync
if __name__ == "__main__":
    token = get_access_token()
    activities = fetch_all_activities(token)
    save_new_activities(activities)
