from fastapi import FastAPI
from routers import auth_router, book_router, review_router

app = FastAPI(title="Letterbooks API")

app.include_router(auth_router.router)
app.include_router(book_router.router)
app.include_router(review_router.router)

@app.get("/")
def root():
    return {"message": "Letterbooks"}
