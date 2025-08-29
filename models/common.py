from pydantic import BaseModel

class PaginationResponse(BaseModel):
    page: str
    limit: str
    total: str
    total_pages: str
    data: str
