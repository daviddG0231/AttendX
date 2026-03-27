"""
AttendX Students API

Handles student management and face registration.
"""

import io
import cv2
import numpy as np
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from config.database import get_supabase

router = APIRouter()


class StudentResponse(BaseModel):
    id: str
    full_name: str
    student_id: str
    email: str
    department: str = None
    is_face_registered: bool = False


@router.get("/")
async def list_students(course_id: str = None):
    """List all students, optionally filtered by course."""
    try:
        db = get_supabase()
        
        if course_id:
            # Get enrolled students for a course
            result = db.table("enrollments").select(
                "student_id, profiles(*)"
            ).eq("course_id", course_id).execute()
            
            students = [item['profiles'] for item in result.data if item.get('profiles')]
        else:
            # Get all students
            result = db.table("profiles").select("*").eq("role", "student").execute()
            students = result.data
        
        return {"students": students, "count": len(students)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{student_id}")
async def get_student(student_id: str):
    """Get a specific student's profile."""
    try:
        db = get_supabase()
        
        result = db.table("profiles").select("*").eq(
            "student_id", student_id
        ).single().execute()
        
        if result.data:
            return result.data
        
        raise HTTPException(status_code=404, detail="Student not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{student_id}/register-face")
async def register_face(
    student_id: str,
    images: List[UploadFile] = File(..., description="Minimum 5 face images")
):
    """
    Register a student's face for recognition.
    
    Requires minimum 5 images under different conditions per project requirements.
    Images are processed to extract face embeddings and stored in the FAISS index.
    """
    if len(images) < 5:
        raise HTTPException(
            status_code=400, 
            detail=f"Minimum 5 images required, got {len(images)}. "
                   f"Please provide images under different lighting and pose conditions."
        )
    
    try:
        # Import face engine
        from face_detector import FaceDetector
        from face_matcher import FaceMatcher
        
        detector = FaceDetector()
        matcher = FaceMatcher()
        matcher.load_index()
        
        # Process uploaded images
        face_images = []
        embeddings = []
        
        for i, image_file in enumerate(images):
            # Read image
            contents = await image_file.read()
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                continue
            
            # Extract face embedding
            faces = detector.detect_faces(img)
            
            if faces:
                embeddings.append(faces[0]['embedding'])
                face_images.append(img)
        
        if len(embeddings) < 3:
            raise HTTPException(
                status_code=400,
                detail=f"Only {len(embeddings)} faces detected from {len(images)} images. "
                       f"Please provide clearer face images."
            )
        
        # Get student name from database
        db = get_supabase()
        student = db.table("profiles").select("full_name, id").eq(
            "student_id", student_id
        ).single().execute()
        
        if not student.data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student_name = student.data['full_name']
        
        # Register in FAISS index
        success = matcher.register_student(student_id, student_name, embeddings)
        
        if success:
            matcher.save_index()
            
            # Update profile
            db.table("profiles").update(
                {"is_face_registered": True}
            ).eq("student_id", student_id).execute()
            
            # Store face data references
            for i in range(len(embeddings)):
                db.table("face_data").insert({
                    "student_id": student.data['id'],
                    "embedding_index": i,
                    "quality_score": 1.0
                }).execute()
            
            return {
                "success": True,
                "message": f"Face registered successfully for {student_name}",
                "student_id": student_id,
                "images_processed": len(images),
                "embeddings_extracted": len(embeddings)
            }
        
        raise HTTPException(status_code=500, detail="Failed to register face")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{student_id}/face-test")
async def face_test(
    student_id: str,
    image: UploadFile = File(...)
):
    """
    Test face recognition for a student (FR3).
    
    Allows students to verify their face is recognizable before registration.
    """
    try:
        from face_detector import FaceDetector
        
        detector = FaceDetector()
        
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Detect faces
        faces = detector.detect_faces(img)
        
        if not faces:
            return {
                "success": False,
                "message": "No face detected. Please ensure your face is clearly visible, "
                          "well-lit, and facing the camera.",
                "faces_detected": 0
            }
        
        if len(faces) > 1:
            return {
                "success": False, 
                "message": "Multiple faces detected. Please ensure only your face is in the image.",
                "faces_detected": len(faces)
            }
        
        face = faces[0]
        return {
            "success": True,
            "message": "Face detected successfully! You can proceed with registration.",
            "faces_detected": 1,
            "detection_confidence": round(face['det_score'], 3),
            "bbox": face['bbox']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{student_id}/attendance")
async def get_student_attendance(student_id: str, course_id: str = None):
    """Get attendance records for a specific student."""
    try:
        db = get_supabase()
        
        # Get student's user ID
        student = db.table("profiles").select("id").eq(
            "student_id", student_id
        ).single().execute()
        
        if not student.data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        query = db.table("attendance_records").select(
            "*, lecture_sessions(*, courses(*))"
        ).eq("student_id", student.data['id'])
        
        if course_id:
            query = query.eq("lecture_sessions.course_id", course_id)
        
        result = query.order("created_at", desc=True).execute()
        
        return {
            "student_id": student_id,
            "records": result.data,
            "total_records": len(result.data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
