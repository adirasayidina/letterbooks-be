import math
from fastapi import APIRouter, Header, HTTPException, Depends
from utils.jwt_handler import verify_access_token
from database import supabase
from models.review import ReviewRequest, ReviewResponse
from utils.jwt_handler import get_current_user
import pandas as pd

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/create")
def add_review(review: ReviewRequest, user=Depends(get_current_user)):
    response = supabase.table("TB_REVIEW").insert({
        "book_id": review.book_id,
        "user_id": user["username"],   # taken from JWT, not frontend
        "rating": review.rating,
        "comment": review.comment,
    }).execute()
    return {"message": "Review added", "data": response.data}

from fastapi import HTTPException

@router.put("/edit/{id}")
def edit_review(id: str, review: ReviewRequest, page: int = 1, limit: int = 10, user=Depends(get_current_user)):
    existing = supabase.table("TB_REVIEW").select("*").eq("id", id).eq("user_id", user["username"]).execute()

    if not existing.data:
        raise HTTPException(status_code=404, detail="Review not found or not authorized")

    response = supabase.table("TB_REVIEW").update({
        "rating": review.rating,
        "comment": review.comment,
    }).eq("id", id).eq("user_id", user["username"]).execute()

    return {"message": "Review updated", "data": response.data}

@router.get("/me")
def get_my_reviews(page: int = 1, limit: int = 10, user=Depends(get_current_user)):
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10

    offset = (page - 1) * limit

    response = supabase.table("TB_REVIEW").select("*", count="exact").eq("user_id", user["username"]).order("updated_at", desc=True).range(offset, offset + limit - 1).execute()

    count_response = supabase.table("TB_REVIEW").select("id", count="exact").eq("user_id", user["username"]).execute()
        
    total = count_response.count or 0
    total_pages = math.ceil(total / limit) if total > 0 else 1
    
    return {
        "page": page,
        "limit": limit,
        "total": response.count,  
        "total_pages": total_pages,
        "reviews": response.data
    }
    
@router.get("/book/{isbn}")
def get_book_reviews(isbn: str, page: int = 1, limit: int = 10):
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10

    offset = (page - 1) * limit

    response = supabase.table("TB_REVIEW").select("*", count="exact").eq("book_id", isbn).order("updated_at", desc=True).range(offset, offset + limit - 1).execute()

    count_response = supabase.table("TB_REVIEW").select("id", count="exact").eq("book_id", isbn).execute()
        
    total = count_response.count or 0
    total_pages = math.ceil(total / limit) if total > 0 else 1
    
    return {
        "page": page,
        "limit": limit,
        "total": response.count,  
        "total_pages": total_pages,
        "reviews": response.data
    }


@router.get("/{reviewId}")
def get_review_by_id(reviewId: str):
    response = supabase.table("TB_REVIEW").select("*").eq("id", reviewId).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Review not found.")
    
    review = response.data[0]
    return ReviewResponse(**review)