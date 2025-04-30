# Based on https://github.com/Chainlit/cookbook/blob/main/anthropic-chat/app.py

from typing import Dict, List

import chainlit as cl
from chromadb.api.models import Collection

from chatbot.session import (
    perform_rag,
    prepare_user_session,
)
from chatbot.llm import LLM
from chatbot.reranking import Reranker
from chatbot.utils.logging_config import configure_logging

Logger = configure_logging()


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initializes the chat session and loads necessary resources.
    """

    Logger.info("Chat started.")
    await cl.Message(
        content=(
            "Hey! I'm here to help you with your PDFs"
            " But before that I need to load some resources."
            " Please wait, I will notify you when loading is complete."
        )
    ).send()
    #* Sleep 1 s, to output the greeting message before loading is done.
    await cl.sleep(1)

    collection, llm, reranker = await prepare_user_session()

    cl.user_session.set("collection", collection)
    cl.user_session.set("conversation_history", [])
    cl.user_session.set("llm", llm)
    cl.user_session.set("reranker", reranker)

    Logger.info("Preparation to chat work completed.")
    await cl.Message(
        content="Loading complete. Please, ask me anything."
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Handles incoming messages from the user.

    Args:
        message (cl.Message): The message received from the user.
    """

    collection: Collection = cl.user_session.get("collection")
    conversation_history: List[Dict[str, str]] = cl.user_session.get(
        "conversation_history"
    )
    llm: LLM = cl.user_session.get("llm")
    reranker: Reranker = cl.user_session.get("reranker")

    query = message.content.strip()
    Logger.info(f"Message received: {query}")
    user_message = {"role": "user", "content": query}
    conversation_history.append(user_message)

    # Set extracted details
    cl.user_session.set("conversation_history", conversation_history)

    #* Perform RAG to generate an answer to the user's query
    answer, titles = await perform_rag(query, collection, conversation_history, llm, reranker)
    answer = f"{answer}\n\n\nRetrieved from PDFs:\n{'\n'.join(titles)}"
    
    cl.user_session.set("conversation_history", conversation_history)
    Logger.info(f"User message processing complete:\n{answer}")

    await cl.Message(content=answer).send()
