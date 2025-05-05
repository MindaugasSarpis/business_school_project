from datetime import UTC, datetime

from influxdb_client import Point

from src.clients.influxdb import push_data_to_influxdb
from src.clients.t212 import get_open_positions
from src.settings import influxdb_settings

if __name__ == "__main__":
    positions = get_open_positions()

    # All data points should have the same timestamp, as they are in the same batch
    timestamp = datetime.now(tz=UTC)
    points: list[Point] = [position.to_point(time=timestamp) for position in positions]

    push_data_to_influxdb(
        points=points,
        bucket=influxdb_settings.stocks_bucket_name,
    )
