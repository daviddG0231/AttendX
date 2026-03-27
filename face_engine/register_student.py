#!/usr/bin/env python3
"""
AttendX — Student Face Registration Tool

Standalone script to register students by providing 5+ face images.
Supports both file uploads and webcam capture.

Usage:
    # From image files:
    python register_student.py --name "Ahmed Sherif" --id 221017673 --images photo1.jpg photo2.jpg photo3.jpg photo4.jpg photo5.jpg

    # From a folder of images:
    python register_student.py --name "Ahmed Sherif" --id 221017673 --folder ./ahmed_photos/

    # From webcam (interactive):
    python register_student.py --name "Ahmed Sherif" --id 221017673 --webcam
"""

import os
import sys
import cv2
import time
import json
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("AttendX Register")

# Minimum required images
MIN_IMAGES = 5


def load_face_engine():
    """Load the face detection and matching modules."""
    try:
        from face_detector import FaceDetector, AntiSpoofDetector
        from face_matcher import FaceMatcher
        return FaceDetector, AntiSpoofDetector, FaceMatcher
    except ImportError as e:
        logger.error(f"Failed to import face engine: {e}")
        logger.error("Make sure you're running from the face_engine/ directory")
        logger.error("Install dependencies: pip install -r requirements.txt")
        sys.exit(1)


