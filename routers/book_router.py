from fastapi import APIRouter, Query, HTTPException
import pandas as pd
from rapidfuzz import process, fuzz
from models.book import BookSearchResponse, BookSearchRequest

router = APIRouter(prefix="/books", tags=["Books"])

bookCv = 'books_data/books.csv'
df = pd.read_csv(bookCv, encoding='latin-1', on_bad_lines='skip', delimiter=";", quotechar='"', low_memory=False,  dtype=str)
df["ISBN"] = df["ISBN"].str.strip()
titles = df["Book-Title"].dropna().astype(str).tolist()

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

    if book.empty:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.to_dict(orient="records")[0]

@router.post("/search", response_model=dict)
def fuzzy_search(req: BookSearchRequest):
    if not req.title and not req.author:
        raise HTTPException(status_code=400, detail="At least one of 'title' or 'author' must be provided")

    search_series = []
    search_text = []

    if req.title and req.author:
        search_series = (df["Book-Title"].fillna('') + " " + df["Book-Author"].fillna(''))
    elif req.title:
        search_series = df["Book-Title"].fillna('')
    elif req.author:
        search_series = df["Book-Author"].fillna('')

    search_list = search_series.tolist()

    substring_filter = []
    for idx, row in df.iterrows():
        match_title = req.title.lower() in row["Book-Title"].lower() if req.title else True
        match_author = req.author.lower() in row["Book-Author"].lower() if req.author else True
        if match_title and match_author:
            substring_filter.append(idx)

    substring_results = []
    for idx in substring_filter:
        row = df.iloc[idx]
        substring_results.append({
            "ISBN": row["ISBN"],
            "Book-Title": row["Book-Title"],
            "Book-Author": row["Book-Author"],
            "Year-Of-Publication": row["Year-Of-Publication"],
            "Publisher": row["Publisher"],
            "Image-URL-L": row["Image-URL-L"],
            "score": 100.0
        })

    results = process.extract(
        (req.title or "") + " " + (req.author or ""),
        search_list,
        scorer=fuzz.token_set_ratio,
        limit=req.limit
    )

    fuzzy_results = []
    seen_titles = set([r["Book-Title"] for r in substring_results])

    for match, score, idx in results:
        if score >= req.threshold:
            row = df.iloc[idx]
            if row["Book-Title"] not in seen_titles:
                fuzzy_results.append({
                    "ISBN": row["ISBN"],
                    "Book-Title": row["Book-Title"],
                    "Book-Author": row["Book-Author"],
                    "Year-Of-Publication": row["Year-Of-Publication"],
                    "Publisher": row["Publisher"],
                    "Image-URL-L": row["Image-URL-L"],
                    "score": float(score)
                })

    all_results = substring_results + fuzzy_results
    start = (req.page - 1) * req.page_size
    end = start + req.page_size
    paginated = all_results[start:end]
    total_pages = (len(all_results) + req.page_size - 1) // req.page_size

    return {
        "total_results": len(all_results),
        "total_pages": total_pages,
        "page": req.page,
        "books": paginated
    }

