from pydantic import BaseModel

class ReviewRequest(BaseModel):
    book_id: str
    user_id: str
    rating: int
    comment: str
