# StreamOS Development Guide

This guide provides a detailed overview of the StreamOS architecture, API, and development practices.

## 🏛️ Architecture Overview

StreamOS is built with a modern, decoupled architecture:
- **Frontend**: A Vue 3 application built with Vite, utilizing a "Liquid Glass" design aesthetic.
- **Backend**: A FastAPI (Python) server managing the media library, database, and streaming.
- **Database**: SQLite for lightweight, file-based data persistence.
- **Media Pipeline**: A custom indexing engine that scans your file system, parses metadata, and generates thumbnails using FFmpeg.

---

## 🛠️ Backend Development

### Project Structure
```bash
backend/
├── app/
│   ├── main.py        # FastAPI entry point & routes
│   ├── scanner.py     # Media indexing engine
│   ├── models.py      # SQLAlchemy database models
│   ├── crud.py        # Database operations (Create, Read, Update, Delete)
│   ├── schemas.py     # Pydantic models for API validation
│   ├── config.py      # System-wide configuration & constants
│   ├── tmdb.py        # TMDB API integration
│   └── utils.py       # Helper functions (FFmpeg, image processing)
├── media/             # Default media source (category-based folders)
├── thumbnails/        # Storage for generated assets
└── requirements.txt   # Python dependencies
```

### Media Indexing
StreamOS uses a path-based categorization system for age filtering:
1. `media/kids/` -> **Kids** category
2. `media/teen/` -> **Teen** category
3. `media/adult/` (or any other folder) -> **Adult** category

**Metadata Parsing Logic**:
- **Episodes**: Matches patterns like `S01E01`, `1x01`, or `Season 1 Episode 1`.
- **Movies**: Matches `Title (Year)`.
- **NFO Files**: Scans for `.nfo` files to extract rich metadata.
- **Local Artwork**: Prioritizes `poster.jpg`, `backdrop.jpg`, and folder-level artwork.

---

## 🎨 Frontend Development

### Tech Stack
- **Framework**: Vue 3 (Composition API)
- **Bundler**: Vite
- **Router**: Vue Router
- **Styling**: Vanilla CSS with a centralized `assets/styles.css` for design tokens.

### Design Principles: "Liquid Glass"
- **Glassmorphism**: 15px blurred backgrounds, subtle borders, and red/cyan glows.
- **Typography**: Inter (Modern, geometric sans-serif).
- **Interactive**: Scale-zooming profile icons and horizontal infinite-scrolling video rows.

---

## 🔌 API Documentation

The backend provides a RESTful API for all system operations.

### 🤖 Automatic Documentation
StreamOS leverages FastAPI's automatic documentation generation. Once the backend is running, you can access interactive documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 📋 Request & Response Examples

#### Get Profiles
`GET /profiles`
**Response:**
```json
[
  {
    "id": 1,
    "username": "Zakir",
    "age_category": "adult",
    "avatar_url": "/public/avatars/avatar1.png",
    "theme": "midnight"
  }
]
```

#### Get Library
`GET /library?profile_id=1`
**Response:**
```json
{
  "movies": [
    {
      "id": 42,
      "title": "Inception",
      "thumbnail_url": "http://localhost:8000/thumbnail/42",
      "type": "movie",
      "release_year": 2010
    }
  ],
  "tv_shows": [],
  "anime": [],
  "continue_watching": []
}
```

#### Update Progress
`POST /progress`
**Request:**
```json
{
  "profile_id": 1,
  "video_id": 42,
  "current_time": 1250,
  "duration": 8400
}
```

---

## 🛠️ Troubleshooting

### FFmpeg Issues
StreamOS requires FFmpeg for generating video scrub thumbnails.
- **Error**: `FFmpeg not found` or thumbnails are not generating.
- **Fix**: Ensure `ffmpeg` is in your system's PATH. 
  - **Windows**: [Download from gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add the `bin` folder to your Environment Variables.
  - **Linux**: `sudo apt install ffmpeg`
  - **macOS**: `brew install ffmpeg`

### Database Locked
Since StreamOS uses SQLite, the database file may occasionally become "locked" during heavy write operations (like a full library scan).
- **Fix**: Restart the backend service. If the issue persists, ensure no other process (like a DB browser) is holding an exclusive lock on `backend/streamos.db`.

### CORS Errors
If the frontend cannot connect to the backend:
- **Fix**: Ensure `VITE_API_BASE` in `streamos-ui/.env` matches your backend URL. If running on a non-standard IP, add it to `ALLOWED_ORIGINS` in your backend environment.

---

## 📊 Database Schema

StreamOS uses a relational SQLite database. Below is the entity relationship diagram:

```mermaid
erDiagram
    profiles ||--o{ watch_progress : tracks
    videos ||--o{ watch_progress : has
    series ||--o{ videos : contains
    
    profiles {
        int id PK
        string username
        string age_category
        string avatar_url
        string theme
    }
    
    series {
        int id PK
        string title
        string description
        string poster_path
        string backdrop_path
        string category
        string folder_category
        string cast
        string director
        string trailer_url
    }
    
    videos {
        int id PK
        string title
        string filepath
        string thumbnail_path
        string backdrop_path
        string category
        string folder_category
        string type
        int series_id FK
        int season
        int episode
        int release_year
        string description
        string cast
        string director
        string trailer_url
        int duration
    }
    
    watch_progress {
        int id PK
        int profile_id FK
        int video_id FK
        int current_time
    }
    
    settings {
        string key PK
        string value
    }
```

---

## ⚙️ Configuration

StreamOS can be configured via environment variables and the internal settings table.

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `TMDB_API_KEY` | API key for fetching metadata from TMDB. | `None` |
| `VITE_API_BASE` | (Frontend) The base URL of the FastAPI backend. | `http://localhost:8000` |

### Internal Settings (`settings` table)
| Key | Description |
|-----|-------------|
| `media_dir` | The root directory where media is stored. |
| `offline_mode` | If `true`, disables all external API calls (TMDB). |
| `tmdb_api_key` | Mirror of the environment variable, editable via UI. |

---

## 🚢 Production Deployment

For production environments, it is recommended to use a robust WSGI/ASGI server and a static file server.

### 1. Backend (Uvicorn + Gunicorn)
Run the backend with multiple workers for better performance:
```bash
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### 2. Frontend (Static Hosting)
Build the frontend and serve the `dist` folder using Nginx, Apache, or any static host:
```bash
cd streamos-ui
npm run build
```

### 3. Docker (Recommended)
The easiest way to deploy StreamOS is using Docker Compose:
```bash
docker-compose up -d --build
```
This will:
- Build and start the FastAPI backend.
- Build and start the Vue frontend (served by Nginx).
- Automatically proxy `/api/` requests from the frontend to the backend.
- Mount your `media/` and `thumbnails/` folders for persistence.

---

## 🛠️ Development Setup & Tasks

### Adding New Features
1. **Model Changes**: Update `models.py` and run migrations (if applicable).
2. **API Routes**: Add new endpoints in `main.py` using appropriate Pydantic schemas.
3. **UI Components**: Create or update Vue components in `streamos-ui/src/components`.

### Useful Commands
- **Regenerate Database**: Delete `backend/streamos.db` and restart the backend.
- **Clear Thumbnails**: Delete all folders inside `backend/thumbnails/` (except the directory itself).
- **Run Scan Manually**: Execute `python -m app.scanner` from the `backend/` directory.

### Dependency Management
- **Backend**: Add new packages to `backend/requirements.txt`.
- **Frontend**: Use `npm install` and ensure `package.json` is updated.
