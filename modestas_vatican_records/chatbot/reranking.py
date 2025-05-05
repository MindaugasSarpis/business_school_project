from typing import List

import numpy as np
import torch
from sentence_transformers import CrossEncoder

from chatbot.config import CROSS_ENCODER, HF_CACHE_DIR, NUM_RETRIEVE_DOCUMENTS
from chatbot.utils.logging_config import configure_logging

Logger = configure_logging()


class Reranker:
    def __init__(self, model_name: str | None = None):
        """Initializes an Reranker instance.

        Args:
            model_name (str | None, optional): The name of the cross encoder model. Defaults to None.

        Raises:
            OSError: If the model or tokenizer cannot be loaded.
        """

        if not model_name:
            model_name = CROSS_ENCODER

        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

        try:
            self.cross_encoder = CrossEncoder(
                model_name=model_name, cache_dir=HF_CACHE_DIR, device=device
            )
            Logger.info(
                f"CrossEncoder loaded successfully from {model_name}"
            )
        except (OSError, FileNotFoundError) as e:
            Logger.error(f"Error loading CrossEncoder model: {e}")
            raise

    async def rerank(
        self,
        query: str,
        documents: List[str],
        num_retrieve_documents: int | None = None,
    ) -> List[str]:
        """Returns the most relevant documents to the query using CrossEncoder.

        Args:
            query: str - The search query.
            documents: List[str]- A list of documents to rerank.

        Returns:
            List[str] - A list of the most relevant documents, limited by NUM_RETRIEVE_DOCUMENTS.
        """
        pairs = [[query, doc] for doc in documents]
        scores = self.cross_encoder.predict(pairs)

        # Get the indices of the documents sorted by score in descending order
        sorted_indices = np.argsort(scores)[::-1]

        if not num_retrieve_documents:
            num_retrieve_documents = NUM_RETRIEVE_DOCUMENTS

        top_indices = sorted_indices[:num_retrieve_documents]
        Logger.info("Documents have been reranked by their relevance to the query.")
        return [documents[i] for i in top_indices]
