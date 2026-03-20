from pydantic import BaseModel
from typing import Optional, List

class ProfileBase(BaseModel):
    username: str
    age_category: str # 'child', 'teen', 'adult'
    avatar_url: Optional[str] = None
    theme: Optional[str] = "midnight" # 'midnight', 'cinematic'

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    age_category: Optional[str] = None
    avatar_url: Optional[str] = None
    theme: Optional[str] = None

class Profile(ProfileBase):
    id: int

    class Config:
        from_attributes = True

class VideoBase(BaseModel):
    id: int
    title: str
    thumbnail_url: str
    show_name: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    type: str # 'movie', 'episode'
    release_year: Optional[int] = None
    description: Optional[str] = None
    folder_category: Optional[str] = None
    cast: Optional[str] = None
    director: Optional[str] = None
    trailer_url: Optional[str] = None
    backdrop_path: Optional[str] = None
    backdrop_url: Optional[str] = None
    current_time: Optional[int] = None
    duration: Optional[int] = None

class VideoDetail(VideoBase):
    filepath: str
    category: str

    class Config:
        from_attributes = True

class LibraryResponse(BaseModel):
    movies: List[VideoBase]
    tv_shows: List[dict]
    anime: List[dict]
    continue_watching: List[dict]
    all: List[dict]

class SystemSettingBase(BaseModel):
    key: str
    value: str

class SystemSetting(SystemSettingBase):
    class Config:
        from_attributes = True

class WatchProgressUpdate(BaseModel):
    profile_id: int
    video_id: int
    current_time: int
    duration: Optional[int] = None
    
class WatchProgressResponse(BaseModel):
    current_time: int
