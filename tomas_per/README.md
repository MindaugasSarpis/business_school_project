# Investment Information Collection

The primary goal of this project is to automatically fetch current investment position data from the Trading 212 platform and store it historically in an InfluxDB time-series database.

## Workflow

1.  **Configuration Loading:**
    The app uses `pydantic-settings` to load configuration from environment variables or a .env file. This includes API keys and specific endpoints for Trading212 and InfluxDB.

2.  **Fetching Data from Trading 212:**
    An `httpx` client is automatically configured with the correct Trading 212 API URL and authentication (using the `Trading212APIKeyAuth` class and the API key from `settings.py`) and an HTTP GET request is made to the configured Trading 212 API endpoint to retrieve the user's current open positions.

3.  **Data Validation and Structuring:**
    On success, the JSON response is parsed using a Pydantic TypeAdapter. During this process, Pydantic ensures the data conforms to the expected types (float, str, datetime), handles alias mapping (e.g., "ppl" to profit), validates the ticker format, and computes derived fields like current_value.

4.  **Data Transformation for InfluxDB:**
    * The workflow iterates through the list of validated `Position` objects obtained from the previous step.
    * For each `Position` object, the `to_point()` method (defined within the `Position` model in `schema.py`) is called.
    * This method transforms the position data into an InfluxDB `Point` object. It tags the data point with the stock `ticker` and includes fields such as `current_price`, `average_price`, `quantity`, `profit`, `forex_movement_impact`, and the calculated `current_value`. A timestamp (UTC by default) is associated with each point.

5.  **Writing Data to InfluxDB:**
    * The generated list of InfluxDB `Point` objects is passed to the `push_data_to_influxdb` function in `influxdb.py`.
    * This function first obtains an InfluxDB client instance using `get_influxdb_client`, configured with the connection details from `settings.py`.
    * It then uses the client's synchronous write API to send the list of points to the InfluxDB bucket specified in the settings (`influxdb_settings.stocks_bucket_name`).


## Overall Purpose and Execution

This entire sequence constitutes a data pipeline designed for automated portfolio tracking. By running this workflow periodically, a user can build a historical record of their Trading 212 positions in InfluxDB. This time-series data can then be used for:

* Monitoring portfolio value over time.
* Analyzing the performance of individual assets.
* Creating dashboards to visualize portfolio trends.
* Calculating historical profit/loss metrics.

A typical execution would involve a main script (not provided) that imports and calls `get_open_positions` and `push_data_to_influxdb` in sequence, potentially wrapped in a main execution block or a dedicated function triggered by a scheduler.

## Requirements
* Python 3.12 or higher
* uv package manager
* [InfluxDB](https://docs.influxdata.com/influxdb/v2/install/)
* Docker (Optional)

## How to run

1. **Clone the Repository**

```bash
git clone <repository-url>
cd stock-info-collection
```

2. **Run in container (Optional)**
If you have Docker and the Devcontainer extension installed, you can run this project in a container. A popup should appear prompting you to reopen folder in container. This can be done in VS Code's command menu as well (Ctrl+Shift+P).

3. **Set Up the Environment by installing dependencies**

```bash
uv sync
```

3. **Configure environment variables**
Create a .env file in the project root (or use the provided sample.env as a template). Edit the .env file to include your Trading 212 and InfluxDB credentials.

4. **Run the Script**

```bash
uv run python main.py
```

5. **Run Tests (Optional)**
```bash
uv run coverage run -m pytest tests/ -vv
coverage report
```
OR
```bash
make test
```