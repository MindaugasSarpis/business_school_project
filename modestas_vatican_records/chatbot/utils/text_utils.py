import re
from typing import Dict, List


def preprocess_text(text: str) -> str:
    """Preprocesses text by lowercasing and removing extra whitespace.

    Args:
        text (str): The text to preprocess.

    Returns:
        str: The preprocessed text.
    """

    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def form_missing_fields_msg(
    missing_fields: List[str], connectivity_details: Dict[str, str] | None = None
) -> str:
    """Forms a message listing missing fields or displaying provided connectivity details.

    Args:
        missing_fields (List[str]): A list of missing fields.
        connectivity_details (Dict[str, str] | None, optional): A dictionary of connectivity details. Defaults to None.

    Returns:
        str: The formatted message.
    """

    if connectivity_details:
        missing_fields_msg = "\n".join(
            [
                f'My {field.replace("_", " ")}: {connectivity_details[field]}'
                for field in missing_fields
            ]
        )
    else:
        missing_fields_msg = "\n".join(
            [
                f'{i + 1}. {field.replace("_", " ")}'
                for i, field in enumerate(missing_fields)
            ]
        )
    return missing_fields_msg
