import asyncio
import numpy as np
import umap
from chatbot.config import CHROMA_DB_PERSIST_DIR, COLLECTION_NAME, DATA_ARTICLES_PATH, NUM_RETRIEVE_DOCUMENTS
from chatbot.database import (
    create_chroma_client,
    create_embedding_function,
    get_or_create_collection,
    load_articles,
    populate_collection,
)
from chatbot.llm import LLM
from tqdm import tqdm
from pathlib import Path
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from chromadb.api.models import Collection
import matplotlib.pyplot as plt
from typing import Tuple, List


async def prepare_chroma() -> Tuple[Collection.Collection, SentenceTransformerEmbeddingFunction]:
    """Prepares the Chroma database for use.

    Creates a Chroma client, embedding function, and collection. Populates the collection with articles if it's empty.

    Returns:
        Tuple containing the Chroma collection and the embedding function.

    Raises:
        Exception: If any of the database operations fail.
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

    return collection, embedding_function


async def project_embeddings(
    embeddings: np.ndarray[float, np.dtype[np.float64]],
    umap_transform: umap.UMAP
) -> np.ndarray[float, np.dtype[np.float64]]:
    """Projects embeddings into a 2D space using UMAP.

    Args:
        embeddings (np.ndarray[float, np.dtype[np.float64]]): The embeddings to project.
        umap_transform (umap.UMAP): The fitted UMAP transformer.

    Returns:
        np.ndarray[float, np.dtype[np.float64]]: The projected embeddings.
    """
    umap_embeddings = np.empty((len(embeddings),2))
    for i, embedding in enumerate(tqdm(embeddings)): 
        umap_embeddings[i] = umap_transform.transform([embedding])
    return umap_embeddings


async def display_latent_space(
    embeddings: np.ndarray[float, np.dtype[np.float64]],
    query_embeddings: np.ndarray[float, np.dtype[np.float64]],
    retrieved_embeddings: np.ndarray[float, np.dtype[np.float64]],
    umap_transform: umap.UMAP
) -> None:
    """Displays the latent space of embeddings using UMAP and matplotlib.

    Projects the embeddings, query embedding, and retrieved embeddings into 2D space and plots them.

    Args:
        embeddings (np.ndarray[float, np.dtype[np.float64]]): The dataset embeddings.
        query_embedding (np.ndarray[float, np.dtype[np.float64]]): The query embedding.
        retrieved_embeddings (np.ndarray[float, np.dtype[np.float64]]): The retrieved embeddings.
        umap_transform (umap.UMAP): The fitted UMAP transformer.

    Returns:
        None
    """
    projected_query_embedding = await project_embeddings([query_embeddings[0]], umap_transform)
    projected_add_queries_embeddings = await project_embeddings(query_embeddings[1:], umap_transform)

    projected_dataset_embeddings = await project_embeddings(embeddings, umap_transform)
    projected_retrieved_embeddings = await project_embeddings(retrieved_embeddings, umap_transform)
    
    plt.figure()
    plt.scatter(projected_dataset_embeddings[:, 0], projected_dataset_embeddings[:, 1], s=10, color='gray')
    plt.scatter(projected_query_embedding[:, 0], projected_query_embedding[:, 1], s=150, marker='X', color='r')
    plt.scatter(projected_add_queries_embeddings[:, 0], projected_add_queries_embeddings[:, 1], s=150, marker='X', color='y')
    plt.scatter(projected_retrieved_embeddings[:, 0], projected_retrieved_embeddings[:, 1], s=100, facecolors='none', edgecolors='g')
    plt.gca().set_aspect('equal', 'datalim')
    plt.title('Projected Embeddings')
    plt.show()


async def get_db_retrieval_embeddings(
    query_texts: List[str],
    chroma_collection: Collection,
    embedding_function: SentenceTransformerEmbeddingFunction
) -> Tuple[np.ndarray[float, np.dtype[np.float64]], np.ndarray[float, np.dtype[np.float64]]]:
    """Retrieves embeddings from the Chroma database for a given query.

    Queries the Chroma collection for similar documents and returns the query embedding and retrieved embeddings.

    Args:
        query (str): The query string.
        chroma_collection (Collection): The Chroma collection.
        embedding_function (SentenceTransformerEmbeddingFunction): The embedding function.

    Returns:
        Tuple containing the query embedding and the retrieved embeddings.

    Raises:
        Exception: If the query fails or if the results are not in the expected format.
    """

    results = chroma_collection.query(query_texts=query_texts, n_results=NUM_RETRIEVE_DOCUMENTS, include=['documents', 'embeddings'])
    query_embeddings = embedding_function(query_texts)
    result_embeddings = results['embeddings']


    # query_embeddings = [item for sublist in query_embeddings for item in sublist]
    retrieved_embeddings = [item for sublist in result_embeddings for item in sublist]

    
    return query_embeddings, retrieved_embeddings



async def main() -> None:
    """Main function to demonstrate the embedding visualization.

    Sets up the Chroma database, retrieves embeddings for a sample query, and displays the latent space.

    Returns:
        None
    """
    query = """Help me solve my connectivity issue problem. Hey, It seems that I am unable to connect to the VPN for some reason.
    My operating system: Windows,
    My country: Lithuania
    """

    llm = LLM()
    # query = await llm.generate_a_help_answer_query(query)
    # query_texts = [query]
    query_texts = await llm.expand_querry_question(query)

    chroma_collection, embedding_function = await prepare_chroma()
    embeddings = chroma_collection.get(include=["embeddings"])["embeddings"]
    umap_transform = umap.UMAP(random_state=0, transform_seed=0).fit(embeddings)

    query_embeddings, retrieved_embeddings = await get_db_retrieval_embeddings(
        query_texts,
        chroma_collection,
        embedding_function
    )

    await display_latent_space(
        embeddings,
        query_embeddings,
        retrieved_embeddings,
        umap_transform
    )


if __name__ == "__main__":
    asyncio.run(main())
