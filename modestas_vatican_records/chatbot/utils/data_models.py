from pydantic import BaseModel


class Article(BaseModel):
    """PDF articles"""

    title: str
    body: str
