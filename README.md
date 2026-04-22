# StreamOS 🎬

StreamOS is a lightweight, self-hosted media streaming platform designed for personal use. It features a modern "Liquid Glass" UI, automated media indexing, thumbnail generation, and multi-profile content isolation with age-based filtering.

## ✨ Features

- **Liquid Glass UI**: A beautiful, responsive interface with Netflix-inspired aesthetics, glassmorphism, and smooth animations.
- **Multi-Profile Support**: Create separate profiles for family members, each with its own watch history and theme.
- **Age-Based Filtering**: Content is automatically categorized and filtered based on profile age categories (Kids, Teen, Adult).
- **Automated Media Scanner**: Automatically indexes your movies, TV shows, and anime. Supports NFO files and local posters/backdrops.
- **TMDB Integration**: Enriches your library with metadata (descriptions, cast, directors, trailers) and high-quality artwork from The Movie Database.
- **Continue Watching**: Resume your favorite content exactly where you left off.
- **In-Browser Playback**: Stream your media directly in any modern web browser.
- **Thumbnail Generation**: Automatically generates preview thumbnails and "scrub" previews for the video player.

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **FFmpeg** (required for thumbnail generation)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Create a `.env` file in the `backend` directory (optional for TMDB):
```env
TMDB_API_KEY=your_api_key_here
```
Run the server:
```bash
python -m uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd streamos-ui
npm install
```
Configure your API URL in `.env`:
```env
VITE_API_BASE=http://localhost:8000
```
Run the development server:
```bash
npm run dev
```

## 📂 Project Structure

- `backend/`: FastAPI server, SQLite database, and media scanner.
- `streamos-ui/`: Vue 3 + Vite frontend application.
- `docs/`: Detailed documentation, including the [User Manual](docs/UserManual.md) and [Development Guide](docs/DEVELOPMENT.md).
- `media/`: Default directory for your video files (organized by category).
- `thumbnails/`: Storage for generated thumbnails and metadata artwork.

## 📖 Documentation
- [User Manual](docs/UserManual.md) - How to use StreamOS.
- [Development Guide](docs/DEVELOPMENT.md) - Architecture, API, and contribution guide.
- [Media Organization Guide](docs/MEDIA_ORGANIZATION.md) - How to name and structure your files.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
