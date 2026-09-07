from pathlib import Path

# ==========================================================
# PROJECT ROOT
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

# ==========================================================
# DATA
# ==========================================================

DATA_DIR = ROOT_DIR / "data"

VIDEO_DIR = DATA_DIR / "videos"

IMAGE_DIR = DATA_DIR / "images"

OUTPUT_DIR = DATA_DIR / "output"

# ==========================================================
# WEIGHTS
# ==========================================================

WEIGHTS_DIR = ROOT_DIR / "weights"

YOLO_MODEL = ROOT_DIR / "models" / "detectors" / "yolo11n.pt"

# Future models

INSIGHTFACE_MODEL = WEIGHTS_DIR / "insightface"

REALESRGAN_MODEL = WEIGHTS_DIR / "realesrgan"

CODEFORMER_MODEL = WEIGHTS_DIR / "codeformer"

# ==========================================================
# DATABASE
# ==========================================================

DATABASE_DIR = ROOT_DIR / "database"

DATABASE_PATH = DATABASE_DIR / "sentinel.db"

# ==========================================================
# DETECTION
# ==========================================================

CONFIDENCE_THRESHOLD = 0.35

IOU_THRESHOLD = 0.50

# ==========================================================
# QUALITY
# ==========================================================

BLUR_THRESHOLD = 100

# ==========================================================
# OCR

OCR_LANGUAGE = ["en"]

# ==========================================================
# VISUALIZATION

WINDOW_NAME = "SentinelAI"

DISPLAY_WIDTH = 960

DISPLAY_HEIGHT = 540