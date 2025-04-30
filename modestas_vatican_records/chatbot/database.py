import pypdf
import uuid
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from chromadb.api.models import Collection
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

from chatbot.config import (
    CHARACTER_SPLIT_CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    SEPARATORS,
    TOKENS_PER_CHUNK,
)
from chatbot.utils.data_models import Article
from chatbot.utils.text_utils import preprocess_text
from chatbot.utils.logging_config import configure_logging

Logger = configure_logging()


async def load_articles(directory_path: Path) -> List[Dict[str, str]]:
    """Loads articles from PDF files in a directory.

    Args:
        directory_path (Path): The path to the directory containing PDF files.

    Returns:
        List[Dict[str, str]]: A list of articles, where each article is a dictionary
                             with "title" (filename) and "body" (text content).

    Raises:
        Exception: If the directory is not found or if there is an error during PDF processing.
    """

    try:
        if not directory_path.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        articles: List[Dict[str, str]] = []
        for filepath in directory_path.iterdir():
            if filepath.name.endswith(".pdf"):
                try:
                    with open(filepath, "rb") as f:
                        reader = pypdf.PdfReader(f)
                        pages_text = []
                        for page in reader.pages:
                            pages_text.append(preprocess_text(page.extract_text()))
                        text = ".\n".join(pages_text)
                        articles.append(
                            {"title": filepath.stem, "body": text}
                        )
                except Exception as e:
                    Logger.error(f"Failed to process PDF {filepath.name}: {e}")
                    # Continue processing other PDFs even if one fails
                    continue

        Logger.info(f"Loaded {len(articles)} articles from {directory_path}")
        return articles

    except FileNotFoundError as e:
        Logger.error(f"Failed to load articles from {directory_path}: {e}")
        raise
    except Exception as e:
        Logger.error(f"An unexpected error occurred: {e}")
        raise


async def create_embedding_function(
    embedding_model_name: str | None = None,
) -> SentenceTransformerEmbeddingFunction:
    """Creates a SentenceTransformerEmbeddingFunction asynchronously.

    Args:
        embedding_model_name (str | None, optional): The name of the embedding model. Defaults to None.

    Returns:
        SentenceTransformerEmbeddingFunction: The embedding function.

    Raises:
        Exception: If there is an error during creation.
    """
    try:
        if not embedding_model_name:
            embedding_model_name = EMBEDDING_MODEL

        embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=embedding_model_name
        )
        Logger.info("Embedding function initialized.")
        return embedding_function
    except Exception as e:
        Logger.error(f"Error initializing embedding function: {e}")
        raise


async def create_chroma_client(persist_directory: str) -> chromadb.PersistentClient:
    """Creates a ChromaDB client.

    Args:
        persist_directory (str): The directory to persist the database.

    Returns:
        chromadb.PersistentClient: The ChromaDB client.

    Raises:
        chromadb.APIError: If there is an error creating the client.
    """

    try:
        client = chromadb.PersistentClient(path=persist_directory)
        Logger.info("Chroma client initialized.")
        return client
    except chromadb.APIError as e:
        Logger.error(f"Error initializing Chroma client: {e}")
        raise


async def get_or_create_collection(
    client: chromadb.PersistentClient,
    collection_name: str,
    embedding_function: SentenceTransformerEmbeddingFunction,
) -> Collection:
    """Gets or creates a ChromaDB collection.

    Args:
        client (chromadb.PersistentClient): The ChromaDB client.
        collection_name (str): The name of the collection.
        embedding_function (SentenceTransformerEmbeddingFunction): The embedding function.

    Returns:
        Collection: The ChromaDB collection.
    """

    try:
        collection = client.get_collection(name=collection_name)
        Logger.info(f"Found existing collection '{collection_name}'.")
    except chromadb.errors.InvalidCollectionException:
        Logger.info(f"Collection '{collection_name}' not found. Creating a new one.")
        collection = client.create_collection(
            name=collection_name, embedding_function=embedding_function
        )
    return collection


async def populate_collection(
    collection: Collection, articles: List[Dict[str, Any]]
) -> None:
    """Populates a ChromaDB collection with articles.

    Args:
        collection (Collection): The ChromaDB collection.
        articles (List[Dict[str, Any]]): The articles to add to the collection.

    Raises:
        chromadb.APIError: If there is an error populating the collection.
    """

    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    character_splitter = RecursiveCharacterTextSplitter(
        separators=SEPARATORS,
        chunk_size=CHARACTER_SPLIT_CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    token_splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=CHUNK_OVERLAP, tokens_per_chunk=TOKENS_PER_CHUNK
    )

    character_split_chunk_num = 0
    token_split_chunk_num = 0

    for entry in articles:

        article = Article(**entry)
        if not article.body:
            Logger.warning(
                f"Article '{article.title}' has no body text content. Skipping."
            )
            continue

        character_split_texts = character_splitter.split_text(article.body)
        character_split_chunk_num += len(character_split_texts)
        chunks = []
        for text in character_split_texts:
            chunks += token_splitter.split_text(text)

        token_split_chunk_num += len(chunks)

        for chunk in chunks:
            uid = str(uuid.uuid4())
            ids.append(uid)
            documents.append(chunk)
            metadatas.append({"title": article.title})

    try:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        Logger.info(
            f"Added {len(ids)} document chunks to collection '{collection.name}'."
        )
        Logger.info(f"Character split chunks = {character_split_chunk_num}.")
    except chromadb.APIError as e:
        Logger.error(f"Error populating collection: {e}")
        raise
