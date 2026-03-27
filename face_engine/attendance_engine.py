"""
AttendX Attendance Engine

Core orchestrator that combines face detection, recognition, tracking,
and anti-spoofing into a unified attendance processing pipeline.

Implements Option 3 design: Entry Detection + Periodic Presence Verification
"""

import time
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, field, asdict
import threading
import logging

from face_detector import FaceDetector, AntiSpoofDetector
from face_matcher import FaceMatcher
from camera_stream import CameraStream, MultiCameraManager
import config

logger = logging.getLogger(__name__)


@dataclass
class StudentPresence:
    """Track a student's presence throughout a lecture."""
    student_id: str
    student_name: str
    entry_time: Optional[datetime] = None
    presence_checks: List[datetime] = field(default_factory=list)
    total_checks: int = 0
    confirmed_checks: int = 0
    is_present: bool = False
    attendance_percentage: float = 0.0
    final_status: str = "absent"  # "present", "absent", "late"
    
    def update_presence(self, check_time: datetime):
        """Record a successful presence check."""
        self.presence_checks.append(check_time)
        self.confirmed_checks += 1
        self.is_present = True
    
    def calculate_attendance(self, lecture_duration_minutes: int):
        """Calculate final attendance percentage."""
        if self.total_checks == 0:
            self.attendance_percentage = 0.0
            self.final_status = "absent"
            return
        
        self.attendance_percentage = (self.confirmed_checks / self.total_checks) * 100
        
        if self.attendance_percentage >= config.PRESENCE_THRESHOLD * 100:
            self.final_status = "present"
        else:
            self.final_status = "absent"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API/storage."""
        return {
            'student_id': self.student_id,
            'student_name': self.student_name,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'presence_checks': [t.isoformat() for t in self.presence_checks],
            'total_checks': self.total_checks,
            'confirmed_checks': self.confirmed_checks,
            'attendance_percentage': round(self.attendance_percentage, 1),
            'final_status': self.final_status
        }


@dataclass
class LectureSession:
    """Represents an active lecture session being monitored."""
    session_id: str
    course_id: str
    course_name: str
    instructor_id: str
    classroom_id: str
    camera_id: str
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    is_active: bool = False
    students: Dict[str, StudentPresence] = field(default_factory=dict)
    total_presence_checks: int = 0


class AttendanceEngine:
    """
    Main attendance processing engine.
    
    Orchestrates the full pipeline:
    1. Camera stream capture
    2. Face detection (RetinaFace)
    3. Face alignment (InsightFace)
    4. Face recognition (ArcFace + FAISS)
    5. Face tracking (DeepSORT)
    6. Anti-spoofing (SilentFace)
    7. Entry detection + periodic presence verification
    8. Attendance calculation and recording
    """
    
    def __init__(self):
        """Initialize all engine components."""
        logger.info("🚀 Initializing AttendX Attendance Engine...")
        
        # Core components
        self.face_detector = FaceDetector(
            det_thresh=config.FACE_DETECTION_THRESHOLD,
            device=config.DEVICE
        )
        self.face_matcher = FaceMatcher(
            threshold=config.FACE_RECOGNITION_THRESHOLD
        )
        self.anti_spoof = AntiSpoofDetector(
            threshold=config.ANTI_SPOOF_THRESHOLD
        )
        self.camera_manager = MultiCameraManager()
        
        # Active lecture sessions
        self.active_sessions: Dict[str, LectureSession] = {}
        
        # Processing thread
        self._processing_thread: Optional[threading.Thread] = None
        self._is_running = False
        
        # Load existing face index
        self.face_matcher.load_index()
        
        logger.info("✅ AttendX Engine initialized")
        logger.info(f"   📊 Registered students: {self.face_matcher.num_registered}")
    
    def register_student(self, student_id: str, student_name: str,
                        face_images: List[np.ndarray]) -> Dict[str, Any]:
        """
        Register a new student with their face images.
        
        Per project requirements: minimum 5 facial images under
        different lighting and pose conditions.
        
        Args:
            student_id: Unique student identifier
            student_name: Student's display name
            face_images: List of face images (minimum 5 recommended)
            
        Returns:
            Registration result dictionary
        """
        if len(face_images) < 5:
            logger.warning(f"Student {student_id} provided {len(face_images)} images "
                         f"(minimum 5 recommended)")
        
        # Extract embeddings from all face images
        embeddings = []
        for i, img in enumerate(face_images):
            embedding = self.face_detector.get_embedding(img)
            if embedding is not None:
                embeddings.append(embedding)
                logger.info(f"  ✅ Image {i+1}: embedding extracted")
            else:
                logger.warning(f"  ⚠️  Image {i+1}: no face detected")
        
        if not embeddings:
            return {
                'success': False,
                'message': 'No faces detected in any of the provided images',
                'student_id': student_id
            }
        
        # Register in FAISS index
        success = self.face_matcher.register_student(student_id, student_name, embeddings)
        
        if success:
            # Save updated index
            self.face_matcher.save_index()
            
            return {
                'success': True,
                'message': f'Student registered successfully with {len(embeddings)} face embeddings',
                'student_id': student_id,
                'student_name': student_name,
                'embeddings_count': len(embeddings),
                'images_provided': len(face_images)
            }
        
        return {
            'success': False,
            'message': 'Failed to register student in face index',
            'student_id': student_id
        }
    
    def start_lecture_session(self, session_id: str, course_id: str, 
                            course_name: str, instructor_id: str,
                            classroom_id: str, camera_rtsp_url: str,
                            duration_minutes: int = 90,
                            enrolled_student_ids: List[str] = None) -> Dict[str, Any]:
        """
        Start monitoring a new lecture session.
        
        Args:
            session_id: Unique session identifier
            course_id: Course code
            course_name: Course name
            instructor_id: Instructor's ID
            classroom_id: Classroom identifier
            camera_rtsp_url: RTSP URL for classroom camera
            duration_minutes: Lecture duration in minutes
            enrolled_student_ids: List of enrolled student IDs
            
        Returns:
            Session start result
        """
        now = datetime.now()
        
        # Create lecture session
        session = LectureSession(
            session_id=session_id,
            course_id=course_id,
            course_name=course_name,
            instructor_id=instructor_id,
            classroom_id=classroom_id,
            camera_id=f"cam_{classroom_id}",
            scheduled_start=now,
            scheduled_end=now + timedelta(minutes=duration_minutes),
            actual_start=now,
            is_active=True
        )
        
        # Initialize student presence tracking
        if enrolled_student_ids:
            for sid in enrolled_student_ids:
                name = self.face_matcher.student_names.get(sid, "Unknown")
                session.students[sid] = StudentPresence(
                    student_id=sid,
                    student_name=name
                )
        
        # Connect camera
        camera_id = f"cam_{classroom_id}"
        self.camera_manager.add_camera(camera_id, camera_rtsp_url)
        
        # Store session
        self.active_sessions[session_id] = session
        
        # Start processing
        if not self._is_running:
            self._start_processing()
        
        logger.info(f"🎓 Lecture session started: {course_name} ({session_id})")
        logger.info(f"   📷 Camera: {camera_id}")
        logger.info(f"   👥 Enrolled students: {len(enrolled_student_ids or [])}")
        logger.info(f"   ⏱️  Duration: {duration_minutes} minutes")
        
        return {
            'success': True,
            'session_id': session_id,
            'course_name': course_name,
            'start_time': now.isoformat(),
            'end_time': session.scheduled_end.isoformat(),
            'camera_status': self.camera_manager.get_status().get(camera_id, {})
        }
    
    def stop_lecture_session(self, session_id: str) -> Dict[str, Any]:
        """
        Stop a lecture session and calculate final attendance.
        
        Returns:
            Final attendance results for all students
        """
        if session_id not in self.active_sessions:
            return {'success': False, 'message': 'Session not found'}
        
        session = self.active_sessions[session_id]
        session.is_active = False
        session.actual_end = datetime.now()
        
        # Calculate lecture duration in minutes
        duration = (session.actual_end - session.actual_start).total_seconds() / 60
        
        # Calculate final attendance for all students
        attendance_results = []
        for student_id, presence in session.students.items():
            presence.total_checks = session.total_presence_checks
            presence.calculate_attendance(int(duration))
            attendance_results.append(presence.to_dict())
        
        # Stop camera
        self.camera_manager.remove_camera(session.camera_id)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        # Check if we should stop processing
        if not self.active_sessions:
            self._stop_processing()
        
        logger.info(f"🏁 Lecture session ended: {session.course_name}")
        logger.info(f"   ⏱️  Duration: {duration:.0f} minutes")
        logger.info(f"   📊 Presence checks: {session.total_presence_checks}")
        
        present_count = sum(1 for r in attendance_results if r['final_status'] == 'present')
        logger.info(f"   ✅ Present: {present_count}/{len(attendance_results)}")
        
        return {
            'success': True,
            'session_id': session_id,
            'course_name': session.course_name,
            'duration_minutes': round(duration, 1),
            'total_presence_checks': session.total_presence_checks,
            'attendance': attendance_results,
            'summary': {
                'total_students': len(attendance_results),
                'present': present_count,
                'absent': len(attendance_results) - present_count
            }
        }
    
    def _start_processing(self):
        """Start the background processing loop."""
        self._is_running = True
        self._processing_thread = threading.Thread(
            target=self._processing_loop, daemon=True
        )
        self._processing_thread.start()
        logger.info("🔄 Processing loop started")
    
    def _stop_processing(self):
        """Stop the background processing loop."""
        self._is_running = False
        if self._processing_thread:
            self._processing_thread.join(timeout=10)
        logger.info("⏹️  Processing loop stopped")
    
    def _processing_loop(self):
        """
        Main processing loop.
        
        For each active session:
        1. Grab frame from camera
        2. Detect faces
        3. Check anti-spoofing
        4. Identify students
        5. Update presence records
        """
        last_presence_check = {}  # session_id -> last check time
        
        while self._is_running:
            for session_id, session in list(self.active_sessions.items()):
                if not session.is_active:
                    continue
                
                try:
                    # Get frame from camera
                    frame = self.camera_manager.get_frame(session.camera_id)
                    if frame is None:
                        continue
                    
                    # Detect faces
                    faces = self.face_detector.detect_faces(frame)
                    
                    if not faces:
                        continue
                    
                    # Process each detected face
                    for face in faces:
                        # Anti-spoofing check
                        if config.ANTI_SPOOF_ENABLED:
                            is_real, spoof_score = self.anti_spoof.is_real_face(
                                face.get('aligned_face')
                            )
                            if not is_real:
                                logger.warning(f"⚠️  Spoofing attempt detected "
                                             f"(score: {spoof_score:.2f})")
                                continue
                        
                        # Identify student
                        matches = self.face_matcher.identify(face['embedding'])
                        
                        if matches:
                            student_id, student_name, confidence = matches[0]
                            now = datetime.now()
                            
                            # Check if this is a new entry or presence confirmation
                            if student_id in session.students:
                                presence = session.students[student_id]
                                
                                # Record entry time (first detection)
                                if presence.entry_time is None:
                                    presence.entry_time = now
                                    logger.info(f"🚪 Entry detected: {student_name} "
                                              f"({student_id}) at {now.strftime('%H:%M:%S')}")
                                
                                # Periodic presence check
                                presence.update_presence(now)
                    
                    # Periodic presence check counter
                    now = datetime.now()
                    last_check = last_presence_check.get(session_id, session.actual_start)
                    
                    if (now - last_check).total_seconds() >= config.PRESENCE_CHECK_INTERVAL:
                        session.total_presence_checks += 1
                        last_presence_check[session_id] = now
                        logger.info(f"📋 Presence check #{session.total_presence_checks} "
                                  f"for {session.course_name}")
                    
                    # Check if lecture time is over
                    if now >= session.scheduled_end:
                        logger.info(f"⏰ Lecture time ended for {session.course_name}")
                        self.stop_lecture_session(session_id)
                
                except Exception as e:
                    logger.error(f"Processing error for session {session_id}: {e}")
            
            # Small delay to prevent CPU overuse
            time.sleep(0.1)
    
    def process_single_frame(self, frame: np.ndarray, session_id: str = None) -> Dict[str, Any]:
        """
        Process a single frame (for testing/demo purposes).
        
        Args:
            frame: BGR image
            session_id: Optional session to update
            
        Returns:
            Detection and identification results
        """
        # Detect faces
        faces = self.face_detector.detect_faces(frame)
        
        results = {
            'faces_detected': len(faces),
            'identifications': [],
            'unknown_faces': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        for face in faces:
            # Anti-spoofing
            is_real, spoof_score = self.anti_spoof.is_real_face(face.get('aligned_face'))
            
            if not is_real:
                results['unknown_faces'] += 1
                continue
            
            # Identify
            matches = self.face_matcher.identify(face['embedding'])
            
            if matches:
                student_id, student_name, confidence = matches[0]
                results['identifications'].append({
                    'student_id': student_id,
                    'student_name': student_name,
                    'confidence': round(confidence, 3),
                    'bbox': face['bbox'],
                    'is_real': is_real,
                    'spoof_score': round(spoof_score, 3)
                })
            else:
                results['unknown_faces'] += 1
        
        return results
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a lecture session."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        now = datetime.now()
        elapsed = (now - session.actual_start).total_seconds() / 60 if session.actual_start else 0
        
        present_students = []
        absent_students = []
        
        for sid, presence in session.students.items():
            if presence.entry_time is not None:
                present_students.append(presence.to_dict())
            else:
                absent_students.append(presence.to_dict())
        
        return {
            'session_id': session_id,
            'course_name': session.course_name,
            'is_active': session.is_active,
            'elapsed_minutes': round(elapsed, 1),
            'remaining_minutes': max(0, round(
                (session.scheduled_end - now).total_seconds() / 60, 1
            )),
            'total_presence_checks': session.total_presence_checks,
            'present_count': len(present_students),
            'absent_count': len(absent_students),
            'present_students': present_students,
            'absent_students': absent_students,
            'camera_status': self.camera_manager.get_status().get(session.camera_id, {})
        }
    
    def shutdown(self):
        """Gracefully shutdown the engine."""
        logger.info("🛑 Shutting down AttendX Engine...")
        
        # Stop all active sessions
        for session_id in list(self.active_sessions.keys()):
            self.stop_lecture_session(session_id)
        
        # Stop processing
        self._stop_processing()
        
        # Stop all cameras
        self.camera_manager.stop_all()
        
        # Save face index
        self.face_matcher.save_index()
        
        logger.info("✅ AttendX Engine shutdown complete")
