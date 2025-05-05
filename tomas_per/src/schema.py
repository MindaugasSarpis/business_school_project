from datetime import UTC, datetime

from influxdb_client import Point
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator
from pydantic.alias_generators import to_camel


class Position(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    ticker: str
    quantity: float
    average_price: float
    current_price: float
    profit: float = Field(alias="ppl")
    forex_movement_impact: float | None = Field(alias="fxPpl")
    initial_fill_date: datetime
    frontend: str
    max_buy: float
    max_sell: float
    pie_quantity: float

    @field_validator("ticker", mode="before")
    def validate_ticker(cls, value: str) -> str:
        ticker, _, _ = value.partition("_")

        return ticker.upper()

    @computed_field
    def current_value(self) -> float:
        return self.current_price * self.quantity

    def to_point(
        self,
        time: datetime | None = None,
    ) -> Point:
        if time is None:
            time = datetime.now(tz=UTC)

        return (
            Point("stock_price")
            .tag("ticker", self.ticker)
            .field("current_price", self.current_price)
            .field("average_price", self.average_price)
            .field("quantity", self.quantity)
            .field("profit", self.profit)
            .field("forex_movement_impact", self.forex_movement_impact)
            .field("current_value", self.current_value)
            .time(time=time)
        )
