"""
AttendX Face Engine Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-key")

# Face Detection Settings
FACE_DETECTION_THRESHOLD = 0.5        # Minimum confidence for face detection
FACE_RECOGNITION_THRESHOLD = 0.4      # Distance threshold for face matching (lower = stricter)
FACE_SIZE = (112, 112)                # Standard face size for ArcFace

# Anti-Spoofing Settings
ANTI_SPOOF_ENABLED = True
ANTI_SPOOF_THRESHOLD = 0.5

# RTSP Camera Settings
RTSP_RECONNECT_DELAY = 5             # Seconds before reconnection attempt
RTSP_FRAME_SKIP = 2                  # Process every Nth frame for performance
RTSP_TIMEOUT = 10                    # Connection timeout in seconds

# Attendance Settings
PRESENCE_CHECK_INTERVAL = 300        # Seconds between periodic checks (5 min)
PRESENCE_THRESHOLD = 0.70            # 70% presence required for attendance
ENTRY_WINDOW_MINUTES = 15            # Minutes after lecture start to count as "on time"

# FAISS Settings
FAISS_INDEX_PATH = "data/faiss_index.bin"
EMBEDDINGS_PATH = "data/embeddings.npy"
STUDENT_IDS_PATH = "data/student_ids.json"

# Tracking Settings (DeepSORT)
MAX_AGE = 30                         # Max frames to keep track without detection
N_INIT = 3                           # Min detections before confirmed track
MAX_COSINE_DISTANCE = 0.3

# Performance
BATCH_SIZE = 8                       # Faces to process per batch
NUM_WORKERS = 4
DEVICE = "cpu"                       # "cpu" or "cuda"
