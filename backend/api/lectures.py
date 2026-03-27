"""
AttendX Lectures API

Handles lecture session management, scheduling, and monitoring.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.database import get_supabase

router = APIRouter()


class CreateLectureRequest(BaseModel):
    course_id: str
    classroom_id: str
    scheduled_start: datetime
    scheduled_end: datetime
    notes: Optional[str] = None


class DelayLectureRequest(BaseModel):
    delay_minutes: int
    reason: Optional[str] = None


class AppealRequest(BaseModel):
    session_id: str
    reason: str
    appeal_type: str = "other"  # room_change, delay, technical_issue, other


@router.get("/")
async def list_lectures(
    course_id: str = None,
    instructor_id: str = None,
    status: str = None,
    date: str = None
):
    """List lecture sessions with optional filters."""
    try:
        db = get_supabase()
        
        query = db.table("lecture_sessions").select(
            "*, courses(*), classrooms(*), profiles!lecture_sessions_instructor_id_fkey(*)"
        )
        
        if course_id:
            query = query.eq("course_id", course_id)
        if instructor_id:
            query = query.eq("instructor_id", instructor_id)
        if status:
            query = query.eq("status", status)
        
        result = query.order("scheduled_start", desc=True).execute()
        
        return {"sessions": result.data, "count": len(result.data)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_lecture(request: CreateLectureRequest):
    """Create a new lecture session."""
    try:
        db = get_supabase()
        
        # Get course info
        course = db.table("courses").select("*").eq(
            "id", request.course_id
        ).single().execute()
        
        if not course.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        session_data = {
            "course_id": request.course_id,
            "classroom_id": request.classroom_id,
            "instructor_id": course.data['instructor_id'],
            "scheduled_start": request.scheduled_start.isoformat(),
            "scheduled_end": request.scheduled_end.isoformat(),
            "status": "scheduled",
            "notes": request.notes
        }
        
        result = db.table("lecture_sessions").insert(session_data).execute()
        
        return {
            "success": True,
            "session": result.data[0] if result.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/start")
async def start_lecture(session_id: str):
    """
    Start a lecture session and begin attendance monitoring.
    
    Activates the face recognition engine for the classroom camera.
    """
    try:
        db = get_supabase()
        
        # Get session details
        session = db.table("lecture_sessions").select(
            "*, classrooms(*), courses(*)"
        ).eq("id", session_id).single().execute()
        
        if not session.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.data['status'] == 'active':
            raise HTTPException(status_code=400, detail="Session already active")
        
        # Update session status
        db.table("lecture_sessions").update({
            "status": "active",
            "actual_start": datetime.now().isoformat()
        }).eq("id", session_id).execute()
        
        # Get enrolled students
        enrollments = db.table("enrollments").select(
            "student_id, profiles(student_id, full_name)"
        ).eq("course_id", session.data['course_id']).execute()
        
        enrolled_students = []
        for enrollment in enrollments.data:
            if enrollment.get('profiles'):
                enrolled_students.append({
                    "user_id": enrollment['student_id'],
                    "student_id": enrollment['profiles']['student_id'],
                    "name": enrollment['profiles']['full_name']
                })
        
        # Initialize attendance records for all enrolled students
        for student in enrolled_students:
            db.table("attendance_records").upsert({
                "session_id": session_id,
                "student_id": student['user_id'],
                "status": "absent",
                "total_checks": 0,
                "confirmed_checks": 0,
                "presence_percentage": 0
            }).execute()
        
        # Get camera RTSP URL
        rtsp_url = session.data.get('classrooms', {}).get('rtsp_url', '')
        
        return {
            "success": True,
            "session_id": session_id,
            "course": session.data.get('courses', {}).get('course_name', ''),
            "classroom": session.data.get('classrooms', {}).get('room_name', ''),
            "rtsp_url": rtsp_url,
            "enrolled_students": len(enrolled_students),
            "start_time": datetime.now().isoformat(),
            "message": "Lecture started. Face recognition engine activated."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/stop")
async def stop_lecture(session_id: str):
    """Stop a lecture session and finalize attendance records."""
    try:
        db = get_supabase()
        
        # Update session status
        db.table("lecture_sessions").update({
            "status": "completed",
            "actual_end": datetime.now().isoformat()
        }).eq("id", session_id).execute()
        
        # Get attendance summary
        records = db.table("attendance_records").select("*").eq(
            "session_id", session_id
        ).execute()
        
        present = sum(1 for r in records.data if r['status'] == 'present')
        absent = sum(1 for r in records.data if r['status'] == 'absent')
        late = sum(1 for r in records.data if r['status'] == 'late')
        
        return {
            "success": True,
            "session_id": session_id,
            "end_time": datetime.now().isoformat(),
            "summary": {
                "total": len(records.data),
                "present": present,
                "absent": absent,
                "late": late
            },
            "records": records.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/delay")
async def delay_lecture(session_id: str, request: DelayLectureRequest):
    """
    Delay a lecture start time (FR11).
    
    Adjusts the scheduled start and extends the end time accordingly.
    """
    try:
        db = get_supabase()
        
        session = db.table("lecture_sessions").select("*").eq(
            "id", session_id
        ).single().execute()
        
        if not session.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Adjust times
        original_start = datetime.fromisoformat(session.data['scheduled_start'])
        original_end = datetime.fromisoformat(session.data['scheduled_end'])
        
        new_start = original_start + timedelta(minutes=request.delay_minutes)
        new_end = original_end + timedelta(minutes=request.delay_minutes)
        
        db.table("lecture_sessions").update({
            "scheduled_start": new_start.isoformat(),
            "scheduled_end": new_end.isoformat(),
            "status": "delayed",
            "notes": f"Delayed by {request.delay_minutes} min. Reason: {request.reason or 'N/A'}"
        }).eq("id", session_id).execute()
        
        return {
            "success": True,
            "session_id": session_id,
            "delay_minutes": request.delay_minutes,
            "new_start": new_start.isoformat(),
            "new_end": new_end.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/appeals")
async def submit_appeal(request: AppealRequest):
    """
    Submit an attendance appeal (room change, delay, etc.).
    """
    try:
        db = get_supabase()
        
        # Get current user (instructor)
        user = db.auth.get_user()
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        appeal_data = {
            "session_id": request.session_id,
            "instructor_id": user.user.id,
            "reason": request.reason,
            "appeal_type": request.appeal_type,
            "status": "pending"
        }
        
        result = db.table("attendance_appeals").insert(appeal_data).execute()
        
        return {
            "success": True,
            "appeal": result.data[0] if result.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appeals")
async def list_appeals(session_id: str = None, status: str = None):
    """List attendance appeals with optional filters."""
    try:
        db = get_supabase()
        
        query = db.table("attendance_appeals").select(
            "*, lecture_sessions(*), profiles(*)"
        )
        
        if session_id:
            query = query.eq("session_id", session_id)
        if status:
            query = query.eq("status", status)
        
        result = query.order("created_at", desc=True).execute()
        
        return {"appeals": result.data, "count": len(result.data)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
