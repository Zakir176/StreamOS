from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse, Response, JSONResponse
import requests
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, crud, schemas, scanner, tmdb, config, utils
from .database import engine, SessionLocal
import os
from PIL import Image
import io
ENABLE_DOCS = os.getenv("ENABLE_DOCS", "true").lower() in ("true", "1")
app = FastAPI(
    title="StreamOS Backend",
    docs_url="/docs" if ENABLE_DOCS else None,
    redoc_url="/redoc" if ENABLE_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_DOCS else None
)

def get_resized_image(image_path, width: Optional[int] = None, height: Optional[int] = None):
    """Resize image on the fly and return a Response."""
    if not os.path.exists(image_path):
        return None
    
    if not width and not height:
        return FileResponse(image_path)
        
    try:
        # Clamp dimensions to prevent memory exhaustion / decompression bomb DoS
        if width is not None:
            width = max(16, min(int(width), 3840))
        if height is not None:
            height = max(16, min(int(height), 2160))

        img = Image.open(image_path)
        orig_w, orig_h = img.size
        
        if width and height:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        elif width:
            new_h = int((width / orig_w) * orig_h)
            img = img.resize((width, new_h), Image.Resampling.LANCZOS)
        elif height:
            new_w = int((height / orig_h) * orig_w)
            img = img.resize((new_w, height), Image.Resampling.LANCZOS)
            
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="WEBP", quality=80)
        img_byte_arr.seek(0)
        return Response(content=img_byte_arr.getvalue(), media_type="image/webp")
    except Exception as e:
        print(f"Error resizing image: {e}")
        return FileResponse(image_path)

import threading

@app.on_event("startup")
async def startup_event():
    # Run initial scan in a background thread so server starts immediately without event loop blockage
    print("Spawning initial library scan in background thread...")
    threading.Thread(target=scanner.scan_media, daemon=True).start()


# CORS setup
# In production, this should be restricted to the actual frontend domain.
# We'll allow localhost and the local network IP for development.
local_ip = utils.get_local_ip()
default_origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
    f"http://{local_ip}:5173"
]
env_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
allowed_origins = [o for o in (default_origins + env_origins) if o]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if "server" in response.headers:
        del response.headers["server"]
    return response


# Database setup
models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

FORBIDDEN_FOLDER_NAMES = {
    "windows", "winnt", "system volume information", "recovery", "perflogs",
    "program files", "program files (x86)", "programdata", "msys64",
    "appdata", ".ssh", ".aws", ".gemini", ".vscode", ".idea", ".git", "venv", "node_modules",
    "etc", "var", "root", "proc", "sys", "usr", "bin", "sbin", "boot"
}

def is_forbidden_path(path: str) -> bool:
    if not path:
        return False
    norm = os.path.normpath(path).lower()
    parts = [p.strip().strip("\\/") for p in norm.split(os.sep) if p.strip()]
    for part in parts:
        if part in FORBIDDEN_FOLDER_NAMES or part.startswith(".") or part.startswith("$"):
            return True
    return False

def validate_path(base_dir, path):
    """Ensure the path is safe and within the base directory."""
    if not utils.is_safe_path(base_dir, path):
        raise HTTPException(status_code=400, detail="Invalid path or path traversal attempt detected")
    return path

# Endpoints
@app.get("/profiles", response_model=list[schemas.Profile])
def profiles(db: Session = Depends(get_db)):
    return crud.get_profiles(db)

