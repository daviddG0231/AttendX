"""
AttendX Database Configuration — Supabase Client
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Client = None


def get_supabase() -> Client:
    """Get or create Supabase client instance."""
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables. "
                "Create a .env file with these values."
            )
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase


# SQL Schema for Supabase (run this in Supabase SQL Editor)
SCHEMA_SQL = """
-- ============================================
-- AttendX Database Schema for Supabase
-- Run this in Supabase SQL Editor
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. Users Table (extends Supabase Auth)
-- ==========================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'instructor', 'admin')),
    student_id TEXT UNIQUE,  -- University registration number
    email TEXT UNIQUE NOT NULL,
    department TEXT,
    avatar_url TEXT,
    is_face_registered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 2. Courses Table
-- ==========================================
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_code TEXT NOT NULL UNIQUE,
    course_name TEXT NOT NULL,
    instructor_id UUID REFERENCES profiles(id),
    department TEXT,
    semester TEXT,
    academic_year TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 3. Course Enrollments
-- ==========================================
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(course_id, student_id)
);

-- ==========================================
-- 4. Classrooms & Cameras
-- ==========================================
CREATE TABLE IF NOT EXISTS classrooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_name TEXT NOT NULL,
    building TEXT,
    floor_number INTEGER,
    capacity INTEGER,
    rtsp_url TEXT,  -- Camera RTSP link
    camera_resolution TEXT DEFAULT '720p',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 5. Lecture Schedule
-- ==========================================
CREATE TABLE IF NOT EXISTS lecture_schedule (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    classroom_id UUID REFERENCES classrooms(id),
    day_of_week INTEGER CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 6. Lecture Sessions (actual instances)
-- ==========================================
CREATE TABLE IF NOT EXISTS lecture_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id UUID REFERENCES lecture_schedule(id),
    course_id UUID REFERENCES courses(id),
    classroom_id UUID REFERENCES classrooms(id),
    instructor_id UUID REFERENCES profiles(id),
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    actual_start TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'active', 'completed', 'cancelled', 'delayed')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 7. Attendance Records
-- ==========================================
CREATE TABLE IF NOT EXISTS attendance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES lecture_sessions(id) ON DELETE CASCADE,
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    entry_time TIMESTAMPTZ,
    presence_percentage DECIMAL(5,2) DEFAULT 0,
    total_checks INTEGER DEFAULT 0,
    confirmed_checks INTEGER DEFAULT 0,
    status TEXT DEFAULT 'absent' CHECK (status IN ('present', 'absent', 'late', 'excused')),
    recorded_by TEXT DEFAULT 'system',  -- 'system' or 'manual'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, student_id)
);

-- ==========================================
-- 8. Face Data (embeddings reference)
-- ==========================================
CREATE TABLE IF NOT EXISTS face_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    image_url TEXT,  -- Stored in Supabase Storage
    embedding_index INTEGER,  -- Index in FAISS
    quality_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 9. Attendance Appeals
-- ==========================================
CREATE TABLE IF NOT EXISTS attendance_appeals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES lecture_sessions(id),
    instructor_id UUID REFERENCES profiles(id),
    reason TEXT NOT NULL,
    appeal_type TEXT CHECK (appeal_type IN ('room_change', 'delay', 'technical_issue', 'other')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- ==========================================
-- 10. System Logs
-- ==========================================
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    session_id UUID,
    camera_id TEXT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- Indexes for Performance
-- ==========================================
CREATE INDEX idx_attendance_session ON attendance_records(session_id);
CREATE INDEX idx_attendance_student ON attendance_records(student_id);
CREATE INDEX idx_sessions_course ON lecture_sessions(course_id);
CREATE INDEX idx_sessions_status ON lecture_sessions(status);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_schedule_course ON lecture_schedule(course_id);
CREATE INDEX idx_face_data_student ON face_data(student_id);

-- ==========================================
-- Row Level Security (RLS)
-- ==========================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;

-- Students can view their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

-- Students can view their own attendance
CREATE POLICY "Students can view own attendance" ON attendance_records
    FOR SELECT USING (auth.uid() = student_id);

-- Instructors can view attendance for their courses
CREATE POLICY "Instructors can view course attendance" ON attendance_records
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM lecture_sessions ls
            JOIN courses c ON ls.course_id = c.id
            WHERE ls.id = attendance_records.session_id
            AND c.instructor_id = auth.uid()
        )
    );
"""
