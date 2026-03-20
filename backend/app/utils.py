import os
import subprocess

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_EXE = "ffmpeg"

def generate_thumbnail(video_path, thumbnail_path, time_sec=30):
    os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
    cmd = [
        FFMPEG_EXE,
        "-ss", str(time_sec),
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "2",
        "-y", # Overwrite if exists
        thumbnail_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print(f"Warning: ffmpeg not found ({FFMPEG_EXE}). Skipping thumbnail generation for {video_path}")
import requests

from PIL import Image
import io

def download_image(url, thumbnail_path, convert_webp=True):
    """Download an image from a URL, optionally convert to WebP, and save locally."""
    try:
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            if convert_webp:
                img = Image.open(io.BytesIO(response.content))
                # Ensure filename ends with .webp if we convert
                if not thumbnail_path.lower().endswith('.webp'):
                    thumbnail_path = os.path.splitext(thumbnail_path)[0] + ".webp"
                img.save(thumbnail_path, "WEBP", quality=80)
            else:
                with open(thumbnail_path, 'wb') as f:
                    f.write(response.content)
            return thumbnail_path # Return the actual saved path (might have changed extension)
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
    return False

def generate_scrub_thumbnails(video_path, output_dir, interval=10):
    """Generate scrub thumbnails every 'interval' seconds."""
    os.makedirs(output_dir, exist_ok=True)
    # fps=1/interval means 1 frame every 'interval' seconds
    # scale=320:-1 keeps aspect ratio with 320px width
    cmd = [
        FFMPEG_EXE,
        "-i", video_path,
        "-vf", f"fps=1/{interval},scale=320:-1",
        "-q:v", "4",
        "-y",
        os.path.join(output_dir, "thumb_%05d.jpg")
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"Error generating scrub thumbnails for {video_path}: {e}")
        return False
import xml.etree.ElementTree as ET

def parse_nfo(nfo_path):
    """Parse a .nfo XML file and return a dictionary of metadata."""
    try:
        tree = ET.parse(nfo_path)
        root = tree.getroot()
        metadata = {}
        
        # Mapping of XML tags to metadata keys
        mappings = {
            "title": "title",
            "plot": "description",
            "outline": "description", # Fallback
            "year": "release_year",
            "premiered": "release_year", # Extract year from YYYY-MM-DD
            "director": "director",
            "actor": "cast", # We'll handle multiple actors below
        }
        
        for xml_tag, meta_key in mappings.items():
            node = root.find(xml_tag)
            if node is not None and node.text:
                val = node.text.strip()
                if meta_key == "release_year":
                    try:
                        metadata[meta_key] = int(val[:4])
                    except: pass
                elif meta_key == "cast":
                    # Actors are usually in <actor><name>...</name></actor>
                    actors = []
                    for actor in root.findall("actor"):
                        name = actor.find("name")
                        if name is not None and name.text:
                            actors.append(name.text.strip())
                    if actors:
                        metadata["cast"] = ", ".join(actors[:10]) # Cap at 10
                else:
                    metadata[meta_key] = val
                    
        return metadata
    except Exception as e:
        print(f"Error parsing NFO {nfo_path}: {e}")
        return {}

def find_local_assets(video_path):
    """Find local artwork (poster, backdrop) adjacent to a video file."""
    base_dir = os.path.dirname(video_path)
    video_filename = os.path.basename(video_path)
    video_basename = os.path.splitext(video_filename)[0]
    
    poster_names = ["poster.jpg", "folder.jpg", "cover.jpg", f"{video_basename}-poster.jpg", f"{video_basename}.jpg"]
    backdrop_names = ["backdrop.jpg", "fanart.jpg", "background.jpg", f"{video_basename}-fanart.jpg", f"{video_basename}-backdrop.jpg"]
    nfo_names = ["movie.nfo", "show.nfo", f"{video_basename}.nfo"]
    
    results = {"poster": None, "backdrop": None, "nfo": None}
    
    for name in poster_names:
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            results["poster"] = path
            break
            
    for name in backdrop_names:
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            results["backdrop"] = path
            break
            
    for name in nfo_names:
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            results["nfo"] = path
            break
            
    return results
