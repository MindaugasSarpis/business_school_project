from logging import Logger, getLogger

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from src.settings import influxdb_settings

logger: Logger = getLogger(__name__)


def get_influxdb_client() -> InfluxDBClient:
    return InfluxDBClient(
        url=influxdb_settings.url,
        token=influxdb_settings.token,
        org=influxdb_settings.org,
    )


def push_data_to_influxdb(
    points: list[Point],
    bucket: str,
) -> None:
    influx_client = get_influxdb_client()

    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    write_api.write(
        bucket=bucket,
        org=influxdb_settings.org,
        record=points,
    )

    logger.info("Data pushed to InfluxDB successfully.")

    return None