@app.get("/filesystem/browse")
def browse_filesystem(path: Optional[str] = None, db: Session = Depends(get_db)):
    import string
    
    current_media_setting = crud.get_setting(db, "media_dir")
    active_media_dir = current_media_setting.value if current_media_setting else config.MEDIA_DIR
    
    quick_paths = []
    if active_media_dir and os.path.exists(active_media_dir):
        quick_paths.append({"name": "Current Library", "path": active_media_dir})
    if os.path.exists(config.MEDIA_DIR) and (not active_media_dir or os.path.abspath(config.MEDIA_DIR) != os.path.abspath(active_media_dir)):
        quick_paths.append({"name": "Default Media", "path": config.MEDIA_DIR})
        
    home_dir = os.path.expanduser("~")
    for common_folder in ["Videos", "Movies"]:
        p = os.path.join(home_dir, common_folder)
        if os.path.exists(p):
            quick_paths.append({"name": f"User {common_folder}", "path": p})

    # Allow drive roots only if explicitly configured via STREAMOS_ALLOW_SYSTEM_BROWSE
    allow_system_browse = os.getenv("STREAMOS_ALLOW_SYSTEM_BROWSE", "false").lower() in ("true", "1")
    drives = []
    if allow_system_browse:
        if os.name == "nt":
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    drives.append(drive_path)
        else:
            drives = ["/"]
        for d in drives:
            quick_paths.append({"name": f"Drive ({d})", "path": d})
        
    target_path = path.strip() if path else None
    if not target_path:
        target_path = active_media_dir if (active_media_dir and os.path.exists(active_media_dir)) else (quick_paths[0]["path"] if quick_paths else os.getcwd())

    norm_path = os.path.abspath(target_path)
    
    # Security check: Block navigation into forbidden system directories
    if is_forbidden_path(norm_path):
        return {
            "success": False,
            "error": "Access to this system directory is restricted for security.",
            "current_path": active_media_dir or norm_path,
            "parent_path": None,
            "drives": drives,
            "quick_paths": quick_paths,
            "directories": [],
            "stats": {"video_count": 0, "has_media_subfolders": False}
        }

    if not os.path.exists(norm_path) or not os.path.isdir(norm_path):
        return {
            "success": False,
            "error": f"Path does not exist or is not a directory: {target_path}",
            "current_path": target_path,
            "parent_path": None,
            "drives": drives,
            "quick_paths": quick_paths,
            "directories": [],
            "stats": {"video_count": 0, "has_media_subfolders": False}
        }
        
    parent_path = os.path.dirname(norm_path)
    if parent_path == norm_path or not parent_path or is_forbidden_path(parent_path):
        parent_path = None
        
    directories = []
    video_extensions = (".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm")
    video_count = 0
    has_media_subfolders = False
    
    try:
        with os.scandir(norm_path) as it:
            for entry in it:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        name = entry.name
                        if is_forbidden_path(name) or is_forbidden_path(entry.path):
                            continue
                        lower = name.lower()
                        if lower in ["movies", "tv shows", "anime", "kids", "teen", "adult"]:
                            has_media_subfolders = True
                        directories.append({
                            "name": name,
                            "path": entry.path
                        })
                    elif entry.is_file(follow_symlinks=False):
                        if entry.name.lower().endswith(video_extensions):
                            video_count += 1
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError) as e:
        return {
            "success": False,
            "error": f"Permission denied accessing folder: {str(e)}",
            "current_path": norm_path,
            "parent_path": parent_path,
            "drives": drives,
            "quick_paths": quick_paths,
            "directories": [],
            "stats": {"video_count": 0, "has_media_subfolders": False}
        }
        
    directories.sort(key=lambda d: d["name"].lower())
    
    return {
        "success": True,
        "current_path": norm_path,
        "parent_path": parent_path,
        "drives": drives,
        "quick_paths": quick_paths,
        "directories": directories,
        "stats": {
            "video_count": video_count,
            "has_media_subfolders": has_media_subfolders
        }
    }

@app.post("/scan")
def trigger_scan(req: Optional[schemas.ScanRequest] = None, db: Session = Depends(get_db)):
    if scanner.is_scan_running():
        return {"success": False, "message": "A library scan is already in progress. Please wait."}

    custom_dir = None
    if req and req.media_dir:
        custom_dir = req.media_dir.strip()
        if not os.path.exists(custom_dir) or not os.path.isdir(custom_dir):
            raise HTTPException(status_code=400, detail=f"Media directory does not exist or is not a directory: {custom_dir}")
        if is_forbidden_path(custom_dir):
            raise HTTPException(status_code=403, detail="Specified media directory is a restricted system path")
        crud.set_setting(db, "media_dir", custom_dir)
    result = scanner.scan_media(custom_dir=custom_dir)
    if result is None:
        return {"success": True, "message": "Scan completed"}
    return result

