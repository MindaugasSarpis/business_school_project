from typing import List

async def deduplicate_documents(documents: List[str]) -> List[str]:
    """Deduplicates a list of strings.

    Args:
        documents: A list of strings representing documents.

    Returns:
        A list of unique strings representing deduplicated documents.

    """
    unique_documents = set()
    
    # Handle both nested and flat document structures
    if documents and isinstance(documents, list):
        if documents and isinstance(documents[0], list):
            # Nested structure [[doc1, doc2], [doc3, doc4]]
            for documents_batch in documents:
                for document in documents_batch:
                    unique_documents.add(document)
        else:
            # Flat structure [doc1, doc2, doc3]
            for document in documents:
                unique_documents.add(document)

    return list(unique_documents)