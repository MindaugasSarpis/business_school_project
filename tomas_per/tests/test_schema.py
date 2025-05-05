import datetime

from time_machine import TimeMachineFixture

from src.schema import Position

DEFAULT_TIME = datetime.datetime(
    year=2025,
    month=3,
    day=13,
    hour=10,
    minute=10,
    second=10,
    tzinfo=datetime.UTC,
)

DEFAULT_SCHEMA_INIT_ARGS = {
    "ticker": "TEST",
    "quantity": 2.0,
    "average_price": 10.5,
    "current_price": 12.5,
    "profit": 10.1,
    "forex_movement_impact": 0.5,
    "initial_fill_date": DEFAULT_TIME,
    "frontend": "app",
    "max_buy": 1000,
    "max_sell": 2.0,
    "pie_quantity": 0,
}


def test_position_to_point(time_machine: TimeMachineFixture):
    # GIVEN
    time_machine.move_to(
        destination=DEFAULT_TIME,
        tick=False,
    )

    position = Position(**DEFAULT_SCHEMA_INIT_ARGS)  # type: ignore

    # WHEN
    point = position.to_point()

    # THEN
    assert point._tags == {"ticker": "TEST"}

    assert point._fields == {
        "current_price": 12.5,
        "average_price": 10.5,
        "quantity": 2.0,
        "profit": 10.1,
        "forex_movement_impact": 0.5,
        "current_value": 25.0,
    }
