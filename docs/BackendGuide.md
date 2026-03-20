folder structure 
StreamOS/
│
├─ media/                  # Video files
│    ├─ kids/
│    └─ mom/
│
├─ thumbnails/             # Generated thumbnails
│    ├─ kids/
│    └─ mom/
│
|-venv/
|
├─ app/
│    ├─ main.py            # FastAPI server
│    ├─ models.py          # SQLite models
│    ├─ crud.py            # DB operations
│    ├─ utils.py           # Thumbnail generator & helpers
│    └─ config.py          # Constants, paths
│
└─ requirements.txt

requirements.txt
pydantic
fastapi
uvicorn[standard]
python-multipart
SQLAlchemy
asyncpg
python-dotenv
ffmpeg-python

app/config.py
import os

MEDIA_DIR = os.path.join(os.getcwd(), "media")
THUMBNAIL_DIR = os.path.join(os.getcwd(), "thumbnails")
DATABASE_URL = "sqlite:///./streamos.db"

VIDEO_PROFILES = ["kids", "mom"]
app/models.py (Final Architecture)
```python
class UserProfile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    age_category = Column(String, nullable=False) # 'child', 'teen', 'adult'
    avatar_url = Column(String, nullable=True)

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=False)
    category = Column(String, nullable=False, default="adult") # 'kids', 'teen', 'adult'
```

app/crud.py (Sync Logic)
```python
def get_allowed_categories(age_category):
    if age_category == "child": return ["kids"]
    elif age_category == "teen": return ["kids", "teen"]
    else: return ["kids", "teen", "adult"]

def get_videos_for_profile(db: Session, profile_id: int):
    profile = get_profile(db, profile_id)
    allowed = get_allowed_categories(profile.age_category)
    return db.query(Video).filter(Video.category.in_(allowed)).all()
```

✅ Features Implemented
- **UserProfile CRUD**: Full profile management (/profile/create, /profiles).
- **Category Filtering**: Strict content access based on age category.
- **Secure Streaming**: `profile_id` required for stream and thumbnail access.
- **Auto-Scanner**: Category-aware media ingestion into `kids/`, `teen/`, `adult/`.
