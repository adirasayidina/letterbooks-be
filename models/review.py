from pydantic import BaseModel
from typing import Optional

class ReviewRequest(BaseModel):
    book_id: Optional[str] = None
    rating: int
    comment: str

class ReviewResponse(BaseModel):
    id: str
    book_id: str
    user_id: str
    rating: int
    comment: str
