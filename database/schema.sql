-- ============================================
-- AttendX Database Schema for Supabase
-- ============================================
-- 
-- HOW TO USE:
-- 1. Go to https://supabase.com → Create a new project
-- 2. Go to SQL Editor (left sidebar)
-- 3. Paste this ENTIRE file
-- 4. Click "Run"
-- 5. Copy your Project URL + anon key from Settings → API
-- 6. Put them in your .env file
--
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ==========================================
-- 1. PROFILES (extends Supabase Auth)
-- ==========================================
-- Every user (student/instructor/admin) gets a profile
-- Linked to Supabase Auth automatically

CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'instructor', 'admin')),
    student_id TEXT UNIQUE,           -- e.g., "221017673"
    email TEXT UNIQUE NOT NULL,
    department TEXT,
    avatar_url TEXT,
    is_face_registered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- ==========================================
-- 2. COURSES
-- ==========================================

CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_code TEXT NOT NULL UNIQUE,  -- e.g., "CS301"
    course_name TEXT NOT NULL,         -- e.g., "Machine Learning"
    instructor_id UUID REFERENCES profiles(id),
    department TEXT,
    semester TEXT,                      -- e.g., "Fall 2025"
    academic_year TEXT,                 -- e.g., "2025-2026"
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ==========================================
-- 3. ENROLLMENTS (which students in which courses)
-- ==========================================

CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(course_id, student_id)  -- Can't enroll twice
);


-- ==========================================
-- 4. CLASSROOMS & CAMERAS
-- ==========================================

CREATE TABLE IF NOT EXISTS classrooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_name TEXT NOT NULL,           -- e.g., "Hall 5A"
    building TEXT,                      -- e.g., "Building C"
    floor_number INTEGER,
    capacity INTEGER,
    rtsp_url TEXT,                      -- Camera RTSP link: rtsp://admin:pass@192.168.1.100:554/stream
    camera_resolution TEXT DEFAULT '720p',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ==========================================
-- 5. LECTURE SCHEDULE (recurring weekly slots)
-- ==========================================

CREATE TABLE IF NOT EXISTS lecture_schedule (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    classroom_id UUID REFERENCES classrooms(id),
    day_of_week INTEGER CHECK (day_of_week BETWEEN 0 AND 6),  -- 0=Sunday, 6=Saturday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ==========================================
-- 6. LECTURE SESSIONS (actual lecture instances)
-- ==========================================
-- Each time a lecture happens, a session is created

CREATE TABLE IF NOT EXISTS lecture_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id UUID REFERENCES lecture_schedule(id),
    course_id UUID REFERENCES courses(id),
    classroom_id UUID REFERENCES classrooms(id),
    instructor_id UUID REFERENCES profiles(id),
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    actual_start TIMESTAMPTZ,          -- When instructor clicked "Start"
    actual_end TIMESTAMPTZ,            -- When lecture actually ended
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'active', 'completed', 'cancelled', 'delayed')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ==========================================
-- 7. ATTENDANCE RECORDS (the main output!)
-- ==========================================
-- One record per student per lecture session

CREATE TABLE IF NOT EXISTS attendance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES lecture_sessions(id) ON DELETE CASCADE,
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    entry_time TIMESTAMPTZ,                    -- When face was first detected
    presence_percentage DECIMAL(5,2) DEFAULT 0, -- e.g., 85.50%
    total_checks INTEGER DEFAULT 0,             -- How many presence checks happened
    confirmed_checks INTEGER DEFAULT 0,         -- How many the student was seen
    status TEXT DEFAULT 'absent' CHECK (status IN ('present', 'absent', 'late', 'excused')),
    recorded_by TEXT DEFAULT 'system',          -- 'system' (AI) or 'manual' (instructor override)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, student_id)              -- One record per student per session
);


-- ==========================================
-- 8. FACE DATA (links to FAISS embeddings)
-- ==========================================

CREATE TABLE IF NOT EXISTS face_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    image_url TEXT,                     -- Photo stored in Supabase Storage
    embedding_index INTEGER,           -- Position in FAISS index
    quality_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ==========================================
-- 9. ATTENDANCE APPEALS
-- ==========================================
-- Instructors can appeal if room changed, lecture delayed, etc.

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
-- 10. SYSTEM LOGS
-- ==========================================

CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,          -- e.g., 'face_detected', 'session_started', 'spoof_attempt'
    session_id UUID,
    camera_id TEXT,
    details JSONB,                     -- Flexible JSON for any extra data
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ==========================================
-- INDEXES (for fast queries)
-- ==========================================

CREATE INDEX idx_attendance_session ON attendance_records(session_id);
CREATE INDEX idx_attendance_student ON attendance_records(student_id);
CREATE INDEX idx_attendance_status ON attendance_records(status);
CREATE INDEX idx_sessions_course ON lecture_sessions(course_id);
CREATE INDEX idx_sessions_status ON lecture_sessions(status);
CREATE INDEX idx_sessions_instructor ON lecture_sessions(instructor_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_schedule_course ON lecture_schedule(course_id);
CREATE INDEX idx_face_data_student ON face_data(student_id);
CREATE INDEX idx_logs_event ON system_logs(event_type);
CREATE INDEX idx_logs_session ON system_logs(session_id);


-- ==========================================
-- ROW LEVEL SECURITY (RLS)
-- ==========================================
-- This makes sure users can only see their own data!

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;

-- Everyone can read their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Students can see their own attendance only
CREATE POLICY "Students view own attendance" ON attendance_records
    FOR SELECT USING (auth.uid() = student_id);

-- Instructors can see attendance for their courses
CREATE POLICY "Instructors view course attendance" ON attendance_records
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM lecture_sessions ls
            JOIN courses c ON ls.course_id = c.id
            WHERE ls.id = attendance_records.session_id
            AND c.instructor_id = auth.uid()
        )
    );

-- System can insert attendance records (service role)
CREATE POLICY "System inserts attendance" ON attendance_records
    FOR INSERT WITH CHECK (true);

-- Instructors can update attendance (manual overrides)
CREATE POLICY "Instructors update attendance" ON attendance_records
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM lecture_sessions ls
            JOIN courses c ON ls.course_id = c.id
            WHERE ls.id = attendance_records.session_id
            AND c.instructor_id = auth.uid()
        )
    );

-- Everyone can see courses they're enrolled in
CREATE POLICY "View enrolled courses" ON courses
    FOR SELECT USING (
        instructor_id = auth.uid()
        OR EXISTS (
            SELECT 1 FROM enrollments e 
            WHERE e.course_id = courses.id 
            AND e.student_id = auth.uid()
        )
    );

-- Students can see their own enrollments
CREATE POLICY "Students view own enrollments" ON enrollments
    FOR SELECT USING (student_id = auth.uid());


-- ==========================================
-- HELPER FUNCTIONS
-- ==========================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_profiles_updated
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_attendance_updated
    BEFORE UPDATE ON attendance_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Auto-create profile when user signs up
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profiles (id, full_name, email, role)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', 'New User'),
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'role', 'student')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();


-- ==========================================
-- SAMPLE DATA (for testing/demo)
-- ==========================================
-- Uncomment to insert demo data after creating tables

/*
-- Demo instructor
INSERT INTO auth.users (id, email) VALUES ('11111111-1111-1111-1111-111111111111', 'prof.atef@aast.edu');
INSERT INTO profiles (id, full_name, role, email, department)
VALUES ('11111111-1111-1111-1111-111111111111', 'Prof. Atef Ghalwsh', 'instructor', 'prof.atef@aast.edu', 'Computer Science');

-- Demo classroom
INSERT INTO classrooms (id, room_name, building, floor_number, capacity, rtsp_url)
VALUES ('22222222-2222-2222-2222-222222222222', 'Hall 5A', 'Building C', 5, 50, 'rtsp://admin:pass@192.168.1.100:554/stream');

-- Demo course
INSERT INTO courses (id, course_code, course_name, instructor_id, semester, academic_year)
VALUES ('33333333-3333-3333-3333-333333333333', 'CS401', 'Artificial Intelligence', '11111111-1111-1111-1111-111111111111', 'Spring 2026', '2025-2026');
*/


-- ==========================================
-- ✅ DONE! Your database is ready.
-- ==========================================
-- 
-- Next steps:
-- 1. Go to Settings → API in Supabase dashboard
-- 2. Copy "Project URL" and "anon public" key
-- 3. Create .env file:
--      SUPABASE_URL=https://xxxxx.supabase.co
--      SUPABASE_KEY=eyJhbGci.....
-- 4. Go to Storage → Create bucket "face-images" (for student photos)
-- 5. Run the backend: cd backend && python main.py
--
