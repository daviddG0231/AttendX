"""
AttendX Authentication API

Handles user registration, login, and session management via Supabase Auth.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from config.database import get_supabase

router = APIRouter()


class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "student"  # student, instructor, admin
    student_id: Optional[str] = None
    department: Optional[str] = None


class SignInRequest(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None


@router.post("/signup")
async def sign_up(request: SignUpRequest):
    """Register a new user (student or instructor)."""
    try:
        db = get_supabase()
        
        # Create auth user
        auth_response = db.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if auth_response.user:
            # Create profile
            profile_data = {
                "id": auth_response.user.id,
                "full_name": request.full_name,
                "role": request.role,
                "email": request.email,
                "student_id": request.student_id,
                "department": request.department
            }
            
            db.table("profiles").insert(profile_data).execute()
            
            return {
                "success": True,
                "message": "Account created successfully",
                "user_id": auth_response.user.id,
                "role": request.role
            }
        
        raise HTTPException(status_code=400, detail="Failed to create account")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signin")
async def sign_in(request: SignInRequest):
    """Sign in with email and password."""
    try:
        db = get_supabase()
        
        auth_response = db.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if auth_response.user:
            # Get profile
            profile = db.table("profiles").select("*").eq(
                "id", auth_response.user.id
            ).single().execute()
            
            return {
                "success": True,
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "profile": profile.data
                }
            }
        
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/signout")
async def sign_out():
    """Sign out current user."""
    try:
        db = get_supabase()
        db.auth.sign_out()
        return {"success": True, "message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def get_current_user(authorization: str = None):
    """Get current authenticated user profile."""
    try:
        db = get_supabase()
        user = db.auth.get_user()
        
        if user:
            profile = db.table("profiles").select("*").eq(
                "id", user.user.id
            ).single().execute()
            
            return {
                "user_id": user.user.id,
                "email": user.user.email,
                "profile": profile.data
            }
        
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
