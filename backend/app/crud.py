from sqlalchemy.orm import Session
from . import models, schemas
from .models import Video, UserProfile, SystemSetting

def get_allowed_categories(age_category):
    # Temporarily disable age-based filtering: all profiles see all categories
    return ["kids", "teen", "adult"]

def get_profiles(db: Session):
    return db.query(UserProfile).all()

def get_profile(db: Session, profile_id: int):
    return db.query(UserProfile).filter(UserProfile.id == profile_id).first()

def create_profile(db: Session, username: str, age_category: str, avatar_url: str = None, theme: str = "midnight"):
    db_profile = UserProfile(username=username, age_category=age_category, avatar_url=avatar_url, theme=theme)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def delete_profile(db: Session, profile_id: int):
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if profile:
        db.delete(profile)
        db.commit()
    return profile

def update_profile(db: Session, profile_id: int, profile_update: schemas.ProfileUpdate):
    db_profile = get_profile(db, profile_id)
    if not db_profile:
        return None
    
    update_data = profile_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_videos_for_profile(db: Session, profile_id: int):
    profile = get_profile(db, profile_id)
    if not profile:
        return []
    allowed = get_allowed_categories(profile.age_category)
    return db.query(Video).filter(Video.category.in_(allowed)).all()

def get_series_for_profile(db: Session, profile_id: int):
    profile = get_profile(db, profile_id)
    if not profile:
        return []
    allowed = get_allowed_categories(profile.age_category)
    return db.query(models.Series).filter(models.Series.category.in_(allowed)).all()

def get_series(db: Session, series_id: int):
    return db.query(models.Series).filter(models.Series.id == series_id).first()

def get_episodes_for_series(db: Session, series_id: int):
    return db.query(Video).filter(Video.series_id == series_id).order_by(Video.season, Video.episode).all()

def get_video(db: Session, video_id: int):
    return db.query(Video).filter(Video.id == video_id).first()

def get_setting(db: Session, key: str):
    return db.query(SystemSetting).filter(SystemSetting.key == key).first()

def get_settings(db: Session):
    return db.query(SystemSetting).all()

def set_setting(db: Session, key: str, value: str):
    setting = get_setting(db, key)
    if setting:
        setting.value = value
    else:
        setting = SystemSetting(key=key, value=value)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting

def seed_defaults(db: Session):
    # Create default profiles if none exist
    if not get_profiles(db):
        create_profile(db, "Dad", "adult", "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix&backgroundColor=b6e3f4")
        create_profile(db, "Mom", "adult", "https://api.dicebear.com/7.x/avataaars/svg?seed=Lola&backgroundColor=b6e3f4")
        create_profile(db, "Kid", "child", "https://api.dicebear.com/7.x/avataaars/svg?seed=Simba&backgroundColor=b6e3f4")
        print("Seeded default profiles")

def update_watch_progress(db: Session, profile_id: int, video_id: int, current_time: int, duration: int = None):
    # Update video duration if provided
    if duration:
        video = get_video(db, video_id)
        if video:
            video.duration = duration

    progress = db.query(models.WatchProgress).filter(
        models.WatchProgress.profile_id == profile_id,
        models.WatchProgress.video_id == video_id
    ).first()
    
    if progress:
        progress.current_time = current_time
    else:
        progress = models.WatchProgress(profile_id=profile_id, video_id=video_id, current_time=current_time)
        db.add(progress)
    
    db.commit()
    db.refresh(progress)
    return progress

def get_watch_progress(db: Session, profile_id: int, video_id: int):
    progress = db.query(models.WatchProgress).filter(
        models.WatchProgress.profile_id == profile_id,
        models.WatchProgress.video_id == video_id
    ).first()
    return progress.current_time if progress else 0

def get_continue_watching(db: Session, profile_id: int):
    # Get all progress entries for the user where they have watched at least 10s
    progresses = db.query(models.WatchProgress).filter(
        models.WatchProgress.profile_id == profile_id,
        models.WatchProgress.current_time > 10
    ).order_by(models.WatchProgress.id.desc()).all()
    
    if not progresses:
        return []
    
    results = []
    for p in progresses:
        video = get_video(db, p.video_id)
        if video:
            # Check if video was finished (within 60 seconds of end)
            if video.duration and p.current_time >= video.duration - 60:
                continue
                
            results.append({
                "video": video,
                "current_time": p.current_time,
                "duration": video.duration
            })
    return results

def get_next_episode(db: Session, video_id: int):
    current = get_video(db, video_id)
    if not current or not current.series_id:
        return None
        
    # Try next episode in same season
    next_ep = db.query(Video).filter(
        Video.series_id == current.series_id,
        Video.season == current.season,
        Video.episode > current.episode
    ).order_by(Video.episode.asc()).first()
    
    if next_ep:
        return next_ep
        
    # Try first episode of next season
    next_season_ep = db.query(Video).filter(
        Video.series_id == current.series_id,
        Video.season > current.season
    ).order_by(Video.season.asc(), Video.episode.asc()).first()
    
    return next_season_ep
