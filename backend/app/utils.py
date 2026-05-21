import os
import subprocess
import base64
import math
from PIL import Image, ImageStat
import io
import requests

import re

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
    # On Windows, ffprobe is usually in the same directory as ffmpeg
    _ffprobe_maybe = os.path.join(os.path.dirname(FFMPEG_EXE), "ffprobe.exe" if os.name == "nt" else "ffprobe")
    if os.path.exists(_ffprobe_maybe):
        FFPROBE_EXE = _ffprobe_maybe
    else:
        FFPROBE_EXE = "ffprobe"
except ImportError:
    FFMPEG_EXE = "ffmpeg"
    FFPROBE_EXE = "ffprobe"

def get_video_duration(video_path):
    """Get duration of video in seconds using ffprobe or ffmpeg fallback."""
    # 1. Try ffprobe (most efficient)
    try:
        cmd = [
            FFPROBE_EXE, "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        return float(output)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        # 2. Try ffmpeg fallback (parse from stderr)
        try:
            cmd = [FFMPEG_EXE, "-i", video_path]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            output, _ = process.communicate()
            
            match = re.search(r"Duration:\s(\d+):(\d+):(\d+).(\d+)", output)
            if match:
                hours, mins, secs, ms = map(int, match.groups())
                return hours * 3600 + mins * 60 + secs + ms / 100
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
            
    print(f"Warning: Could not get duration for {video_path}. Ensure FFmpeg/FFprobe is installed.")
    return 0

def generate_thumbnail(video_path, thumbnail_path, time_sec=None):
    """Smart Thumbnail Generation with better frame selection."""
    try:
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        if not thumbnail_path.lower().endswith('.webp'):
            thumbnail_path = os.path.splitext(thumbnail_path)[0] + ".webp"
        
        duration = get_video_duration(video_path)
        
        # Smart Frame Selection
        if time_sec is None:
            start_offset = min(30, duration * 0.1) if duration > 0 else 5
            best_thumb = None
            max_brightness = 0
            
            # Try a few timestamps
            for i in range(3):
                test_time = start_offset + (i * (duration * 0.2)) if duration > 0 else start_offset
                if duration > 0 and test_time > duration: break
                
                temp_thumb = f"{thumbnail_path}.temp_{i}.webp"
                cmd = [
                    FFMPEG_EXE, "-ss", str(test_time), "-i", video_path,
                    "-frames:v", "1", "-q:v", "4", "-c:v", "webp", "-y", temp_thumb
                ]
                try:
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    if os.path.exists(temp_thumb):
                        with Image.open(temp_thumb) as img:
                            stat = ImageStat.Stat(img.convert('L'))
                            brightness = stat.mean[0]
                            if brightness > max_brightness:
                                max_brightness = brightness
                                if best_thumb and os.path.exists(best_thumb): os.remove(best_thumb)
                                best_thumb = temp_thumb
                            else:
                                os.remove(temp_thumb)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if best_thumb:
                if os.path.exists(thumbnail_path): os.remove(thumbnail_path)
                os.rename(best_thumb, thumbnail_path)
                return thumbnail_path

        # Fallback to simple generation
        time_sec = time_sec or 30
        cmd = [
            FFMPEG_EXE, "-ss", str(time_sec), "-i", video_path,
            "-frames:v", "1", "-q:v", "4", "-c:v", "webp", "-y", thumbnail_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return thumbnail_path if os.path.exists(thumbnail_path) else None
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Warning: Failed to generate thumbnail for {video_path}: {e}")
        return None

def get_blur_placeholder(image_path):
    """Generate a tiny Base64 encoded WebP image for blur-up effects."""
    try:
        if not os.path.exists(image_path): return None
        with Image.open(image_path) as img:
            img = img.resize((20, 11)) # Very tiny (16:9 approx)
            buffered = io.BytesIO()
            img.save(buffered, format="WEBP", quality=10)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except:
        return None

def generate_sprite_sheet(video_path, output_path, interval=10, cols=10):
    """Generate a sprite sheet for high-performance scrubbing."""
    temp_dir = f"{output_path}_temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. Generate individual frames
    cmd = [
        FFMPEG_EXE, "-i", video_path,
        "-vf", f"fps=1/{interval},scale=160:-1",
        "-q:v", "5", "-y", os.path.join(temp_dir, "f_%05d.jpg")
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    frames = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".jpg")])
    if not frames:
        return None
        
    # 2. Stitch frames into a sprite sheet
    with Image.open(frames[0]) as first_frame:
        fw, fh = first_frame.size
        
    num_frames = len(frames)
    rows = math.ceil(num_frames / cols)
    
    sheet = Image.new("RGB", (fw * cols, fh * rows))
    
    for i, frame_path in enumerate(frames):
        with Image.open(frame_path) as img:
            x = (i % cols) * fw
            y = (i // cols) * fh
            sheet.paste(img, (x, y))
            
    sheet.save(output_path, "WEBP", quality=70)
    
    # Cleanup
    for f in frames: os.remove(f)
    os.rmdir(temp_dir)
    return {
        "path": output_path,
        "fw": fw,
        "fh": fh,
        "cols": cols,
        "interval": interval,
        "count": num_frames
    }

def get_dominant_color(image_path):
    """Calculate the dominant color of an image for Ambilight effects."""
    try:
        if not os.path.exists(image_path):
            return "rgb(20, 20, 20)"
            
        img = Image.open(image_path)
        img = img.resize((50, 50)) # Resize for speed
        img = img.convert('RGB')
        
        # Simple averaging
        pixels = list(img.getdata())
        r_total = g_total = b_total = 0
        for r, g, b in pixels:
            r_total += r
            g_total += g
            b_total += b
            
        count = len(pixels)
        return f"rgb({round(r_total/count)}, {round(g_total/count)}, {round(b_total/count)})"
    except Exception as e:
        print(f"Error calculating dominant color: {e}")
        return "rgb(20, 20, 20)"
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