def register_from_images(name: str, student_id: str, image_paths: list):
    """
    Register a student using image file paths.
    
    Args:
        name: Student's full name
        student_id: University registration number
        image_paths: List of paths to face images (minimum 5)
    """
    FaceDetector, AntiSpoofDetector, FaceMatcher = load_face_engine()
    
    print()
    print("=" * 60)
    print("  AttendX — Student Face Registration")
    print("=" * 60)
    print(f"  👤 Name:       {name}")
    print(f"  🆔 Student ID: {student_id}")
    print(f"  📸 Images:     {len(image_paths)} provided")
    print("=" * 60)
    print()
    
    # Validate minimum images
    if len(image_paths) < MIN_IMAGES:
        print(f"❌ ERROR: Minimum {MIN_IMAGES} images required!")
        print(f"   You provided: {len(image_paths)}")
        print(f"   Please provide at least {MIN_IMAGES} photos taken under different conditions:")
        print(f"     1. Looking straight at camera")
        print(f"     2. Slight left turn")
        print(f"     3. Slight right turn")
        print(f"     4. Different lighting")
        print(f"     5. With/without glasses or accessories")
        return False
    
    # Initialize face engine
    print("🔧 Loading face recognition models...")
    detector = FaceDetector(det_thresh=0.5, device="cpu")
    anti_spoof = AntiSpoofDetector()
    matcher = FaceMatcher()
    matcher.load_index()
    print(f"✅ Models loaded. Currently {matcher.num_registered} students registered.")
    print()
    
    # Check if student already registered
    if student_id in matcher.student_ids:
        print(f"⚠️  Student {student_id} is already registered as '{matcher.student_names[student_id]}'")
        response = input("   Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Registration cancelled.")
            return False
        matcher.remove_student(student_id)
        print("   Old registration removed.")
    
    # Process each image
    embeddings = []
    results = []
    
    print(f"📸 Processing {len(image_paths)} images...")
    print("-" * 50)
    
    for i, image_path in enumerate(image_paths):
        print(f"\n  [{i+1}/{len(image_paths)}] {os.path.basename(image_path)}")
        
        # Check file exists
        if not os.path.exists(image_path):
            print(f"      ❌ File not found: {image_path}")
            results.append({"file": image_path, "status": "not_found"})
            continue
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            print(f"      ❌ Failed to read image (corrupted or unsupported format)")
            results.append({"file": image_path, "status": "read_error"})
            continue
        
        print(f"      📐 Image size: {img.shape[1]}x{img.shape[0]}")
        
        # Detect faces
        faces = detector.detect_faces(img)
        
        if not faces:
            print(f"      ❌ No face detected — make sure face is clearly visible")
            results.append({"file": image_path, "status": "no_face"})
            continue
        
        if len(faces) > 1:
            print(f"      ⚠️  {len(faces)} faces detected — using the largest one")
            # Pick the largest face (biggest bounding box area)
            faces.sort(key=lambda f: (f['bbox'][2]-f['bbox'][0]) * (f['bbox'][3]-f['bbox'][1]), reverse=True)
        
        face = faces[0]
        
        # Anti-spoofing check
        is_real, spoof_score = anti_spoof.is_real_face(face.get('aligned_face'))
        
        if not is_real:
            print(f"      ❌ Spoofing detected (score: {spoof_score:.2f}) — use a real photo, not a screen")
            results.append({"file": image_path, "status": "spoof_detected"})
            continue
        
        # Extract embedding
        embedding = face['embedding']
        embeddings.append(embedding)
        
        confidence = face['det_score']
        print(f"      ✅ Face detected (confidence: {confidence:.3f})")
        print(f"      ✅ Liveness check passed (score: {spoof_score:.2f})")
        print(f"      ✅ Embedding extracted (512-d vector)")
        
        results.append({
            "file": image_path, 
            "status": "success",
            "confidence": confidence,
            "spoof_score": spoof_score
        })
        
        # Save annotated image for verification
        output_dir = Path("registrations") / student_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        annotated = detector.draw_detections(img, [face], [name])
        cv2.imwrite(str(output_dir / f"face_{i+1}.jpg"), annotated)
    
    print()
    print("-" * 50)
    
    # Summary
    successful = len(embeddings)
    failed = len(image_paths) - successful
    
    print(f"\n📊 Processing Summary:")
    print(f"   ✅ Successful: {successful}/{len(image_paths)}")
    print(f"   ❌ Failed:     {failed}/{len(image_paths)}")
    
    if successful < 3:
        print(f"\n❌ REGISTRATION FAILED")
        print(f"   Need at least 3 successful face extractions, got {successful}")
        print(f"   Please provide clearer photos and try again.")
        return False
    
    if successful < MIN_IMAGES:
        print(f"\n⚠️  WARNING: Only {successful} embeddings (recommended: {MIN_IMAGES}+)")
        print(f"   Registration will proceed but accuracy may be lower.")
    
    # Register in FAISS index
    print(f"\n🔐 Registering {name} in face database...")
    
    success = matcher.register_student(student_id, name, embeddings)
    
    if not success:
        print("❌ REGISTRATION FAILED — could not add to face index")
        return False
    
    # Save index to disk
    matcher.save_index()
    
    # Save registration metadata
    metadata = {
        "student_id": student_id,
        "student_name": name,
        "registered_at": datetime.now().isoformat(),
        "total_images": len(image_paths),
        "successful_embeddings": successful,
        "failed_images": failed,
        "results": results,
        "total_registered": matcher.num_registered
    }
    
    metadata_path = Path("registrations") / student_id / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    print()
    print("=" * 60)
    print(f"  ✅ REGISTRATION SUCCESSFUL!")
    print("=" * 60)
    print(f"  👤 Name:          {name}")
    print(f"  🆔 Student ID:    {student_id}")
    print(f"  📸 Embeddings:    {successful}")
    print(f"  📁 Files saved:   registrations/{student_id}/")
    print(f"  🗂️  Total in DB:   {matcher.num_registered} students")
    print("=" * 60)
    print()
    
    return True


def register_from_folder(name: str, student_id: str, folder_path: str):
    """Register using all images in a folder."""
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        return False
    
    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    image_paths = sorted([
        str(f) for f in folder.iterdir() 
        if f.suffix.lower() in image_extensions
    ])
    
    if not image_paths:
        print(f"❌ No images found in {folder_path}")
        print(f"   Supported formats: {', '.join(image_extensions)}")
        return False
    
    print(f"📂 Found {len(image_paths)} images in {folder_path}")
    
    return register_from_images(name, student_id, image_paths)


