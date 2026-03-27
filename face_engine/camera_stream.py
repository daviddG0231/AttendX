"""
AttendX Camera Stream Module

Handles RTSP camera connections and frame extraction using OpenCV.
"""

import cv2
import time
import threading
import numpy as np
from typing import Optional, Callable
from queue import Queue
import logging

logger = logging.getLogger(__name__)


class CameraStream:
    """
    RTSP camera stream handler with automatic reconnection.
    
    Connects to IP cameras via RTSP protocol and provides
    frame-by-frame access for the face engine.
    """
    
    def __init__(self, rtsp_url: str, camera_id: str = "cam_0",
                 frame_skip: int = 2, reconnect_delay: int = 5):
        """
        Initialize camera stream.
        
        Args:
            rtsp_url: RTSP URL (e.g., rtsp://admin:pass@192.168.1.100:554/stream)
            camera_id: Unique identifier for this camera
            frame_skip: Process every Nth frame (performance optimization)
            reconnect_delay: Seconds to wait before reconnection attempt
        """
        self.rtsp_url = rtsp_url
        self.camera_id = camera_id
        self.frame_skip = frame_skip
        self.reconnect_delay = reconnect_delay
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.is_connected = False
        self.frame_count = 0
        self.fps = 0.0
        
        # Thread-safe frame buffer
        self._frame_queue = Queue(maxsize=5)
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def connect(self) -> bool:
        """
        Establish connection to RTSP camera.
        
        Returns:
            True if connection successful
        """
        try:
            logger.info(f"📷 Connecting to camera {self.camera_id}: {self.rtsp_url}")
            
            # OpenCV RTSP connection with optimized settings
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            # Set buffer size to minimize latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if self.cap.isOpened():
                # Read a test frame
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    h, w = frame.shape[:2]
                    self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
                    self.is_connected = True
                    logger.info(f"✅ Camera {self.camera_id} connected: "
                              f"{w}x{h} @ {self.fps:.1f} FPS")
                    return True
            
            logger.error(f"❌ Failed to connect to camera {self.camera_id}")
            self.is_connected = False
            return False
            
        except Exception as e:
            logger.error(f"❌ Camera connection error: {e}")
            self.is_connected = False
            return False
    
    def start(self):
        """Start background frame capture thread."""
        if self._thread and self._thread.is_alive():
            logger.warning(f"Camera {self.camera_id} already running")
            return
        
        if not self.is_connected:
            if not self.connect():
                return
        
        self.is_running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info(f"🎬 Camera {self.camera_id} capture started")
    
    def stop(self):
        """Stop frame capture and release camera."""
        self.is_running = False
        
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.is_connected = False
        logger.info(f"⏹️  Camera {self.camera_id} stopped")
    
    def _capture_loop(self):
        """Background thread for continuous frame capture."""
        frame_count = 0
        last_time = time.time()
        
        while self.is_running:
            if not self.is_connected or self.cap is None:
                self._reconnect()
                continue
            
            try:
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    logger.warning(f"⚠️  Frame read failed for {self.camera_id}")
                    self.is_connected = False
                    continue
                
                frame_count += 1
                
                # Frame skip for performance
                if frame_count % self.frame_skip != 0:
                    continue
                
                # Update FPS calculation
                current_time = time.time()
                if current_time - last_time >= 1.0:
                    self.fps = frame_count / (current_time - last_time)
                    frame_count = 0
                    last_time = current_time
                
                # Put frame in queue (drop old frames if full)
                if self._frame_queue.full():
                    try:
                        self._frame_queue.get_nowait()
                    except:
                        pass
                
                self._frame_queue.put(frame)
                self.frame_count += 1
                
            except Exception as e:
                logger.error(f"Capture error: {e}")
                self.is_connected = False
    
    def _reconnect(self):
        """Attempt to reconnect to camera."""
        logger.info(f"🔄 Reconnecting to camera {self.camera_id} "
                   f"in {self.reconnect_delay}s...")
        time.sleep(self.reconnect_delay)
        self.connect()
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get the latest frame from the camera.
        
        Returns:
            BGR frame as numpy array, or None if no frame available
        """
        try:
            if not self._frame_queue.empty():
                return self._frame_queue.get_nowait()
            return None
        except:
            return None
    
    def get_frame_blocking(self, timeout: float = 5.0) -> Optional[np.ndarray]:
        """
        Get frame with blocking wait.
        
        Args:
            timeout: Maximum seconds to wait
            
        Returns:
            BGR frame or None on timeout
        """
        try:
            return self._frame_queue.get(timeout=timeout)
        except:
            return None
    
    @property
    def status(self) -> dict:
        """Get camera status information."""
        return {
            'camera_id': self.camera_id,
            'rtsp_url': self.rtsp_url,
            'is_connected': self.is_connected,
            'is_running': self.is_running,
            'fps': round(self.fps, 1),
            'total_frames': self.frame_count
        }


class MultiCameraManager:
    """
    Manage multiple RTSP camera streams simultaneously.
    """
    
    def __init__(self):
        self.cameras: dict[str, CameraStream] = {}
    
    def add_camera(self, camera_id: str, rtsp_url: str, **kwargs) -> bool:
        """Add and start a new camera stream."""
        if camera_id in self.cameras:
            logger.warning(f"Camera {camera_id} already exists")
            return False
        
        camera = CameraStream(rtsp_url, camera_id, **kwargs)
        self.cameras[camera_id] = camera
        camera.start()
        return True
    
    def remove_camera(self, camera_id: str):
        """Stop and remove a camera stream."""
        if camera_id in self.cameras:
            self.cameras[camera_id].stop()
            del self.cameras[camera_id]
    
    def get_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """Get latest frame from a specific camera."""
        if camera_id in self.cameras:
            return self.cameras[camera_id].get_frame()
        return None
    
    def get_all_frames(self) -> dict[str, Optional[np.ndarray]]:
        """Get latest frames from all cameras."""
        return {cid: cam.get_frame() for cid, cam in self.cameras.items()}
    
    def get_status(self) -> dict:
        """Get status of all cameras."""
        return {cid: cam.status for cid, cam in self.cameras.items()}
    
    def stop_all(self):
        """Stop all camera streams."""
        for camera in self.cameras.values():
            camera.stop()
        logger.info("⏹️  All cameras stopped")
