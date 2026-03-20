import requests
from . import crud, config

TMDB_API_URL = "https://api.themoviedb.org/3"

def get_tmdb_api_key(db):
    # Prioritize key from config/env
    if config.TMDB_API_KEY:
        return config.TMDB_API_KEY
    # Fallback to database setting
    setting = crud.get_setting(db, "tmdb_api_key")
    return setting.value if setting else None

def search_tmdb(db, query, media_type="movie", year=None):
    api_key = get_tmdb_api_key(db)
    if not api_key:
        return None
    
    endpoint = f"{TMDB_API_URL}/search/{media_type}"
    params = {
        "api_key": api_key,
        "query": query
    }
    if year:
        # Use year for movies or first_air_date_year for TV shows
        if media_type == "movie":
            params["year"] = str(year)
        else:
            params["first_air_date_year"] = str(year)
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]
    return None

def get_tmdb_details(db, tmdb_id, media_type="movie"):
    api_key = get_tmdb_api_key(db)
    if not api_key:
        return None
    
    endpoint = f"{TMDB_API_URL}/{media_type}/{tmdb_id}"
    params = {
        "api_key": api_key
    }
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_tmdb_credits(db, tmdb_id, media_type="movie"):
    api_key = get_tmdb_api_key(db)
    if not api_key:
        return None, None
    
    endpoint = f"{TMDB_API_URL}/{media_type}/{tmdb_id}/credits"
    params = {"api_key": api_key}
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        cast = [person["name"] for person in data.get("cast", [])[:5]]
        cast_str = ", ".join(cast) if cast else None
        
        director = None
        for person in data.get("crew", []):
            if person.get("job") == "Director":
                director = person["name"]
                break
        return cast_str, director
    return None, None

def get_tmdb_trailer(db, tmdb_id, media_type="movie"):
    api_key = get_tmdb_api_key(db)
    if not api_key:
        return None
    
    endpoint = f"{TMDB_API_URL}/{media_type}/{tmdb_id}/videos"
    params = {"api_key": api_key}
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        for video in data.get("results", []):
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                return f"https://www.youtube.com/embed/{video['key']}"
    return None
