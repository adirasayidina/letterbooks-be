from fastapi import APIRouter, Query, HTTPException
import pandas as pd

router = APIRouter(prefix="/books", tags=["Books"])

bookCv = 'books_data/books.csv'
df = pd.read_csv(bookCv, encoding='latin-1', on_bad_lines='skip', delimiter=";", quotechar='"', low_memory=False,  dtype=str)
df["ISBN"] = df["ISBN"].str.strip()

json_data = df.to_dict(orient="records")

@router.get("/")
def get_books(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    start = (page - 1) * limit
    end = start + limit

    total_books = len(df)

    books = json_data[start:end]

    return {
        "page": page,
        "limit": limit,
        "total": total_books,
        "total_pages": (total_books + limit - 1) // limit,
        "books": books
    }
    
@router.get("/{isbn}")
def get_book(isbn: str):
    book = df.loc[df["ISBN"] == isbn]
    
    print(book)
    if book.empty:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.to_dict(orient="records")[0]