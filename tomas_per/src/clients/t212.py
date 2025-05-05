from contextlib import contextmanager
from logging import Logger, getLogger
from typing import Generator

from httpx import Auth, Client, HTTPError, Request, Response
from pydantic import TypeAdapter

from src.exceptions import APICallFailedException
from src.schema import Position
from src.settings import t212_settings

logger: Logger = getLogger(__name__)


class Trading212APIKeyAuth(Auth):
    def __init__(self, key: str) -> None:
        self.key = key

    def auth_flow(self, request: Request) -> Generator[Request, Response, None]:
        request.headers["Authorization"] = self.key
        yield request


@contextmanager
def get_t212_client() -> Generator[Client, None, None]:
    client = Client(
        auth=Trading212APIKeyAuth(
            key=t212_settings.api_key,
        )
    )

    try:
        yield client
    finally:
        client.close()


def get_open_positions() -> list[Position]:
    try:
        with get_t212_client() as client:
            response = client.get(t212_settings.url)

        response.raise_for_status()
    except HTTPError as exc:
        logger.error(
            f"API call to Trading212 failed with status code {response.status_code}.\n Exception info: {exc}"
        )
        raise APICallFailedException() from exc

    logger.info("API call to Trading212 successful.")

    return TypeAdapter(list[Position]).validate_python(response.json())
