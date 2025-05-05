import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from collections import defaultdict
import matplotlib.pyplot as plt
import json

# --- Configuration ---
# Load the JSON config file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

API_KEY= config['api_key']
WISHLIST_CSV= config['wishlist_csv']
MONTHS_AHEAD = config['months_ahead']
BASE_URL = "http://api.aviationstack.com/v1/flights" 

REQUEST_DELAY = 0.5 # Delay between API requests in seconds (respect API rate limits)

# --- Helper Functions ---

def get_flights(api_key, base_url, dep_iata, arr_iata, flight_date):

    params = {
        'access_key': api_key,
        'dep_iata': dep_iata,
        'arr_iata': arr_iata,
        'flight_date': flight_date,
    }
    try:
        print(f"Requesting: {dep_iata} -> {arr_iata} on {flight_date}")
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        flights = data.get('data', [])

        direct_flights = [
            f for f in flights
            if f.get('flight', {}).get('stops', 0) == 0
            and f.get('flight_status') == 'scheduled'
        ]

        print(f"Found {len(direct_flights)} direct flights.")
        time.sleep(REQUEST_DELAY) # Be respectful of API rate limits
        return direct_flights
    except requests.exceptions.RequestException as e:
        print(f"API Request failed for {dep_iata}->{arr_iata} on {flight_date}: {e}")
        # Handle specific errors like rate limits if needed
        if response.status_code == 429: # Too Many Requests
             print("Rate limit likely hit. Consider increasing REQUEST_DELAY.")
        time.sleep(REQUEST_DELAY) # Still delay even on error
        return []
    except Exception as e:
        print(f"An error occurred processing {dep_iata}->{arr_iata} on {flight_date}: {e}")
        return []


def find_weekend_trips(api_key, base_url, origin, destination, start_date, end_date):

    possible_trips = []
    current_date = start_date
    while current_date <= end_date:
        # Check for Fri-Sun pattern
        if current_date.weekday() == 4: # Friday
            departure_date = current_date
            return_date = current_date + timedelta(days=2)
            if return_date <= end_date:
                # Check outbound flight on Friday
                outbound_flights = get_flights(api_key, base_url, origin, destination, departure_date.strftime('%Y-%m-%d'))
                if outbound_flights:
                    # Check inbound flight on Sunday
                    inbound_flights = get_flights(api_key, base_url, destination, origin, return_date.strftime('%Y-%m-%d'))
                    if inbound_flights:
                        possible_trips.append((departure_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d')))

        # Check for Sat-Mon pattern
        elif current_date.weekday() == 5: # Saturday
            departure_date = current_date
            return_date = current_date + timedelta(days=2)
            if return_date <= end_date:
                 # Check outbound flight on Saturday
                outbound_flights = get_flights(api_key, base_url, origin, destination, departure_date.strftime('%Y-%m-%d'))
                if outbound_flights:
                    # Check inbound flight on Monday
                    inbound_flights = get_flights(api_key, base_url, destination, origin, return_date.strftime('%Y-%m-%d'))
                    if inbound_flights:
                        possible_trips.append((departure_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d')))

        current_date += timedelta(days=1) # Move to the next day
    return possible_trips

# --- Main Execution ---

# 1. Load Wishlist
try:
    wishlist_df = pd.read_csv(WISHLIST_CSV)
except FileNotFoundError:
    print(f"Error: CSV file not found at {WISHLIST_CSV}")
except ValueError as ve:
     print(f"CSV format error: {ve}")
except Exception as e:
    print(f"An error occurred during CSV processing: {e}")

# 2. Define Date Range
start_date = datetime.now().date()
end_date = (datetime.now() + timedelta(days=MONTHS_AHEAD * 30)).date()
print(f"\nChecking flights from {start_date} to {end_date}")

# 3. Find Trips and Aggregate Results
weekend_trip_counts = defaultdict(int)

if not wishlist_df.empty:
    for index, row in wishlist_df.iterrows():
        origin = row['Origin'].strip().upper()
        destination = row['Destination'].strip().upper()
        print(f"\n--- Checking Route: {origin} -> {destination} ---")
        trips = find_weekend_trips(API_KEY, BASE_URL, origin, destination, start_date, end_date)

        if trips:
            print(f"Found {len(trips)} possible weekend round trips for {origin}<->{destination}:")
            for dep_date_str, ret_date_str in trips:
                print(f"  - Depart: {dep_date_str}, Return: {ret_date_str}")
                # Aggregate by departure weekend start date (Friday or Saturday)
                dep_date_obj = datetime.strptime(dep_date_str, '%Y-%m-%d').date()
                day_name = dep_date_obj.strftime('%a')
                weekend_key = f"{dep_date_str} ({day_name})"
                weekend_trip_counts[weekend_key] += 1
        else:
            print(f"No direct weekend round trips found for {origin}<->{destination} in the date range.")
else:
    print("\nWishlist is empty. No routes to check.")


# 4. Analyze and Plot Results
if weekend_trip_counts:
    print("\n--- Overall Weekend Trip Availability ---")
    # Sort weekends by date
    sorted_weekends = sorted(weekend_trip_counts.items(), key=lambda item: datetime.strptime(item[0].split(' ')[0], '%Y-%m-%d'))

    weekend_labels = [item[0] for item in sorted_weekends]
    trip_counts = [item[1] for item in sorted_weekends]

    # Print summary
    for label, count in sorted_weekends:
        print(f"{label}: {count} possible route(s)")


    # Create Bar Chart
    plt.figure(figsize=(15, 7)) # Adjust figure size as needed
    bars = plt.bar(weekend_labels, trip_counts)
    plt.xlabel("Weekend Start Date (Fri/Sat)")
    plt.ylabel("Number of Possible Wishlist Trips")
    plt.title(f"Direct Weekend Flight Availability ({start_date} to {end_date})")
    plt.xticks(rotation=75, ha='right') # Rotate labels for better readability
    plt.tight_layout() # Adjust layout to prevent labels overlapping

    # Add counts above bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom', ha='center') # va: vertical alignment

    # Save the plot to a file
    plot_filename = 'weekend_flight_availability.png'
    plt.savefig(plot_filename)
    print(f"\nChart saved as {plot_filename}")

    # Display the plot (optional)
    plt.show()

else:
    print("\nNo possible weekend trips found for any route in the wishlist.")

print("\nScript finished.")