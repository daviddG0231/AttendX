# AttendX — AI-Based Attendance System

**Arab Academy for Science, Technology, and Maritime Transport**  
**College of Computing and Information Technology — Smart Village**  
**Graduation Project 2025-2026**

## Overview
AttendX is an AI-powered attendance system that automatically records student attendance via facial recognition from live classroom camera feeds (RTSP). It eliminates manual attendance-taking, prevents proxy attendance, and provides real-time dashboards for instructors.

## Architecture
```
┌─────────────────┐     RTSP Stream     ┌──────────────────────┐
│  IP Cameras     │ ──────────────────→  │  Face Engine (Python) │
│  (720p+ RTSP)   │                      │  • RetinaFace detect  │
└─────────────────┘                      │  • InsightFace align  │
                                         │  • ArcFace embed      │
                                         │  • DeepSORT track     │
                                         │  • SilentFace spoof   │
                                         │  • FAISS match        │
                                         └──────────┬───────────┘
                                                    │
                                                    ▼
┌─────────────────┐     REST API         ┌──────────────────────┐
│  Frontend       │ ◄──────────────────→ │  Backend (FastAPI)    │
│  (Next.js)      │                      │  • Auth (Supabase)    │
│  • Student UI   │                      │  • Attendance CRUD    │
│  • Instructor   │                      │  • Schedule mgmt      │
│  • Dashboard    │                      │  • Face registration  │
└─────────────────┘                      └──────────┬───────────┘
                                                    │
                                                    ▼
                                         ┌──────────────────────┐
                                         │  Supabase             │
                                         │  • PostgreSQL DB      │
                                         │  • Auth               │
                                         │  • Storage (faces)    │
                                         └──────────────────────┘
```

## Quick Start
```bash
# 1. Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload

# 2. Face Engine  
cd face_engine && pip install -r requirements.txt
python engine.py

# 3. Frontend
cd frontend && npm install && npm run dev
```

## Tech Stack
- **Face Detection:** RetinaFace
- **Face Recognition:** ArcFace (InsightFace)  
- **Face Tracking:** DeepSORT
- **Anti-Spoofing:** SilentFace
- **Vector Search:** FAISS
- **Backend:** Python FastAPI
- **Database:** Supabase (PostgreSQL)
- **Frontend:** Next.js + TailwindCSS
- **Streaming:** RTSP via OpenCV

## Team
- Ahmed Sherif (221017673)
- Mohamed Sheren (221017843)  
- Youssef Mohamed (221017612)
- Ahmed Mohamed (221004993)
- Mohamed Mostafa (221027785)
- Abdallah Mohamed (221006269)

**Supervised by:** Prof. Atef Ghalwsh
