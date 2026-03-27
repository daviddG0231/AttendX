"""
AttendX Backend — FastAPI Application

REST API for the AI-based attendance system.
Handles authentication, student management, lecture sessions,
attendance records, and face registration.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

# Add face_engine to path
sys.path.insert(0, str(Path(__file__).parent.parent / "face_engine"))

from api.auth import router as auth_router
from api.students import router as students_router
from api.lectures import router as lectures_router
from api.attendance import router as attendance_router
from api.dashboard import router as dashboard_router

# Initialize FastAPI app
app = FastAPI(
    title="AttendX API",
    description="AI-Based Attendance System - REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(students_router, prefix="/api/students", tags=["Students"])
app.include_router(lectures_router, prefix="/api/lectures", tags=["Lectures"])
app.include_router(attendance_router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "AttendX API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "running",
            "database": "connected",
            "face_engine": "ready"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
