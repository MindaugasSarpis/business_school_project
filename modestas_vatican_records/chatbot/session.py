from pathlib import Path
from typing import Dict, List, Tuple

import chromadb
from chromadb.api.models import Collection
from chromadb.utils.embedding_functions import \
    SentenceTransformerEmbeddingFunction

from chatbot.config import (
    CHROMA_DB_PERSIST_DIR,
    COLLECTION_NAME,
    CONVERSATION_HISTORY_LIMIT,
    CROSS_ENCODER,
    DATA_ARTICLES_PATH,
    HF_LLM_MODEL_ID,
    NUM_RETRIEVE_DOCUMENTS
)
from chatbot.database import (
    create_chroma_client,
    create_embedding_function,
    get_or_create_collection,
    load_articles,
    populate_collection
)
from chatbot.llm import LLM
from chatbot.reranking import Reranker
from chatbot.utils.logging_config import configure_logging
from chatbot.utils.filter_documents import deduplicate_documents

Logger = configure_logging()


async def prepare_user_session() -> Tuple[chromadb.api.models.Collection, LLM, Reranker]:
    """Prepares the user session by loading resources and setting up the chatbot.

    Returns:
        Tuple[chromadb.api.models.Collection, LLM]: A tuple containing the ChromaDB collection and the LLM instance.
    """

    client = await create_chroma_client(persist_directory=CHROMA_DB_PERSIST_DIR)
    embedding_function: SentenceTransformerEmbeddingFunction = (
        await create_embedding_function()
    )
    collection = await get_or_create_collection(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )
    if collection.count() == 0:
        articles = await load_articles(Path(DATA_ARTICLES_PATH))
        await populate_collection(collection=collection, articles=articles)

    llm = LLM(HF_LLM_MODEL_ID)
    reranker = Reranker(CROSS_ENCODER)
    return collection, llm, reranker


async def perform_rag(
    query: str,
    collection: Collection,
    conversation_history: List[Dict[str, str]],
    llm: LLM,
    reranker: Reranker,
) -> Tuple[str, List[str]]:
    """Performs RAG (Retrieval Augmented Generation) to answer a user's query.

    Args:
        query (str): The user's query.
        collection (Collection): The ChromaDB collection.
        conversation_history (List[Dict[str, str]]): The conversation history.
        llm (LLM): The language model instance.

    Returns:
        Tuple[str, List[str]]: A tuple containing the answer and a list of URLs of retrieved documents.
    """

    Logger.info("Fetching documents for RAG")
    # Generate multiple query variations to improve retrieval
    query_texts = [query]
    expanded_query = await llm.expand_querry_question(query)
    if expanded_query:
        query_texts.extend(expanded_query)
    
    # Add query processing and caching
    results = collection.query(
        query_texts=query_texts,
        n_results=NUM_RETRIEVE_DOCUMENTS,
        include=["documents", "metadatas"]
    )
    
    # Flatten and deduplicate documents from multiple queries
    all_documents = [doc for sublist in results["documents"] for doc in sublist]
    documents = await deduplicate_documents(all_documents)
    
    # Rerank documents for better relevance
    documents = await reranker.rerank(query, documents)
    
    # Extract titles from metadata instead of URLs
    titles = []
    for metadatas_list in results["metadatas"]:
        for metadata in metadatas_list:
            if metadata.get("title") and metadata.get("title") not in titles:
                titles.append(metadata.get("title"))

    Logger.info(f"Performing RAG for query:\n{query}")
    answer = await llm.rag(
        query=query, documents=documents, conversation_history=conversation_history
    )

    llm_response = {"role": "assistant", "content": answer}
    conversation_history.append(llm_response)
    while len(conversation_history) > CONVERSATION_HISTORY_LIMIT:
        conversation_history.pop(0)

    return answer, titles