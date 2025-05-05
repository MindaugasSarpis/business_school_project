import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Load credentials from .env file
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')

# Step 1: Get a fresh access token
def get_access_token():
    response = requests.post(
        url='https://www.strava.com/api/v3/oauth/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': REFRESH_TOKEN,
            'grant_type': 'refresh_token'
        }
    )
    return response.json()['access_token']

# Step 2: Fetch new activities only
def fetch_only_new_activities(access_token, known_ids):
    headers = {"Authorization": f"Bearer {access_token}"}
    activities = []
    page = 1
    per_page = 30
    stop_fetching = False

    while not stop_fetching:
        url = f"https://www.strava.com/api/v3/athlete/activities?page={page}&per_page={per_page}"
        response = requests.get(url, headers=headers)
        data = response.json()

        if not data:
            break

        for activity in data:
            if str(activity["id"]) in known_ids:
                stop_fetching = True
                break
            activities.append(activity)

        print(f"✅ Page {page} – {len(data)} activities")
        page += 1

    return activities

# Step 3: Main execution
if __name__ == "__main__":
    token = get_access_token()

    csv_path = "Data/strava_activities.csv"
    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
        known_ids = set(existing_df["id"].astype(str))
    else:
        existing_df = pd.DataFrame()
        known_ids = set()

    new_activities = fetch_only_new_activities(token, known_ids)

    if new_activities:
        new_df = pd.json_normalize(new_activities)
        combined_df = pd.concat([new_df, existing_df], ignore_index=True)
        combined_df.to_csv(csv_path, index=False)
        print(f"💾 Saved {len(new_activities)} new activities to {csv_path}")
    else:
        print("👋 No new activities found.")
