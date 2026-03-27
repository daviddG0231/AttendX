"""
AttendX Attendance API

Handles attendance record management and reporting.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.database import get_supabase

router = APIRouter()


class UpdateAttendanceRequest(BaseModel):
    status: str  # present, absent, late, excused
    notes: Optional[str] = None


@router.get("/session/{session_id}")
async def get_session_attendance(session_id: str):
    """Get all attendance records for a lecture session (FR8)."""
    try:
        db = get_supabase()
        
        records = db.table("attendance_records").select(
            "*, profiles!attendance_records_student_id_fkey(full_name, student_id, email)"
        ).eq("session_id", session_id).execute()
        
        # Calculate summary
        total = len(records.data)
        present = sum(1 for r in records.data if r['status'] == 'present')
        absent = sum(1 for r in records.data if r['status'] == 'absent')
        late = sum(1 for r in records.data if r['status'] == 'late')
        excused = sum(1 for r in records.data if r['status'] == 'excused')
        
        attendance_rate = (present + late) / total * 100 if total > 0 else 0
        
        return {
            "session_id": session_id,
            "records": records.data,
            "summary": {
                "total": total,
                "present": present,
                "absent": absent,
                "late": late,
                "excused": excused,
                "attendance_rate": round(attendance_rate, 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/course/{course_id}")
async def get_course_attendance(course_id: str):
    """Get attendance overview for an entire course."""
    try:
        db = get_supabase()
        
        # Get all sessions for this course
        sessions = db.table("lecture_sessions").select("id, scheduled_start, status").eq(
            "course_id", course_id
        ).eq("status", "completed").order("scheduled_start").execute()
        
        course_data = []
        
        for session in sessions.data:
            records = db.table("attendance_records").select(
                "student_id, status, presence_percentage"
            ).eq("session_id", session['id']).execute()
            
            total = len(records.data)
            present = sum(1 for r in records.data if r['status'] in ['present', 'late'])
            
            course_data.append({
                "session_id": session['id'],
                "date": session['scheduled_start'],
                "total_students": total,
                "present": present,
                "attendance_rate": round(present / total * 100, 1) if total > 0 else 0
            })
        
        return {
            "course_id": course_id,
            "total_sessions": len(course_data),
            "sessions": course_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{record_id}")
async def update_attendance(record_id: str, request: UpdateAttendanceRequest):
    """Manually update an attendance record (for appeals/corrections)."""
    try:
        db = get_supabase()
        
        update_data = {
            "status": request.status,
            "recorded_by": "manual",
            "updated_at": datetime.now().isoformat()
        }
        
        result = db.table("attendance_records").update(update_data).eq(
            "id", record_id
        ).execute()
        
        if result.data:
            return {
                "success": True,
                "record": result.data[0],
                "message": f"Attendance updated to '{request.status}'"
            }
        
        raise HTTPException(status_code=404, detail="Record not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{course_id}")
async def generate_attendance_report(course_id: str):
    """
    Generate comprehensive attendance report for a course.
    
    Returns per-student attendance statistics across all sessions.
    """
    try:
        db = get_supabase()
        
        # Get all enrolled students
        enrollments = db.table("enrollments").select(
            "student_id, profiles(full_name, student_id, email)"
        ).eq("course_id", course_id).execute()
        
        # Get all completed sessions
        sessions = db.table("lecture_sessions").select("id").eq(
            "course_id", course_id
        ).eq("status", "completed").execute()
        
        total_sessions = len(sessions.data)
        session_ids = [s['id'] for s in sessions.data]
        
        # Build per-student report
        student_reports = []
        
        for enrollment in enrollments.data:
            student_user_id = enrollment['student_id']
            profile = enrollment.get('profiles', {})
            
            # Get attendance records for this student
            records = db.table("attendance_records").select(
                "status, presence_percentage, entry_time"
            ).eq("student_id", student_user_id).in_(
                "session_id", session_ids
            ).execute() if session_ids else type('', (), {'data': []})()
            
            present_count = sum(1 for r in records.data if r['status'] in ['present', 'late'])
            absent_count = sum(1 for r in records.data if r['status'] == 'absent')
            avg_presence = sum(
                r.get('presence_percentage', 0) or 0 for r in records.data
            ) / len(records.data) if records.data else 0
            
            overall_rate = present_count / total_sessions * 100 if total_sessions > 0 else 0
            
            student_reports.append({
                "student_name": profile.get('full_name', 'Unknown'),
                "student_id": profile.get('student_id', ''),
                "email": profile.get('email', ''),
                "total_sessions": total_sessions,
                "sessions_present": present_count,
                "sessions_absent": absent_count,
                "overall_attendance_rate": round(overall_rate, 1),
                "average_presence_percentage": round(avg_presence, 1),
                "status": "good" if overall_rate >= 75 else "warning" if overall_rate >= 50 else "critical"
            })
        
        # Sort by attendance rate
        student_reports.sort(key=lambda x: x['overall_attendance_rate'], reverse=True)
        
        return {
            "course_id": course_id,
            "total_sessions": total_sessions,
            "total_students": len(student_reports),
            "class_average_attendance": round(
                sum(r['overall_attendance_rate'] for r in student_reports) / len(student_reports), 1
            ) if student_reports else 0,
            "students": student_reports,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
