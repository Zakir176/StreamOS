import os
import re
from . import models, database, crud, utils
from .config import MEDIA_DIR, THUMBNAIL_DIR, IGNORED_MEDIA_PATTERNS

def parse_metadata(filename):
    # Common patterns: S01E01, 1x01, Season 1 Episode 1
    show_patterns = [
        r"(.*?)[\s\._\-][Ss](\d+)[\s\._\-]*[Ee](\d+)", # S01E01
        r"(.*?)[\s\._\-]*(\d+)x(\d+)",                 # 1x01
        r"(.*?)Season\s*(\d+)\s*Episode\s*(\d+)",      # Season 1 Episode 1
    ]
    
    for pattern in show_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            show_name = match.group(1).replace('.', ' ').replace('_', ' ').strip()
            season = int(match.group(2))
            episode = int(match.group(3))
            return "episode", show_name, season, episode, None
            
    # Movie patterns: Title (Year)
    movie_pattern = r"(.*?)[\s\._\-\(](\d{4})[\)\s\._\-]"
    match = re.search(movie_pattern, filename)
    if match:
        title = match.group(1).replace('.', ' ').replace('_', ' ').strip()
        year = int(match.group(2))
        return "movie", title, None, None, year
        
    return "movie", os.path.splitext(filename)[0].replace('.', ' ').replace('_', ' ').strip(), None, None, None

