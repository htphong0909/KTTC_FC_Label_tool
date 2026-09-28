import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_VIDEO_DIR = BASE_DIR / "VIDEO_TRAIN"
ANNOTATION_DIR = BASE_DIR / "outputs" / "annotations"
CUT_CLIPS_DIR = BASE_DIR / "outputs" / "cut_clips"
DEFAULT_PORT = 5055
ALLOWED_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

ANNOTATION_DIR.mkdir(parents=True, exist_ok=True)
CUT_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
