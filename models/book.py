from pydantic import BaseModel

class BookSearchResponse(BaseModel):
    ISBN: str
    title: str
    author: str
    year: str
    publisher: str
