import asyncio
import time

from chatbot.llm import LLM
from chatbot.utils.free_torch_cache import free_torch_cache
from chatbot.utils.logging_config import configure_logging

Logger = configure_logging()


async def async_test_extract_connectivity_details() -> None:
    """Tests the extract_connectivity_details method asynchronously."""

    llm_instance = LLM()

    start = time.time()
    response = await llm_instance.extract_connectivity_details(
        user_prompt="My sister lives in USA, my father resides in London and my mother is in Sweden, my sister uses Linux Ubuntu, my mother uses Windows, but I use macOS and I am from Japan"
    )
    Logger.info(f"Response: {response}")
    Logger.info(f"Time taken: {time.time() - start:.2f} seconds")

    start = time.time()
    response = await llm_instance.extract_connectivity_details(
        user_prompt="I'm using Windows"
    )
    Logger.info(f"Response: {response}")
    Logger.info(f"Time taken: {time.time() - start:.2f} seconds")

    start = time.time()
    response = await llm_instance.extract_connectivity_details(
        user_prompt="I'm from Lithuania"
    )
    Logger.info(f"Response: {response}")
    Logger.info(f"Time taken: {time.time() - start:.2f} seconds")

    start = time.time()
    response = await llm_instance.extract_connectivity_details(
        user_prompt="I've bought some discounted bananas"
    )
    Logger.info(f"Response: {response}")
    Logger.info(f"Time taken: {time.time() - start:.2f} seconds")

    device = llm_instance.device
    del llm_instance
    await free_torch_cache(device)


async def async_test_determine_connectivity_issue_case() -> None:
    """Tests the determine_connectivity_issue_case method asynchronously."""
    
    llm_instance = LLM()

    start = time.time()
    response = await llm_instance.determine_connectivity_issue_case(
        user_prompt="Hey, It seems that I am unable to connect to the VPN for some reason"
    )
    Logger.info(f"Response: {response}, Expected: True")
    Logger.info(f"Time taken: {time.time() - start:.2f} seconds")

    start = time.time()
    response = await llm_instance.determine_connectivity_issue_case(
        user_prompt="Hey, my web browser says that there are no connection"
    )
    Logger.info(f"Response: {response}, Expected: True")
    Logger.info(f"Time taken: {time.time() - start:.2f} seconds")

    start = time.time()
    response = await llm_instance.determine_connectivity_issue_case(
        user_prompt="How to setup proxy on Deluge?"
    )
    Logger.info(f"Response: {response}, Expected: False")
    Logger.info(f"Time taken: {time.time() - start:.2f} seconds")

    start = time.time()
    response = await llm_instance.determine_connectivity_issue_case(
        user_prompt="What is NordVPN?"
    )
    Logger.info(f"Response: {response}, Expected: False")
    Logger.info(f"Time taken: {time.time() - start:.2f} seconds")

    device = llm_instance.device
    del llm_instance
    await free_torch_cache(device)


def test_extract_connectivity_details() -> None:
    asyncio.run(async_test_extract_connectivity_details())


def test_determine_connectivity_issue_case() -> None:
    asyncio.run(async_test_determine_connectivity_issue_case())
