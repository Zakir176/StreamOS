import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
THUMBNAIL_DIR = os.path.join(BASE_DIR, "thumbnails")
STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "static")
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'streamos.db')}"

VIDEO_PROFILES = ["kids", "mom"]

# Filenames or path fragments to always ignore in scans
IGNORED_MEDIA_PATTERNS = [
    "blue",
    "green",
    "red",
]

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