@app.get("/settings", response_model=list[schemas.SystemSetting])
def get_settings(db: Session = Depends(get_db)):
    settings = crud.get_settings(db)
    has_media_dir = False
    for s in settings:
        if s.key == "media_dir":
            has_media_dir = True
        if s.key == "tmdb_api_key" and s.value:
            s.value = "********" + s.value[-4:] if len(s.value) > 4 else "********"
    if not has_media_dir:
        settings.append(schemas.SystemSetting(key="media_dir", value=config.MEDIA_DIR))
    return settings

@app.get("/settings/{key}", response_model=schemas.SystemSetting)
def get_setting(key: str, db: Session = Depends(get_db)):
    setting = crud.get_setting(db, key)
    if not setting:
        if key == "media_dir":
            return schemas.SystemSetting(key="media_dir", value=config.MEDIA_DIR)
        raise HTTPException(status_code=404, detail="Setting not found")
    
    # Mask sensitive keys
    if key == "tmdb_api_key" and setting.value:
        return schemas.SystemSetting(
            key=setting.key, 
            value="********" + setting.value[-4:] if len(setting.value) > 4 else "********"
        )
    return setting

@app.post("/settings", response_model=schemas.SystemSetting)
def set_setting(setting: schemas.SystemSettingBase, db: Session = Depends(get_db)):
    # If it's the TMDB key and it's masked, don't update it
    if setting.key == "tmdb_api_key" and setting.value.startswith("********"):
        existing = crud.get_setting(db, setting.key)
        if existing:
            return existing
            
    # If setting media_dir, validate that it exists on disk and is not a restricted path
    if setting.key == "media_dir":
        val = setting.value.strip()
        if val:
            if not os.path.exists(val) or not os.path.isdir(val):
                raise HTTPException(status_code=400, detail=f"Directory does not exist on server: {val}")
            if is_forbidden_path(val):
                raise HTTPException(status_code=403, detail="Specified directory is a restricted system path")
    
    return crud.set_setting(db, setting.key, setting.value)


