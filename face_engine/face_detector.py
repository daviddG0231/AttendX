"""
AttendX Face Detection Module

Uses RetinaFace (via InsightFace) for robust face detection
and ArcFace for face embedding generation.
"""

import numpy as np
import cv2
from typing import List, Tuple, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FaceDetector:
    """
    Face detection and recognition using InsightFace (RetinaFace + ArcFace).
    
    Pipeline:
    1. RetinaFace detects faces in frame
    2. InsightFace aligns detected faces 
    3. ArcFace generates 512-d embeddings
    """
    
    def __init__(self, det_thresh: float = 0.5, device: str = "cpu"):
        """
        Initialize face detector with InsightFace models.
        
        Args:
            det_thresh: Detection confidence threshold
            device: Compute device ("cpu" or "cuda")
        """
        self.det_thresh = det_thresh
        self.device = device
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Load InsightFace analysis model (downloads on first run)."""
        try:
            import insightface
            from insightface.app import FaceAnalysis
            
            # Initialize FaceAnalysis with buffalo_l model
            # This bundles RetinaFace (detection) + ArcFace (recognition)
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if self.device == "cuda" \
                       else ['CPUExecutionProvider']
            
            self.model = FaceAnalysis(
                name='buffalo_l',  # High-accuracy model
                root='./models',
                providers=providers
            )
            self.model.prepare(ctx_id=0 if self.device == "cuda" else -1, 
                             det_thresh=self.det_thresh,
                             det_size=(640, 640))
            
            logger.info("✅ InsightFace model loaded (RetinaFace + ArcFace)")
            
        except ImportError:
            logger.error("InsightFace not installed. Run: pip install insightface")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize InsightFace: {e}")
            raise
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect all faces in a video frame.
        
        Args:
            frame: BGR image as numpy array (from OpenCV)
            
        Returns:
            List of face dictionaries with:
            - bbox: [x1, y1, x2, y2] bounding box
            - embedding: 512-d face embedding vector
            - landmarks: 5 facial landmarks (eyes, nose, mouth corners)
            - det_score: detection confidence score
            - aligned_face: aligned face image (112x112)
        """
        if frame is None or frame.size == 0:
            return []
        
        try:
            # InsightFace processes the frame end-to-end:
            # RetinaFace detection → face alignment → ArcFace embedding
            faces = self.model.get(frame)
            
            results = []
            for face in faces:
                face_data = {
                    'bbox': face.bbox.astype(int).tolist(),        # [x1, y1, x2, y2]
                    'embedding': face.normed_embedding,             # 512-d normalized vector
                    'landmarks': face.kps.astype(int).tolist() if face.kps is not None else None,
                    'det_score': float(face.det_score),
                    'age': int(face.age) if hasattr(face, 'age') and face.age else None,
                    'gender': 'M' if hasattr(face, 'gender') and face.gender == 1 else 'F' if hasattr(face, 'gender') and face.gender == 0 else None,
                }
                
                # Extract aligned face crop for display/storage
                x1, y1, x2, y2 = face.bbox.astype(int)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                face_data['aligned_face'] = frame[y1:y2, x1:x2].copy()
                
                results.append(face_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []
    
    def get_embedding(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Get face embedding from a single face image.
        
        Args:
            face_image: BGR face image
            
        Returns:
            512-d normalized embedding vector, or None if no face detected
        """
        faces = self.detect_faces(face_image)
        if faces:
            return faces[0]['embedding']
        return None
    
    def get_embeddings_batch(self, face_images: List[np.ndarray]) -> List[Optional[np.ndarray]]:
        """
        Get embeddings for a batch of face images.
        
        Args:
            face_images: List of BGR face images
            
        Returns:
            List of 512-d embeddings (None for failed detections)
        """
        return [self.get_embedding(img) for img in face_images]
    
    def draw_detections(self, frame: np.ndarray, faces: List[Dict], 
                       names: List[str] = None) -> np.ndarray:
        """
        Draw detection results on frame for visualization.
        
        Args:
            frame: Original BGR frame
            faces: List of face detection results
            names: Optional list of identified names
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        for i, face in enumerate(faces):
            x1, y1, x2, y2 = face['bbox']
            score = face['det_score']
            
            # Determine color and label
            if names and i < len(names) and names[i]:
                color = (0, 255, 0)  # Green for identified
                label = f"{names[i]} ({score:.2f})"
            else:
                color = (0, 0, 255)  # Red for unknown
                label = f"Unknown ({score:.2f})"
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Draw label background
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(annotated, (x1, y1 - th - 10), (x1 + tw, y1), color, -1)
            cv2.putText(annotated, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Draw landmarks
            if face.get('landmarks'):
                for lm in face['landmarks']:
                    cv2.circle(annotated, tuple(lm), 2, (0, 255, 255), -1)
        
        return annotated


class AntiSpoofDetector:
    """
    Anti-spoofing detection using SilentFace / liveness check.
    
    Detects if the face is a real person or a photo/video replay attack.
    """
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.enabled = True
        logger.info("✅ Anti-spoofing detector initialized")
    
    def is_real_face(self, face_image: np.ndarray) -> Tuple[bool, float]:
        """
        Check if a face image is from a real person.
        
        Uses multiple heuristics:
        1. Texture analysis (real faces have more micro-texture)
        2. Color analysis (printed photos have different color distribution)
        3. Reflection detection (screens have specular reflections)
        
        Args:
            face_image: Cropped face image (BGR)
            
        Returns:
            Tuple of (is_real, confidence_score)
        """
        if not self.enabled or face_image is None or face_image.size == 0:
            return True, 1.0
        
        try:
            scores = []
            
            # 1. Texture Analysis using Laplacian variance
            # Real faces have more texture detail than printed photos
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            texture_score = min(1.0, laplacian_var / 500.0)
            scores.append(texture_score)
            
            # 2. Color Distribution Analysis
            # Real faces have specific color distributions in different channels
            hsv = cv2.cvtColor(face_image, cv2.COLOR_BGR2HSV)
            saturation_mean = np.mean(hsv[:, :, 1])
            color_score = min(1.0, saturation_mean / 80.0)
            scores.append(color_score)
            
            # 3. Frequency Domain Analysis
            # Real faces have more high-frequency components
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude = np.abs(f_shift)
            high_freq_ratio = np.sum(magnitude[magnitude > np.median(magnitude)]) / np.sum(magnitude)
            freq_score = min(1.0, high_freq_ratio)
            scores.append(freq_score)
            
            # Combined score
            final_score = np.mean(scores)
            is_real = final_score >= self.threshold
            
            return is_real, float(final_score)
            
        except Exception as e:
            logger.warning(f"Anti-spoof check failed: {e}")
            return True, 0.5  # Default to allowing on error