def register_from_webcam(name: str, student_id: str):
    """Register by capturing photos from webcam."""
    
    FaceDetector, AntiSpoofDetector, FaceMatcher = load_face_engine()
    
    print()
    print("=" * 60)
    print("  AttendX — Webcam Face Registration")
    print("=" * 60)
    print(f"  👤 Name:       {name}")
    print(f"  🆔 Student ID: {student_id}")
    print("=" * 60)
    print()
    print("📷 Opening webcam...")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open webcam")
        return False
    
    print("✅ Webcam ready")
    print()
    print("Instructions:")
    print(f"  We need {MIN_IMAGES} photos. After each capture, change your pose slightly.")
    print("  Press [SPACE] to capture a photo")
    print("  Press [q] to cancel")
    print()
    
    # Initialize
    detector = FaceDetector(det_thresh=0.5, device="cpu")
    
    captured_images = []
    output_dir = Path("registrations") / student_id / "webcam_captures"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    poses = [
        "Look STRAIGHT at the camera",
        "Turn your head SLIGHTLY LEFT",
        "Turn your head SLIGHTLY RIGHT", 
        "TILT your head slightly",
        "SMILE naturally"
    ]
    
    capture_count = 0
    
    while capture_count < MIN_IMAGES:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect faces for live preview
        faces = detector.detect_faces(frame)
        
        # Draw UI overlay
        display = frame.copy()
        
        # Draw instruction
        pose_instruction = poses[capture_count] if capture_count < len(poses) else "Any natural pose"
        
        # Top bar
        cv2.rectangle(display, (0, 0), (display.shape[1], 80), (0, 0, 0), -1)
        cv2.putText(display, f"AttendX Registration - {name}", (15, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display, f"Photo {capture_count + 1}/{MIN_IMAGES}: {pose_instruction}", (15, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        
        # Face detection indicator
        if faces:
            face = faces[0]
            x1, y1, x2, y2 = face['bbox']
            color = (0, 255, 0)  # Green = face detected, ready to capture
            cv2.rectangle(display, (x1, y1), (x2, y2), color, 3)
            cv2.putText(display, "Face OK - Press SPACE", (15, display.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(display, "No face detected - center your face", (15, display.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Progress bar
        progress = int((capture_count / MIN_IMAGES) * (display.shape[1] - 30))
        cv2.rectangle(display, (15, display.shape[0] - 50), (15 + progress, display.shape[0] - 40), (0, 255, 0), -1)
        cv2.rectangle(display, (15, display.shape[0] - 50), (display.shape[1] - 15, display.shape[0] - 40), (100, 100, 100), 1)
        
        cv2.imshow("AttendX Registration", display)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\n❌ Registration cancelled by user")
            cap.release()
            cv2.destroyAllWindows()
            return False
        
        if key == ord(' ') and faces:
            # Capture!
            capture_count += 1
            
            # Save the raw image
            img_path = str(output_dir / f"capture_{capture_count}.jpg")
            cv2.imwrite(img_path, frame)
            captured_images.append(img_path)
            
            print(f"  📸 Photo {capture_count}/{MIN_IMAGES} captured! ({pose_instruction})")
            
            # Brief flash effect
            flash = np.ones_like(display) * 255
            cv2.imshow("AttendX Registration", flash)
            cv2.waitKey(200)
    
    cap.release()
    cv2.destroyAllWindows()
    
    if len(captured_images) < MIN_IMAGES:
        print(f"\n❌ Only captured {len(captured_images)}/{MIN_IMAGES} photos")
        return False
    
    print(f"\n✅ All {MIN_IMAGES} photos captured!")
    print("🔄 Processing registration...\n")
    
    # Now register using the captured images
    return register_from_images(name, student_id, captured_images)


def list_registered():
    """List all registered students."""
    _, _, FaceMatcher = load_face_engine()
    
    matcher = FaceMatcher()
    if not matcher.load_index():
        print("📭 No students registered yet.")
        return
    
    print()
    print("=" * 60)
    print("  AttendX — Registered Students")
    print("=" * 60)
    print(f"  Total: {matcher.num_registered} students")
    print("-" * 60)
    print(f"  {'#':<4} {'Student ID':<15} {'Name':<30}")
    print("-" * 60)
    
    for i, (sid, name) in enumerate(zip(matcher.student_ids, 
                                         [matcher.student_names[sid] for sid in matcher.student_ids])):
        print(f"  {i+1:<4} {sid:<15} {name:<30}")
    
    print("=" * 60)


def remove_student(student_id: str):
    """Remove a student from the face database."""
    _, _, FaceMatcher = load_face_engine()
    
    matcher = FaceMatcher()
    matcher.load_index()
    
    if student_id not in matcher.student_ids:
        print(f"❌ Student {student_id} not found in database")
        return False
    
    name = matcher.student_names[student_id]
    
    print(f"⚠️  About to remove: {name} ({student_id})")
    response = input("   Confirm? (y/n): ").strip().lower()
    
    if response == 'y':
        matcher.remove_student(student_id)
        matcher.save_index()
        print(f"✅ {name} ({student_id}) removed from database")
        return True
    else:
        print("❌ Cancelled")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="AttendX — Student Face Registration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Register with 5 image files:
  python register_student.py --name "Ahmed Sherif" --id 221017673 --images face1.jpg face2.jpg face3.jpg face4.jpg face5.jpg

  # Register from a folder of images:
  python register_student.py --name "Ahmed Sherif" --id 221017673 --folder ./ahmed_photos/

  # Register using webcam:
  python register_student.py --name "Ahmed Sherif" --id 221017673 --webcam

  # List all registered students:
  python register_student.py --list

  # Remove a student:
  python register_student.py --remove 221017673
        """
    )
    
    parser.add_argument('--name', type=str, help='Student full name')
    parser.add_argument('--id', type=str, help='Student registration number')
    parser.add_argument('--images', nargs='+', help=f'Path to {MIN_IMAGES}+ face images')
    parser.add_argument('--folder', type=str, help='Folder containing face images')
    parser.add_argument('--webcam', action='store_true', help='Capture from webcam')
    parser.add_argument('--list', action='store_true', help='List registered students')
    parser.add_argument('--remove', type=str, help='Remove student by ID')
    
    args = parser.parse_args()
    
    # List registered students
    if args.list:
        list_registered()
        return
    
    # Remove student
    if args.remove:
        remove_student(args.remove)
        return
    
    # Registration requires name and ID
    if not args.name or not args.id:
        # Interactive mode
        if not args.name:
            args.name = input("👤 Enter student full name: ").strip()
        if not args.id:
            args.id = input("🆔 Enter student ID: ").strip()
        
        if not args.name or not args.id:
            print("❌ Name and ID are required")
            return
    
    # Choose registration method
    if args.images:
        register_from_images(args.name, args.id, args.images)
    elif args.folder:
        register_from_folder(args.name, args.id, args.folder)
    elif args.webcam:
        register_from_webcam(args.name, args.id)
    else:
        # Interactive: ask for method
        print()
        print("📸 How do you want to provide face photos?")
        print("  1. Image files")
        print("  2. Folder of images")
        print("  3. Webcam capture")
        print()
        
        choice = input("Choose (1/2/3): ").strip()
        
        if choice == '1':
            print(f"\nEnter paths to {MIN_IMAGES}+ image files (one per line, empty line to finish):")
            paths = []
            while True:
                path = input(f"  Image {len(paths)+1}: ").strip()
                if not path:
                    break
                paths.append(path)
            
            if paths:
                register_from_images(args.name, args.id, paths)
            else:
                print("❌ No images provided")
                
        elif choice == '2':
            folder = input("\n📂 Enter folder path: ").strip()
            if folder:
                register_from_folder(args.name, args.id, folder)
            else:
                print("❌ No folder provided")
                
        elif choice == '3':
            register_from_webcam(args.name, args.id)
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
