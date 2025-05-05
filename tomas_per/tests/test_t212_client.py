import pytest
from pytest_httpx import HTTPXMock

from src.clients.t212 import get_open_positions
from src.exceptions import APICallFailedException

DEFAULT_RESPONSE_CONTENT = [
    {
        "ticker": "TEST1_US_EQ",
        "quantity": 0.168629,
        "averagePrice": 52.8971885,
        "currentPrice": 56.73,
        "ppl": 0.99,
        "fxPpl": 0.27,
        "initialFillDate": "2025-03-12T20:00:00.000+03:00",
        "frontend": "SYSTEM",
        "maxBuy": 1000.1000,
        "maxSell": 1000,
        "pieQuantity": 0,
    },
    {
        "ticker": "TEST2_US_EQ",
        "quantity": 1,
        "averagePrice": 30.7,
        "currentPrice": 24.92,
        "ppl": -4.9,
        "fxPpl": 0.94,
        "initialFillDate": "2025-03-12T20:00:00.000+03:00",
        "frontend": "ANDROID",
        "maxBuy": 1000,
        "maxSell": 1000,
        "pieQuantity": 0,
    },
]


def test_get_open_positions(httpx_mock: HTTPXMock):
    # GIVEN
    httpx_mock.add_response(json=DEFAULT_RESPONSE_CONTENT)

    # WHEN
    positions = get_open_positions()

    # THEN
    positions_json = []
    for position in positions:
        positions_json.append(position.model_dump(mode="json"))

    assert positions_json == [
        {
            "ticker": "TEST1",
            "quantity": 0.168629,
            "average_price": 52.8971885,
            "current_price": 56.73,
            "profit": 0.99,
            "forex_movement_impact": 0.27,
            "initial_fill_date": "2025-03-12T20:00:00+03:00",
            "frontend": "SYSTEM",
            "max_buy": 1000.1,
            "max_sell": 1000.0,
            "pie_quantity": 0.0,
        },
        {
            "ticker": "TEST2",
            "quantity": 1.0,
            "average_price": 30.7,
            "current_price": 24.92,
            "profit": -4.9,
            "forex_movement_impact": 0.94,
            "initial_fill_date": "2025-03-12T20:00:00+03:00",
            "frontend": "ANDROID",
            "max_buy": 1000.0,
            "max_sell": 1000.0,
            "pie_quantity": 0.0,
        },
    ]


def test_get_open_positions_failed(httpx_mock: HTTPXMock):
    # GIVEN
    httpx_mock.add_response(status_code=400, json={})

    # WHEN/THEN
    with pytest.raises(APICallFailedException):
        get_open_positions()
