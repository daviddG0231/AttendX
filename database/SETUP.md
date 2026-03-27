# AttendX — Supabase Database Setup Guide

## Step 1: Create Supabase Project

1. Go to **https://supabase.com** → Sign up / Log in
2. Click **"New Project"**
3. Fill in:
   - **Name:** `attendx`
   - **Password:** (save this! it's your DB password)
   - **Region:** Choose closest to you
4. Click **"Create new project"** → Wait ~2 minutes

## Step 2: Run the Schema

1. In your Supabase dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New query"**
3. Open `schema.sql` from this folder
4. **Copy the ENTIRE file** and paste it in the SQL editor
5. Click **"Run"** (or Ctrl+Enter)
6. You should see: ✅ "Success. No rows returned"

## Step 3: Get Your API Keys

1. Go to **Settings** → **API** (left sidebar)
2. Copy these two values:

```
Project URL:  https://xxxxxxxxxxxxx.supabase.co
anon public:  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx...
```

## Step 4: Create .env File

In the project root (`attendx/`), create a `.env` file:

```env
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx...
```

## Step 5: Create Storage Bucket

1. Go to **Storage** (left sidebar)
2. Click **"New bucket"**
3. Name: `face-images`
4. ✅ Check "Public bucket" (for now, can secure later)
5. Click **"Create bucket"**

## Step 6: Verify Tables

Go to **Table Editor** → You should see these 10 tables:

| # | Table | Purpose |
|---|-------|---------|
| 1 | `profiles` | Student/instructor accounts |
| 2 | `courses` | Course information |
| 3 | `enrollments` | Which students in which courses |
| 4 | `classrooms` | Rooms + RTSP camera URLs |
| 5 | `lecture_schedule` | Weekly recurring schedule |
| 6 | `lecture_sessions` | Actual lecture instances |
| 7 | `attendance_records` | **THE MAIN TABLE** — who attended what |
| 8 | `face_data` | Links to FAISS face embeddings |
| 9 | `attendance_appeals` | Instructor appeals |
| 10 | `system_logs` | System event logs |

## Database Diagram

```
profiles (users)
    │
    ├── courses (instructor_id → profiles.id)
    │       │
    │       ├── enrollments (course_id + student_id)
    │       │
    │       └── lecture_sessions (course_id)
    │               │
    │               ├── attendance_records (session_id + student_id)
    │               │
    │               └── attendance_appeals (session_id)
    │
    ├── face_data (student_id → profiles.id)
    │
    └── classrooms (linked via lecture_sessions)
```

## Security (RLS)

Row Level Security is **enabled automatically**:
- ✅ Students can only see **their own** attendance
- ✅ Instructors can see attendance for **their courses** only
- ✅ System (service role) can write attendance records
- ✅ Instructors can manually override attendance

## Done! 🎉

Now run the backend:
```bash
cd backend
pip install -r requirements.txt
python main.py
# API running at http://localhost:8000/docs
```
