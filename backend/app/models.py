from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    age_category = Column(String, nullable=False) # 'child', 'teen', 'adult'
    avatar_url = Column(String, nullable=True)
    theme = Column(String, nullable=False, default="midnight") # 'midnight', 'cinematic'

class Series(Base):
    __tablename__ = "series"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    poster_path = Column(String, nullable=True)
    category = Column(String, nullable=False, default="adult")
    folder_category = Column(String, nullable=True)
    cast = Column(String, nullable=True)
    director = Column(String, nullable=True)
    trailer_url = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    dominant_color = Column(String, nullable=True)
    thumbnail_placeholder = Column(String, nullable=True) # Base64 tiny image

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=False)
    category = Column(String, nullable=False, default="adult") # 'kids', 'teen', 'adult'
    show_name = Column(String, nullable=True)
    series_id = Column(Integer, nullable=True)
    season = Column(Integer, nullable=True)
    episode = Column(Integer, nullable=True)
    type = Column(String, nullable=False, default="movie") # 'movie', 'episode'
    release_year = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    folder_category = Column(String, nullable=True) # 'Movies', 'TV Shows', 'Anime'
    cast = Column(String, nullable=True)
    director = Column(String, nullable=True)
    trailer_url = Column(String, nullable=True)
    duration = Column(Integer, nullable=True) # duration in seconds
    backdrop_path = Column(String, nullable=True)
    dominant_color = Column(String, nullable=True)
    thumbnail_placeholder = Column(String, nullable=True) # Base64 tiny image

class SystemSetting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)

class WatchProgress(Base):
    __tablename__ = "watch_progress"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, nullable=False, index=True)
    video_id = Column(Integer, nullable=False, index=True)
    current_time = Column(Integer, nullable=False, default=0) # current time in seconds
