from pydantic import BaseModel

class BookSearchResponse(BaseModel):
    ISBN: str
    title: str
    author: str
    year: str
    publisher: str
    score: float
    
class BookSearchRequest(BaseModel):
    title: str = None      # optional
    author: str = None     # optional
    limit: int = 500
    threshold: int = 60
    page: int = 1
    page_size: int = 100