from fastapi import APIRouter, HTTPException, Depends
from database import supabase
from models.auth import SignUpRequest, LoginRequest
from utils.jwt_handler import create_access_token, verify_access_token
import bcrypt

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup")
def signup(user: SignUpRequest):
    existing = supabase.table("TB_USER").select("*").eq("username", user.username).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    response = supabase.table("TB_USER").insert({
        "username": user.username,
        "password": hashed_pw
    }).execute()

    return {"message": "User created successfully"}

@router.post("/login")
def login(user: LoginRequest):
    response = supabase.table("TB_USER").select("*").eq("username", user.username).execute()
    if not response.data:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    db_user = response.data[0]
    if not bcrypt.checkpw(user.password.encode("utf-8"), db_user["password"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"username": db_user["username"]})
    return {"access_token": token, "token_type": "bearer"}
