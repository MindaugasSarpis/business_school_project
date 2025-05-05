from typing import Final

from pydantic_settings import BaseSettings, SettingsConfigDict

NOT_SET: Final[str] = "NOT_SET"

BASE_SETTINGS: SettingsConfigDict = {
    "env_file": ".env",
    "extra": "ignore",
}


class T212Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="T212_",
        **BASE_SETTINGS,
    )

    api_key: str = NOT_SET
    url: str = NOT_SET


class InfluxDBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INFLUXDB_",
        **BASE_SETTINGS,
    )

    token: str = NOT_SET
    org: str = NOT_SET
    url: str = NOT_SET
    stocks_bucket_name: str = "stocks"


t212_settings = T212Settings()
influxdb_settings = InfluxDBSettings()
