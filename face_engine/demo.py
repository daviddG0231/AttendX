#!/usr/bin/env python3
"""
AttendX Demo Script

Demonstrates the face recognition pipeline using webcam input.
Run this to test the system without RTSP cameras.
"""

import cv2
import numpy as np
import os
import sys
import time
from pathlib import Path

# Setup logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("AttendX Demo")


def demo_webcam():
    """Run face detection demo using laptop webcam."""
    
    print("=" * 60)
    print("  AttendX - Face Recognition Demo")
    print("  Using webcam for real-time face detection")
    print("=" * 60)
    print()
    
    try:
        from face_detector import FaceDetector, AntiSpoofDetector
        from face_matcher import FaceMatcher
    except ImportError:
        print("❌ Failed to import face engine modules.")
        print("   Make sure you're running from the face_engine directory.")
        return
    
    # Initialize components
    print("🔧 Initializing face detector...")
    try:
        detector = FaceDetector(det_thresh=0.5, device="cpu")
        print("✅ Face detector ready")
    except Exception as e:
        print(f"❌ Failed to initialize face detector: {e}")
        print("   Try: pip install insightface onnxruntime")
        return
    
    anti_spoof = AntiSpoofDetector(threshold=0.5)
    matcher = FaceMatcher()
    matcher.load_index()
    
    print(f"📊 Registered students: {matcher.num_registered}")
    print()
    
    # Open webcam
    print("📷 Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Failed to open webcam")
        return
    
    print("✅ Webcam ready")
    print()
    print("Controls:")
    print("  [r] Register current face as new student")
    print("  [s] Take screenshot")
    print("  [q] Quit")
    print()
    
    frame_count = 0
    fps_start = time.time()
    current_fps = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Calculate FPS
        elapsed = time.time() - fps_start
        if elapsed >= 1.0:
            current_fps = frame_count / elapsed
            frame_count = 0
            fps_start = time.time()
        
        # Process every 3rd frame for performance
        if frame_count % 3 == 0:
            # Detect faces
            faces = detector.detect_faces(frame)
            
            # Process each detected face
            names = []
            for face in faces:
                # Anti-spoofing check
                is_real, spoof_score = anti_spoof.is_real_face(face.get('aligned_face'))
                
                if not is_real:
                    names.append(f"SPOOF ({spoof_score:.2f})")
                    continue
                
                # Try to identify
                matches = matcher.identify(face['embedding'])
                
                if matches:
                    student_id, name, confidence = matches[0]
                    names.append(f"{name} ({confidence:.2f})")
                else:
                    names.append(None)
            
            # Draw results
            display_frame = detector.draw_detections(frame, faces, names)
        else:
            display_frame = frame
        
        # Draw FPS counter
        cv2.putText(display_frame, f"FPS: {current_fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw registration count
        cv2.putText(display_frame, f"Registered: {matcher.num_registered}", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show frame
        cv2.imshow("AttendX Demo - Face Recognition", display_frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        
        elif key == ord('r'):
            # Register current face
            if faces and len(faces) == 1:
                student_name = input("\n📝 Enter student name: ").strip()
                student_id = input("📝 Enter student ID: ").strip()
                
                if student_name and student_id:
                    # Collect 5 frames for registration
                    print("📸 Collecting face samples... Look at the camera from different angles")
                    embeddings = []
                    
                    for i in range(10):
                        ret, reg_frame = cap.read()
                        if ret:
                            reg_faces = detector.detect_faces(reg_frame)
                            if reg_faces:
                                embeddings.append(reg_faces[0]['embedding'])
                                print(f"  ✅ Sample {len(embeddings)}/5 captured")
                        time.sleep(0.3)
                        
                        if len(embeddings) >= 5:
                            break
                    
                    if len(embeddings) >= 3:
                        success = matcher.register_student(student_id, student_name, embeddings)
                        if success:
                            matcher.save_index()
                            print(f"✅ {student_name} registered successfully!")
                        else:
                            print("❌ Registration failed")
                    else:
                        print(f"❌ Only {len(embeddings)} samples captured (need at least 3)")
            else:
                print("⚠️  Please ensure exactly one face is visible for registration")
        
        elif key == ord('s'):
            # Screenshot
            filename = f"screenshot_{int(time.time())}.jpg"
            cv2.imwrite(filename, display_frame)
            print(f"📸 Screenshot saved: {filename}")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("\n👋 Demo ended")


def demo_from_image(image_path: str):
    """Run face detection on a single image."""
    
    print(f"🖼️  Processing image: {image_path}")
    
    from face_detector import FaceDetector
    from face_matcher import FaceMatcher
    
    detector = FaceDetector()
    matcher = FaceMatcher()
    matcher.load_index()
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Failed to load image: {image_path}")
        return
    
    # Detect faces
    faces = detector.detect_faces(img)
    print(f"📊 Detected {len(faces)} face(s)")
    
    # Identify each face
    names = []
    for i, face in enumerate(faces):
        matches = matcher.identify(face['embedding'])
        if matches:
            sid, name, conf = matches[0]
            print(f"  Face {i+1}: {name} (confidence: {conf:.3f})")
            names.append(f"{name} ({conf:.2f})")
        else:
            print(f"  Face {i+1}: Unknown")
            names.append(None)
    
    # Draw and save result
    result = detector.draw_detections(img, faces, names)
    output_path = f"result_{Path(image_path).stem}.jpg"
    cv2.imwrite(output_path, result)
    print(f"💾 Result saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Process image file
        demo_from_image(sys.argv[1])
    else:
        # Webcam demo
        demo_webcam()
