from fastapi import APIRouter, Header, HTTPException, Depends
from utils.jwt_handler import verify_access_token
from database import supabase
from models.review import ReviewRequest

router = APIRouter(prefix="/reviews", tags=["Reviews"])