@app.get("/profile/{profile_id}", response_model=schemas.Profile)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.post("/profile/create", response_model=schemas.Profile)
def create_profile(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    return crud.create_profile(db, profile.username, profile.age_category, profile.avatar_url, profile.theme)

@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    success = crud.delete_profile(db, profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted"}

@app.patch("/profiles/{profile_id}", response_model=schemas.Profile)
def update_profile(profile_id: int, profile: schemas.ProfileUpdate, db: Session = Depends(get_db)):
    updated_profile = crud.update_profile(db, profile_id, profile)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return updated_profile

@app.post("/scrape")
def scrape_metadata(db: Session = Depends(get_db)):
    offline_mode = crud.get_setting(db, "offline_mode")
    if offline_mode and offline_mode.value == "true":
        raise HTTPException(status_code=400, detail="Cannot scrape metadata while in Offline Mode.")
        
    # Simple scraper logic: iterate over all videos and series without descriptions and try to fetch from TMDB
    api_key = crud.get_setting(db, "tmdb_api_key")
    if not api_key:
        raise HTTPException(status_code=400, detail="TMDB API key not set in settings")

    updated_series = 0
    updated_videos = 0

    # Scrape Series
    all_series = db.query(models.Series).all()
    for series in all_series:
        if not series.description or "poster.tmdb.org" not in (series.poster_path or ""):
            # Try to get the year from the first video in the series
            first_video = db.query(models.Video).filter(models.Video.series_id == series.id).first()
            year = first_video.release_year if first_video else None
            
            search_result = tmdb.search_tmdb(db, series.title, "tv" if series.folder_category == "TV Shows" else "movie", year=year)
            if search_result:
                series.description = search_result.get("overview", series.description)
                if search_result.get("poster_path"):
                    tmdb_poster_path = search_result.get("poster_path")
                    tmdb_url = f"https://image.tmdb.org/t/p/w500{tmdb_poster_path}"
                    local_filename = f"series_{series.id}.jpg"
                    local_path = os.path.join(config.THUMBNAIL_DIR, series.category, local_filename)
                    saved_path = utils.download_image(tmdb_url, local_path)
                    if saved_path:
                        series.poster_path = os.path.relpath(saved_path, config.THUMBNAIL_DIR)
                
                # Download backdrop locally
                tmdb_backdrop_path = search_result.get("backdrop_path")
                if tmdb_backdrop_path:
                    tmdb_url = f"https://image.tmdb.org/t/p/w1280{tmdb_backdrop_path}"
                    local_filename = f"series_backdrop_{series.id}.jpg"
                    local_path = os.path.join(config.THUMBNAIL_DIR, series.category, local_filename)
                    saved_path = utils.download_image(tmdb_url, local_path)
                    if saved_path:
                        series.backdrop_path = os.path.relpath(saved_path, config.THUMBNAIL_DIR)

                # Fetch extra metadata (Cast, Director, Trailer)
                tmdb_id = search_result.get("id")
                m_type = "tv" if series.folder_category == "TV Shows" else "movie"
                series.cast, series.director = tmdb.get_tmdb_credits(db, tmdb_id, m_type)
                series.trailer_url = tmdb.get_tmdb_trailer(db, tmdb_id, m_type)
                
                updated_series += 1

    # Scrape Videos (mainly movies not in series)
    standalone_movies = db.query(models.Video).filter(models.Video.series_id == None, models.Video.folder_category == "Movies").all()
    for movie in standalone_movies:
        # For simplicity, if title is generic or missing description, scrape
        search_result = tmdb.search_tmdb(db, movie.title, "movie", year=movie.release_year)
        if search_result:
            # Update year if we found a better match
            movie.release_year = int(search_result.get("release_date", "0000")[:4]) or movie.release_year
            # Save synopsis
            movie.description = search_result.get("overview", movie.description)
            # Download poster locally
            tmdb_poster_path = search_result.get("poster_path")
            if tmdb_poster_path:
                tmdb_url = f"https://image.tmdb.org/t/p/w500{tmdb_poster_path}"
                local_filename = f"video_{movie.id}.jpg"
                local_path = os.path.join(config.THUMBNAIL_DIR, movie.category, local_filename)
                saved_path = utils.download_image(tmdb_url, local_path)
                if saved_path:
                    movie.thumbnail_path = os.path.relpath(saved_path, config.THUMBNAIL_DIR)
            
            # Download backdrop locally
            tmdb_backdrop_path = search_result.get("backdrop_path")
            if tmdb_backdrop_path:
                tmdb_url = f"https://image.tmdb.org/t/p/w1280{tmdb_backdrop_path}"
                local_filename = f"video_backdrop_{movie.id}.jpg"
                local_path = os.path.join(config.THUMBNAIL_DIR, movie.category, local_filename)
                saved_path = utils.download_image(tmdb_url, local_path)
                if saved_path:
                    movie.backdrop_path = os.path.relpath(saved_path, config.THUMBNAIL_DIR)

            # Fetch extra metadata (Cast, Director, Trailer)
            tmdb_id = search_result.get("id")
            movie.cast, movie.director = tmdb.get_tmdb_credits(db, tmdb_id, "movie")
            movie.trailer_url = tmdb.get_tmdb_trailer(db, tmdb_id, "movie")
            
            updated_videos += 1

    db.commit()
    return {"message": f"Scrape completed. Updated {updated_series} series and {updated_videos} videos."}

@app.get("/library")
def library(profile_id: int, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    if not profile:
         raise HTTPException(status_code=404, detail="Profile not found")
    
    videos = crud.get_videos_for_profile(db, profile_id)

    def is_ignored(video):
        title = (video.title or "").lower()
        return any(p in title for p in config.IGNORED_MEDIA_PATTERNS)
    series = crud.get_series_for_profile(db, profile_id)
    
    # Standalone Movies (not part of a series)
    movies = [v for v in videos if v.folder_category == "Movies" and v.series_id is None and not is_ignored(v)]
    
    # TV Shows (Series)
    shows_list = [s for s in series if s.folder_category == "TV Shows"]
    
    # Anime (Series)
    anime_list = [s for s in series if s.folder_category == "Anime"]
    
    def format_series(s_list):
        results = []
        for s in s_list:
            # For thumbnail, use poster if available, otherwise first episode's thumb
            first_ep = db.query(models.Video).filter(models.Video.series_id == s.id).first()
            thumb_url = f"/thumbnail/series/{s.id}?profile_id={profile_id}" if s.poster_path else (f"/thumbnail/{first_ep.id}?profile_id={profile_id}" if first_ep else "")
            
            results.append({
                "id": s.id,
                "title": s.title,
                "thumbnail_url": thumb_url,
                "backdrop_url": f"/thumbnail/backdrop/series/{s.id}?profile_id={profile_id}" if s.backdrop_path else None,
                "type": "show",
                "episodes_count": db.query(models.Video).filter(models.Video.series_id == s.id).count(),
                "dominant_color": s.dominant_color or (first_ep.dominant_color if first_ep else None),
                "thumbnail_placeholder": s.thumbnail_placeholder or (first_ep.thumbnail_placeholder if first_ep else None)
            })
        return results

    return {
        "movies": [
            {
                "id": v.id, 
                "title": v.title, 
                "thumbnail_url": f"/thumbnail/{v.id}?profile_id={profile_id}",
                "backdrop_url": f"/thumbnail/backdrop/{v.id}?profile_id={profile_id}" if v.backdrop_path else None,
                "type": v.type,
                "release_year": v.release_year,
                "dominant_color": v.dominant_color,
                "thumbnail_placeholder": v.thumbnail_placeholder
            } 
            for v in movies
        ],
        "tv_shows": format_series(shows_list),
        "anime": format_series(anime_list),
        "continue_watching": [
            {
                "id": item["video"].id, 
                "title": item["video"].title, 
                "thumbnail_url": f"/thumbnail/{item['video'].id}?profile_id={profile_id}",
                "show_name": item["video"].show_name,
                "season": item["video"].season,
                "episode": item["video"].episode,
                "type": item["video"].type,
                "folder_category": item["video"].folder_category,
                "backdrop_url": f"/thumbnail/backdrop/{item['video'].id}?profile_id={profile_id}" if item["video"].backdrop_path else None,
                "current_time": item["current_time"],
                "duration": item["duration"],
                "dominant_color": item["video"].dominant_color,
                "thumbnail_placeholder": item["video"].thumbnail_placeholder
            }
            for item in crud.get_continue_watching(db, profile_id)
        ],
        "all": [
             {
                "id": v.id, 
                "title": v.title, 
                "thumbnail_url": f"/thumbnail/{v.id}?profile_id={profile_id}",
                "backdrop_url": f"/thumbnail/backdrop/{v.id}?profile_id={profile_id}" if v.backdrop_path else None,
                "show_name": v.show_name,
                "season": v.season,
                "episode": v.episode,
                "type": v.type,
                "folder_category": v.folder_category,
                "duration": v.duration,
                "current_time": crud.get_watch_progress(db, profile_id, v.id),
                "dominant_color": v.dominant_color,
                "thumbnail_placeholder": v.thumbnail_placeholder
            } 
            for v in videos
            if not is_ignored(v)
        ]
    }

@app.post("/progress")
def update_progress(progress: schemas.WatchProgressUpdate, db: Session = Depends(get_db)):
    crud.update_watch_progress(db, progress.profile_id, progress.video_id, progress.current_time, progress.duration)
    return {"success": True}

@app.get("/progress/{video_id}", response_model=schemas.WatchProgressResponse)
def get_progress(video_id: int, profile_id: int, db: Session = Depends(get_db)):
    current_time = crud.get_watch_progress(db, profile_id, video_id)
    return {"current_time": current_time}

@app.get("/next-episode/{video_id}")
def get_next_episode(video_id: int, db: Session = Depends(get_db)):
    next_ep = crud.get_next_episode(db, video_id)
    if not next_ep:
        return None
    return {
        "id": next_ep.id,
        "title": next_ep.title,
        "thumbnail_url": f"/thumbnail/{next_ep.id}"
    }

@app.get("/series/{series_id}")
def get_series_detail(series_id: int, profile_id: int, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    series = crud.get_series(db, series_id)
    if not series or not profile:
        raise HTTPException(status_code=404, detail="Not found")
    
    allowed = crud.get_allowed_categories(profile.age_category)
    if series.category not in allowed:
        raise HTTPException(status_code=403, detail="Access denied")
        
    episodes = crud.get_episodes_for_series(db, series_id)
    return {
        "id": series.id,
        "title": series.title,
        "description": series.description,
        "cast": series.cast,
        "director": series.director,
        "trailer_url": series.trailer_url,
        "dominant_color": series.dominant_color,
        "thumbnail_placeholder": series.thumbnail_placeholder,
        "thumbnail_url": f"/thumbnail/series/{series.id}?profile_id={profile_id}" if series.poster_path else None,
        "backdrop_url": f"/thumbnail/backdrop/series/{series.id}?profile_id={profile_id}" if series.backdrop_path else None,
        "episodes": [
            {
                "id": e.id,
                "title": e.title,
                "season": e.season,
                "episode": e.episode,
                "thumbnail_url": f"/thumbnail/{e.id}?profile_id={profile_id}"
            }
            for e in episodes
        ]
    }

@app.get("/thumbnail/series/{series_id}")
def get_series_thumbnail(series_id: int, profile_id: int, w: Optional[int] = None, h: Optional[int] = None, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    series = crud.get_series(db, series_id)
    
    if not series or not profile:
        raise HTTPException(status_code=404, detail="Not found")
        
    allowed = crud.get_allowed_categories(profile.age_category)
    if series.category not in allowed:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not series.poster_path:
         raise HTTPException(status_code=404, detail="Poster not found")
    
    if series.poster_path.startswith("http"):
        return RedirectResponse(series.poster_path)
    
    # Resolve relative path
    # 1. Try THUMBNAIL_DIR
    path1 = os.path.join(config.THUMBNAIL_DIR, series.poster_path)
    if os.path.exists(path1):
        validate_path(config.THUMBNAIL_DIR, path1)
        res = get_resized_image(path1, w, h)
        if res: return res
        
    # 2. Try MEDIA_DIR (local posters)
    media_dir_setting = crud.get_setting(db, "media_dir")
    media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
    path2 = os.path.join(media_base, series.poster_path)
    if os.path.exists(path2):
        validate_path(media_base, path2)
        res = get_resized_image(path2, w, h)
        if res: return res
        
    raise HTTPException(status_code=404, detail="Poster not found on disk")

@app.get("/stream/{video_id}")
def stream_video(video_id: int, profile_id: int, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    video = crud.get_video(db, video_id)
    
    if not video or not profile:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    allowed = crud.get_allowed_categories(profile.age_category)
    if video.category not in allowed:
        raise HTTPException(status_code=403, detail="Access denied for this profile category")

    full_path = video.filepath
    media_dir_setting = crud.get_setting(db, "media_dir")
    media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
    
    if not os.path.isabs(full_path):
        full_path = os.path.join(media_base, video.filepath)

    validate_path(media_base, full_path)

    if not os.path.exists(full_path):
         raise HTTPException(status_code=404, detail="Video file not found on disk")
    return FileResponse(full_path, media_type="video/mp4", filename=video.title)

@app.get("/thumbnail/{video_id}")
def get_thumbnail(video_id: int, profile_id: int, w: Optional[int] = None, h: Optional[int] = None, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    video = crud.get_video(db, video_id)
    
    if not video or not profile:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    allowed = crud.get_allowed_categories(profile.age_category)
    if video.category not in allowed:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not video.thumbnail_path:
         raise HTTPException(status_code=404, detail="Thumbnail not found")

    if video.thumbnail_path.startswith("http"):
        return RedirectResponse(video.thumbnail_path)

    # Resolve relative path
    # 1. Try THUMBNAIL_DIR (generated thumbs)
    thumb_path = os.path.join(config.THUMBNAIL_DIR, video.thumbnail_path)
    if os.path.exists(thumb_path):
        validate_path(config.THUMBNAIL_DIR, thumb_path)
        res = get_resized_image(thumb_path, w, h)
        if res: return res
        
    # 2. Try MEDIA_DIR (local posters)
    media_dir_setting = crud.get_setting(db, "media_dir")
    media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
    media_path = os.path.join(media_base, video.thumbnail_path)
    if os.path.exists(media_path):
        validate_path(media_base, media_path)
        res = get_resized_image(media_path, w, h)
        if res: return res
    
    return FileResponse(os.path.join(config.STATIC_DIR, "default_poster.jpg"))

@app.get("/thumbnail/backdrop/{video_id}")
def get_video_backdrop(video_id: int, profile_id: int, w: Optional[int] = None, h: Optional[int] = None, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    video = crud.get_video(db, video_id)
    
    if not video or not profile:
        raise HTTPException(status_code=404, detail="Not found")
        
    if video.category not in crud.get_allowed_categories(profile.age_category):
          raise HTTPException(status_code=403, detail="Access denied")

    if video.backdrop_path:
        if video.backdrop_path.startswith("http"):
            return RedirectResponse(video.backdrop_path)
            
        # 1. Try THUMBNAIL_DIR
        path1 = os.path.join(config.THUMBNAIL_DIR, video.backdrop_path)
        if os.path.exists(path1):
            validate_path(config.THUMBNAIL_DIR, path1)
            res = get_resized_image(path1, w, h)
            if res: return res
            
        # 2. Try MEDIA_DIR
        media_dir_setting = crud.get_setting(db, "media_dir")
        media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
        path2 = os.path.join(media_base, video.backdrop_path)
        if os.path.exists(path2):
            validate_path(media_base, path2)
            res = get_resized_image(path2, w, h)
            if res: return res
            
    # Fallback to poster
    return get_thumbnail(video_id, profile_id, w, h, db)

@app.get("/thumbnail/backdrop/series/{series_id}")
def get_series_backdrop(series_id: int, profile_id: int, w: Optional[int] = None, h: Optional[int] = None, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    series = crud.get_series(db, series_id)
    
    if not series or not profile:
        raise HTTPException(status_code=404, detail="Not found")
        
    if series.category not in crud.get_allowed_categories(profile.age_category):
          raise HTTPException(status_code=403, detail="Access denied")

    if series.backdrop_path:
        if series.backdrop_path.startswith("http"):
            return RedirectResponse(series.backdrop_path)
            
        # 1. Try THUMBNAIL_DIR
        path1 = os.path.join(config.THUMBNAIL_DIR, series.backdrop_path)
        if os.path.exists(path1):
            validate_path(config.THUMBNAIL_DIR, path1)
            res = get_resized_image(path1, w, h)
            if res: return res
            
        # 2. Try MEDIA_DIR
        media_dir_setting = crud.get_setting(db, "media_dir")
        media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
        path2 = os.path.join(media_base, series.backdrop_path)
        if os.path.exists(path2):
            validate_path(media_base, path2)
            res = get_resized_image(path2, w, h)
            if res: return res
            
    raise HTTPException(status_code=404, detail="Backdrop not found")

@app.get("/video/{video_id}/scrub")
def get_video_scrub_sheet(video_id: int, db: Session = Depends(get_db)):
    """Return the sprite sheet for scrubbing."""
    video = crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    sheet_path = os.path.join(config.THUMBNAIL_DIR, "scrub", f"{video_id}_sprite.webp")
    if not os.path.exists(sheet_path):
        # Return a simple JSON indicating it's not ready
        return JSONResponse(status_code=404, content={"message": "Sprite sheet not generated yet"})
        
    return FileResponse(sheet_path, media_type="image/webp")

@app.get("/video/{video_id}/scrub-info")
def get_video_scrub_info(video_id: int, db: Session = Depends(get_db)):
    """Return metadata for the sprite sheet."""
    # For now, we use a fixed config, but we could store this in the DB
    return {
        "interval": 10,
        "cols": 10,
        "fw": 160,
        "fh": 90 # approximate
    }

running_scrub_tasks = set()

@app.post("/video/{video_id}/generate-scrub")
def generate_video_scrub(video_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    video = crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    scrub_path = os.path.join(config.THUMBNAIL_DIR, "scrub", f"{video_id}_sprite.webp")
    if os.path.exists(scrub_path):
        return {"message": "Sprite sheet already generated"}
        
    if video_id in running_scrub_tasks:
        return {"message": "Sprite sheet generation already in progress"}
    
    media_dir_setting = crud.get_setting(db, "media_dir")
    media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
    video_abs_path = os.path.join(media_base, video.filepath)
    
    validate_path(media_base, video_abs_path)
    if not os.path.exists(video_abs_path):
        raise HTTPException(status_code=404, detail="Video file not found on disk")
        
    running_scrub_tasks.add(video_id)
    os.makedirs(os.path.dirname(scrub_path), exist_ok=True)
    
    def _execute_scrub(vid, vpath, spath):
        try:
            utils.generate_sprite_sheet(vpath, spath)
        finally:
            running_scrub_tasks.discard(vid)
            
    background_tasks.add_task(_execute_scrub, video_id, video_abs_path, scrub_path)
    return {"message": "Sprite sheet generation started in background"}

