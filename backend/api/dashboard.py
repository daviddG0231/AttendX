"""
AttendX Dashboard API

Provides data for instructor and admin dashboards (FR7-FR11).
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from config.database import get_supabase

router = APIRouter()


@router.get("/instructor/{instructor_id}")
async def instructor_dashboard(instructor_id: str):
    """
    Get instructor dashboard data (FR7).
    
    Returns:
    - Today's lectures
    - Active sessions
    - Recent attendance stats
    - Course overview
    """
    try:
        db = get_supabase()
        
        # Get instructor's courses
        courses = db.table("courses").select("*").eq(
            "instructor_id", instructor_id
        ).execute()
        
        # Get today's sessions
        today = datetime.now().date()
        today_sessions = db.table("lecture_sessions").select(
            "*, courses(course_name, course_code), classrooms(room_name)"
        ).eq("instructor_id", instructor_id).gte(
            "scheduled_start", today.isoformat()
        ).lte(
            "scheduled_start", (today + timedelta(days=1)).isoformat()
        ).execute()
        
        # Get active sessions
        active_sessions = db.table("lecture_sessions").select(
            "*, courses(course_name), classrooms(room_name)"
        ).eq("instructor_id", instructor_id).eq("status", "active").execute()
        
        # Get recent attendance stats (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_sessions = db.table("lecture_sessions").select("id").eq(
            "instructor_id", instructor_id
        ).gte("scheduled_start", week_ago).eq("status", "completed").execute()
        
        total_attendance_rate = 0
        session_count = 0
        
        for session in recent_sessions.data:
            records = db.table("attendance_records").select(
                "status"
            ).eq("session_id", session['id']).execute()
            
            if records.data:
                present = sum(1 for r in records.data if r['status'] in ['present', 'late'])
                rate = present / len(records.data) * 100
                total_attendance_rate += rate
                session_count += 1
        
        avg_attendance = total_attendance_rate / session_count if session_count > 0 else 0
        
        # Pending appeals
        appeals = db.table("attendance_appeals").select("*").eq(
            "instructor_id", instructor_id
        ).eq("status", "pending").execute()
        
        return {
            "instructor_id": instructor_id,
            "courses": {
                "total": len(courses.data),
                "list": courses.data
            },
            "today": {
                "sessions": today_sessions.data,
                "count": len(today_sessions.data)
            },
            "active_sessions": active_sessions.data,
            "stats": {
                "avg_attendance_rate": round(avg_attendance, 1),
                "sessions_this_week": session_count,
                "pending_appeals": len(appeals.data)
            },
            "pending_appeals": appeals.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/student/{student_user_id}")
async def student_dashboard(student_user_id: str):
    """
    Get student dashboard data.
    
    Returns:
    - Enrolled courses
    - Attendance summary per course
    - Today's schedule
    - Alerts for low attendance
    """
    try:
        db = get_supabase()
        
        # Get enrolled courses
        enrollments = db.table("enrollments").select(
            "course_id, courses(course_name, course_code, instructor_id, profiles!courses_instructor_id_fkey(full_name))"
        ).eq("student_id", student_user_id).execute()
        
        course_summaries = []
        
        for enrollment in enrollments.data:
            course = enrollment.get('courses', {})
            course_id = enrollment['course_id']
            
            # Get completed sessions for this course
            sessions = db.table("lecture_sessions").select("id").eq(
                "course_id", course_id
            ).eq("status", "completed").execute()
            
            total_sessions = len(sessions.data)
            session_ids = [s['id'] for s in sessions.data]
            
            # Get student's attendance for these sessions
            if session_ids:
                records = db.table("attendance_records").select(
                    "status"
                ).eq("student_id", student_user_id).in_(
                    "session_id", session_ids
                ).execute()
                
                present = sum(1 for r in records.data if r['status'] in ['present', 'late'])
                rate = present / total_sessions * 100 if total_sessions > 0 else 0
            else:
                present = 0
                rate = 0
            
            course_summaries.append({
                "course_id": course_id,
                "course_name": course.get('course_name', ''),
                "course_code": course.get('course_code', ''),
                "instructor": course.get('profiles', {}).get('full_name', ''),
                "total_sessions": total_sessions,
                "attended": present,
                "attendance_rate": round(rate, 1),
                "status": "good" if rate >= 75 else "warning" if rate >= 50 else "critical"
            })
        
        # Face registration status
        profile = db.table("profiles").select(
            "is_face_registered"
        ).eq("id", student_user_id).single().execute()
        
        return {
            "student_id": student_user_id,
            "is_face_registered": profile.data.get('is_face_registered', False) if profile.data else False,
            "courses": course_summaries,
            "alerts": [
                {
                    "type": "low_attendance",
                    "course": c['course_name'],
                    "rate": c['attendance_rate'],
                    "message": f"Your attendance in {c['course_name']} is {c['attendance_rate']}% - below minimum threshold"
                }
                for c in course_summaries if c['attendance_rate'] < 75 and c['total_sessions'] > 0
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/overview")
async def admin_overview():
    """Admin dashboard with system-wide statistics."""
    try:
        db = get_supabase()
        
        # System stats
        students = db.table("profiles").select("id", count="exact").eq("role", "student").execute()
        instructors = db.table("profiles").select("id", count="exact").eq("role", "instructor").execute()
        courses = db.table("courses").select("id", count="exact").execute()
        classrooms = db.table("classrooms").select("id", count="exact").execute()
        
        # Face registration stats
        face_registered = db.table("profiles").select("id", count="exact").eq(
            "role", "student"
        ).eq("is_face_registered", True).execute()
        
        # Active sessions
        active = db.table("lecture_sessions").select("id", count="exact").eq(
            "status", "active"
        ).execute()
        
        return {
            "system_stats": {
                "total_students": students.count or 0,
                "total_instructors": instructors.count or 0,
                "total_courses": courses.count or 0,
                "total_classrooms": classrooms.count or 0,
                "face_registered_students": face_registered.count or 0,
                "active_sessions": active.count or 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
