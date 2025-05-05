# Weekend Flight Availability Checker

This project allows you to check the availability of direct weekend round trips (Friday-Sunday or Saturday-Monday) for wishlisted destinations over the next few months. It fetches flight data using the AviationStack API and checks for possible trips from a list of origin and destination airports in your wishlist. The results are aggregated and visualized using a bar chart.

## Features

- Loads a wishlist of flight routes (origin and destination) from a CSV file.
- Fetches flight data from the AviationStack API to check for direct flights.
- Filters available flights based on specific dates (Friday-Sunday or Saturday-Monday).
- Aggregates results and displays the number of trips available for each weekend.
- Visualizes the availability of trips with a bar chart showing the number of trips per weekend.

## Requirements

### Python Libraries
To run this project, you will need to install the following Python libraries:

- `pandas`: For data manipulation and CSV handling.
- `requests`: For making API requests to the AviationStack API.
- `matplotlib`: For visualizing flight availability as a bar chart.
- `json`: For reading the configuration file.
- `time`: For handling API request rate limits.

You can install the required libraries using `pip`:

### AviationStack API
For project to work, aviationStack API is needed. Create a new account or use existing one and 
copy API KEY from dashboard. `AviationStack API`is not fully free, so limitation might occur.

### Configuration
Project uses `config.json` file to set parameters. 

Format:
{
    "api_key": "YOUR_Key_Here",
    "wishlist_csv":"FileName or Path to file",
    "months_ahead": Number
}

there is also `_config.json` file that you can copy and rename to `config.json`, then fill your parameters.

### Run project
To run project simply run `flightChecker.py` file. Make sure all libraries are imported and configuration is set.

