from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse, Response
import requests
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, crud, schemas, scanner, tmdb, config, utils
from .database import engine, SessionLocal
import os

app = FastAPI(title="StreamOS Backend")

@app.on_event("startup")
async def startup_event():
    # Run scan on startup
    print("Running initial library scan...")
    scanner.scan_media()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.get("/profiles", response_model=list[schemas.Profile])
def profiles(db: Session = Depends(get_db)):
    return crud.get_profiles(db)

@app.post("/scan")
def trigger_scan():
    result = scanner.scan_media()
    # For backward compatibility if scan_media returns None
    if result is None:
        return {"success": True, "message": "Scan completed"}
    return result

@app.get("/settings", response_model=list[schemas.SystemSetting])
def get_settings(db: Session = Depends(get_db)):
    return crud.get_settings(db)

@app.get("/settings/{key}", response_model=schemas.SystemSetting)
def get_setting(key: str, db: Session = Depends(get_db)):
    setting = crud.get_setting(db, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@app.post("/settings", response_model=schemas.SystemSetting)
def set_setting(setting: schemas.SystemSettingBase, db: Session = Depends(get_db)):
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
                "episodes_count": db.query(models.Video).filter(models.Video.series_id == s.id).count()
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
                "release_year": v.release_year
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
                "duration": item["duration"]
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
                "current_time": crud.get_watch_progress(db, profile_id, v.id)
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
def get_series_thumbnail(series_id: int, profile_id: int, db: Session = Depends(get_db)):
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
        try:
            resp = requests.get(series.poster_path, stream=True, timeout=5)
            return StreamingResponse(resp.iter_content(chunk_size=1024), media_type=resp.headers.get("Content-Type", "image/jpeg"))
        except:
             return FileResponse(os.path.join(config.STATIC_DIR, "default_poster.jpg"))
    
    # Resolve relative path
    # 1. Try THUMBNAIL_DIR
    path1 = os.path.join(config.THUMBNAIL_DIR, series.poster_path)
    if os.path.exists(path1):
        return FileResponse(path1, media_type="image/jpeg")
        
    # 2. Try MEDIA_DIR (local posters)
    media_dir_setting = crud.get_setting(db, "media_dir")
    media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
    path2 = os.path.join(media_base, series.poster_path)
    if os.path.exists(path2):
        return FileResponse(path2, media_type="image/jpeg")
        
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
    if not os.path.isabs(full_path):
        media_dir_setting = crud.get_setting(db, "media_dir")
        media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
        full_path = os.path.join(media_base, video.filepath)

    if not os.path.exists(full_path):
         raise HTTPException(status_code=404, detail="Video file not found on disk")
    return FileResponse(full_path, media_type="video/mp4", filename=video.title)

@app.get("/thumbnail/{video_id}")
def get_thumbnail(video_id: int, profile_id: int, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    video = crud.get_video(db, video_id)
    
    if not video or not profile:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    allowed = crud.get_allowed_categories(profile.age_category)
    if video.category not in allowed:
        raise HTTPException(status_code=403, detail="Access denied for this profile category")
    
    if not video.thumbnail_path:
         raise HTTPException(status_code=404, detail="Thumbnail not found")

    if video.thumbnail_path.startswith("http"):
        try:
            resp = requests.get(video.thumbnail_path, stream=True, timeout=5)
            return StreamingResponse(resp.iter_content(chunk_size=1024), media_type=resp.headers.get("Content-Type", "image/jpeg"))
        except:
             return FileResponse(os.path.join(config.STATIC_DIR, "default_poster.jpg"))
    
    # Resolve relative path
    # 1. Try THUMBNAIL_DIR (generated thumbs)
    thumb_path = os.path.join(config.THUMBNAIL_DIR, video.thumbnail_path)
    if os.path.exists(thumb_path):
        return FileResponse(thumb_path, media_type="image/jpeg")
        
    # 2. Try MEDIA_DIR (local posters)
    media_dir_setting = crud.get_setting(db, "media_dir")
    media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
    media_path = os.path.join(media_base, video.thumbnail_path)
    if os.path.exists(media_path):
        return FileResponse(media_path, media_type="image/jpeg")
    
    # 3. Fallback
    return FileResponse(os.path.join(config.STATIC_DIR, "default_poster.jpg"))

@app.get("/thumbnail/backdrop/{video_id}")
def get_video_backdrop(video_id: int, profile_id: int, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    video = crud.get_video(db, video_id)
    
    if not video or not profile:
        raise HTTPException(status_code=404, detail="Not found")
        
    if video.category not in crud.get_allowed_categories(profile.age_category):
          raise HTTPException(status_code=403, detail="Access denied")

    if video.backdrop_path:
        if video.backdrop_path.startswith("http"):
            try:
                resp = requests.get(video.backdrop_path, stream=True, timeout=5)
                return StreamingResponse(resp.iter_content(chunk_size=1024), media_type=resp.headers.get("Content-Type", "image/jpeg"))
            except: pass

        # 1. Try THUMBNAIL_DIR
        path1 = os.path.join(config.THUMBNAIL_DIR, video.backdrop_path)
        if os.path.exists(path1):
            return FileResponse(path1)
            
        # 2. Try MEDIA_DIR
        media_dir_setting = crud.get_setting(db, "media_dir")
        media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
        path2 = os.path.join(media_base, video.backdrop_path)
        if os.path.exists(path2):
            return FileResponse(path2)
            
    # Fallback to poster
    if video.thumbnail_path:
        # Try both dirs for poster too
        path1 = os.path.join(config.THUMBNAIL_DIR, video.thumbnail_path)
        if os.path.exists(path1): return FileResponse(path1)
        
        media_dir_setting = crud.get_setting(db, "media_dir")
        media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
        path2 = os.path.join(media_base, video.thumbnail_path)
        if os.path.exists(path2): return FileResponse(path2)
            
@app.get("/thumbnail/backdrop/series/{series_id}")
def get_series_backdrop(series_id: int, profile_id: int, db: Session = Depends(get_db)):
    profile = crud.get_profile(db, profile_id)
    series = crud.get_series(db, series_id)
    
    if not series or not profile:
        raise HTTPException(status_code=404, detail="Not found")
        
    if series.category not in crud.get_allowed_categories(profile.age_category):
          raise HTTPException(status_code=403, detail="Access denied")

    if series.backdrop_path:
        if series.backdrop_path.startswith("http"):
            try:
                resp = requests.get(series.backdrop_path, stream=True, timeout=5)
                return StreamingResponse(resp.iter_content(chunk_size=1024), media_type=resp.headers.get("Content-Type", "image/jpeg"))
            except: pass

        # 1. Try THUMBNAIL_DIR
        path1 = os.path.join(config.THUMBNAIL_DIR, series.backdrop_path)
        if os.path.exists(path1):
            return FileResponse(path1)
            
        # 2. Try MEDIA_DIR
        media_dir_setting = crud.get_setting(db, "media_dir")
        media_base = media_dir_setting.value if media_dir_setting else config.MEDIA_DIR
        path2 = os.path.join(media_base, series.backdrop_path)
        if os.path.exists(path2):
            return FileResponse(path2)
            
    raise HTTPException(status_code=404, detail="Backdrop not found")

@app.get("/video/{video_id}/scrub/{timestamp}")
def get_video_scrub(video_id: int, timestamp: int, db: Session = Depends(get_db)):
    video = crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # We assume 10s intervals
    interval = 10
    index = (timestamp // interval) + 1
    filename = f"thumb_{index:05d}.jpg"
    
    scrub_dir = os.path.join(config.THUMBNAIL_DIR, "scrub", str(video_id))
    full_path = os.path.join(scrub_dir, filename)
    
    if not os.path.exists(full_path):
        # Fallback to standard thumbnail
        std_thumb = os.path.join(config.THUMBNAIL_DIR, video.thumbnail_path)
        if os.path.exists(std_thumb):
            return FileResponse(std_thumb, media_type="image/jpeg")
        raise HTTPException(status_code=404, detail="Scrub thumbnail not found")
        
    return FileResponse(full_path, media_type="image/jpeg")

@app.post("/video/{video_id}/generate-scrub")
def generate_video_scrub(video_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    video = crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_abs_path = os.path.join(config.MEDIA_DIR, video.filepath)
    scrub_dir = os.path.join(config.THUMBNAIL_DIR, "scrub", str(video_id))
    
    background_tasks.add_task(utils.generate_scrub_thumbnails, video_abs_path, scrub_dir)
    return {"message": "Scrub generation started in background"}
