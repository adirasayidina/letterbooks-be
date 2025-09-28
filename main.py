from fastapi import FastAPI
from routers import auth_router, book_router, review_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Letterbooks API")

origins = [
    "http://localhost:3031",
    "http://127.0.0.1:3031",
    "http://localhost:8081",
    "https://letterbooks.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(book_router.router)
app.include_router(review_router.router)

@app.get("/")
def root():
    return {"message": "Letterbooks"}