def scan_media():
    # Ensure DB tables exist
    models.Base.metadata.create_all(bind=database.engine)
    
    db = database.SessionLocal()
    crud.seed_defaults(db)
    
    # Get media directory from settings
    media_dir_setting = crud.get_setting(db, "media_dir")
    media_dir = media_dir_setting.value if media_dir_setting else MEDIA_DIR
    
    if not os.path.exists(media_dir):
        print(f"Error: Media directory does not exist: {media_dir}")
        db.close()
        return {
            "success": False,
            "media_dir": media_dir,
            "added": 0,
            "updated": 0,
            "removed": 0,
            "series_removed": 0,
            "message": f"Media directory does not exist: {media_dir}"
        }

    print(f"Scanning media in: {media_dir}")

    # File extensions to scan
    EXTENSIONS = (".mp4", ".mkv", ".avi")

    added_count = 0
    updated_count = 0

    for root, dirs, files in os.walk(media_dir):
        # Determine category based on path (for age filtering)
        rel_path = os.path.relpath(root, media_dir).lower()
        if "kids" in rel_path:
            category = "kids"
        elif "teen" in rel_path:
            category = "teen"
        else:
            category = "adult"
            
        # Determine folder-based category (Movies, TV Shows, Anime)
        folder_category = "Movies"
        if "tv shows" in rel_path:
            folder_category = "TV Shows"
        elif "anime" in rel_path:
            folder_category = "Anime"
        elif "movies" in rel_path:
            folder_category = "Movies"
            
        # Ensure thumbnail subdir for this category exists
        thumb_subdir = os.path.join(THUMBNAIL_DIR, category)
        os.makedirs(thumb_subdir, exist_ok=True)

        for filename in files:
            if not filename.endswith(EXTENSIONS):
                continue

            lower_name = filename.lower()
            # Skip unwanted test clips (like solid blue/green/red videos)
            if any(pattern in lower_name for pattern in IGNORED_MEDIA_PATTERNS):
                video_path = os.path.join(root, filename)
                existing = db.query(models.Video).filter(models.Video.filepath == video_path).first()
                if existing:
                    print(f"Removing ignored media: {existing.title}")
                    db.delete(existing)
                continue

            video_path = os.path.join(root, filename)
            rel_video_path = os.path.relpath(video_path, media_dir)
            
            # Extract metadata and local assets
            local_assets = utils.find_local_assets(video_path)
            v_type, title_or_show, season, episode, year = parse_metadata(filename)
            
            # Priority 1: NFO metadata
            description = None
            cast = None
            director = None
            if local_assets["nfo"]:
                nfo_meta = utils.parse_nfo(local_assets["nfo"])
                title_or_show = nfo_meta.get("title", title_or_show)
                description = nfo_meta.get("description")
                year = nfo_meta.get("release_year", year)
                cast = nfo_meta.get("cast")
                director = nfo_meta.get("director")
            
            # Priority 2: Local artwork
            local_poster_rel = None
            local_backdrop_rel = None
            if local_assets["poster"]:
                local_poster_rel = os.path.relpath(local_assets["poster"], media_dir)
            if local_assets["backdrop"]:
                local_backdrop_rel = os.path.relpath(local_assets["backdrop"], media_dir)

            series_id = None
            if v_type == "episode":
                title = f"{title_or_show} - S{season:02d}E{episode:02d}"
                show_name = title_or_show
                # Check if series exists
                series = db.query(models.Series).filter(models.Series.title == show_name).first()
                if not series:
                    # Find potential show-level assets
                    parent_dir = os.path.dirname(root)
                    show_poster = None
                    show_desc = None
                    
                    for p_name in ["poster.jpg", "folder.jpg", "banner.jpg", "show.nfo"]:
                        p_test = os.path.join(root, p_name)
                        if not os.path.exists(p_test):
                            p_test = os.path.join(parent_dir, p_name)
                            
                        if os.path.exists(p_test):
                            if p_name.endswith(".nfo"):
                                show_nfo_meta = utils.parse_nfo(p_test)
                                show_desc = show_nfo_meta.get("description")
                            elif not show_poster: # Priority to the first found image
                                show_poster = os.path.relpath(p_test, media_dir)
                    
                    # Calculate dominant color and placeholder for series
                    series_color = None
                    series_placeholder = None
                    if show_poster:
                        series_poster_path = os.path.join(media_dir, show_poster)
                        if os.path.exists(series_poster_path):
                            series_color = utils.get_dominant_color(series_poster_path)
                            series_placeholder = utils.get_blur_placeholder(series_poster_path)

                    series = models.Series(
                        title=show_name,
                        category=category,
                        folder_category=folder_category,
                        poster_path=show_poster,
                        description=show_desc,
                        dominant_color=series_color,
                        thumbnail_placeholder=series_placeholder
                    )
                    db.add(series)
                    db.flush()
                series_id = series.id
            else:
                title = title_or_show
                show_name = None
            
            # Calculate thumbnail paths
            thumb_filename = f"{os.path.splitext(filename)[0]}.webp"
            thumb_path = os.path.join(thumb_subdir, thumb_filename)
            rel_thumb_path = os.path.join(category, thumb_filename)
            
            # Use local poster as thumbnail if available
            final_thumb_rel = local_poster_rel if local_poster_rel else rel_thumb_path

            # Check if already in DB (check both absolute and relative)
            existing_video = db.query(models.Video).filter(
                (models.Video.filepath == video_path) | (models.Video.filepath == rel_video_path)
            ).first()
            
            dominant_color = None
            thumbnail_placeholder = None
            if not existing_video:
                # Generate thumbnail only if local poster is missing
                if not local_poster_rel:
                    utils.generate_thumbnail(video_path, thumb_path)
                
                # Calculate dominant color and placeholder
                asset_for_color = local_assets["poster"] or thumb_path
                if os.path.exists(asset_for_color):
                    dominant_color = utils.get_dominant_color(asset_for_color)
                    thumbnail_placeholder = utils.get_blur_placeholder(asset_for_color)

                new_video = models.Video(
                    title=title,
                    filepath=rel_video_path,
                    thumbnail_path=final_thumb_rel,
                    backdrop_path=local_backdrop_rel,
                    category=category,
                    show_name=show_name,
                    series_id=series_id,
                    season=season,
                    episode=episode,
                    type=v_type,
                    release_year=year,
                    description=description,
                    cast=cast,
                    director=director,
                    folder_category=folder_category,
                    dominant_color=dominant_color,
                    thumbnail_placeholder=thumbnail_placeholder
                )
                db.add(new_video)
                added_count += 1
                print(f"Added {v_type}: {title}")
            else:
                # Migrate and update
                existing_video.filepath = rel_video_path
                existing_video.show_name = show_name
                existing_video.series_id = series_id
                existing_video.season = season
                existing_video.episode = episode
                existing_video.title = title
                existing_video.type = v_type
                existing_video.release_year = year or existing_video.release_year
                existing_video.folder_category = folder_category
                existing_video.thumbnail_path = final_thumb_rel
                existing_video.backdrop_path = local_backdrop_rel or existing_video.backdrop_path
                existing_video.category = category
                existing_video.description = description or existing_video.description
                existing_video.cast = cast or existing_video.cast
                existing_video.director = director or existing_video.director
                
                if not local_poster_rel and not os.path.exists(thumb_path):
                    utils.generate_thumbnail(video_path, thumb_path)
                
                # Update dominant color and placeholder if missing
                if not existing_video.dominant_color or not existing_video.thumbnail_placeholder:
                    asset_for_color = local_assets["poster"] or thumb_path
                    if os.path.exists(asset_for_color):
                        existing_video.dominant_color = existing_video.dominant_color or utils.get_dominant_color(asset_for_color)
                        existing_video.thumbnail_placeholder = existing_video.thumbnail_placeholder or utils.get_blur_placeholder(asset_for_color)
                
                updated_count += 1
    
    # Optional: Cleanup videos that no longer exist on disk
    all_videos = db.query(models.Video).all()
    removed_count = 0
    for video in all_videos:
        full_path = video.filepath
        if not os.path.isabs(full_path):
            full_path = os.path.join(media_dir, video.filepath)

        if not os.path.exists(full_path):
            print(f"Removing missing video: {video.title}")
            db.delete(video)
            removed_count += 1
    
    # Cleanup empty series
    all_series = db.query(models.Series).all()
    series_removed = 0
    for series in all_series:
        if db.query(models.Video).filter(models.Video.series_id == series.id).count() == 0:
            print(f"Removing empty series: {series.title}")
            db.delete(series)
            series_removed += 1

    db.commit()
    db.close()

    return {
        "success": True,
        "media_dir": media_dir,
        "added": added_count,
        "updated": updated_count,
        "removed": removed_count,
        "series_removed": series_removed,
        "message": f"Scan completed. Added {added_count}, updated {updated_count}, removed {removed_count} videos."
    }

if __name__ == "__main__":
    scan_media()
