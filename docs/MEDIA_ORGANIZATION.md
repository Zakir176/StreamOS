# Media Organization Guide 📂

To ensure StreamOS accurately indexes your media library and fetches the correct metadata, follow these naming conventions and folder structures.

## 📁 Root Directory Structure

StreamOS uses a path-based approach for age-based filtering. Organize your root media folder like this:

```text
media/
├── kids/           # Accessible by Kids, Teen, and Adult profiles
│   ├── Movies/
│   └── TV Shows/
├── teen/           # Accessible by Teen and Adult profiles
│   ├── Movies/
│   └── TV Shows/
└── adult/          # Accessible ONLY by Adult profiles (Default)
    ├── Movies/
    ├── TV Shows/
    └── Anime/
```

---

## 🎬 Movies

Movies should be placed in their own folders, especially if you have local metadata (NFOs or posters).

### Recommended Structure:
```text
Movies/
└── Inception (2010)/
    ├── Inception (2010).mkv
    ├── poster.jpg          (Optional local poster)
    ├── backdrop.jpg        (Optional local background)
    └── movie.nfo           (Optional local metadata)
```

### Naming Convention:
- `Movie Title (Year).ext`
- Example: `The Matrix (1999).mp4`

---

## 📺 TV Shows & Anime

TV shows must be organized by series and season folders for the scanner to group them correctly.

### Recommended Structure:
```text
TV Shows/
└── Stranger Things/
    ├── poster.jpg          (Series-level poster)
    ├── show.nfo            (Series-level metadata)
    ├── Season 01/
    │   ├── Stranger Things - S01E01 - The Vanishing of Will Byers.mkv
    │   └── Stranger Things - S01E02.mkv
    └── Season 02/
        └── Stranger Things - S02E01.mkv
```

### Naming Conventions:
The scanner supports several common patterns:
- **S01E01**: `Show Name - S01E01 - Episode Title.mkv` (Highly Recommended)
- **1x01**: `Show Name - 1x01.mkv`
- **Season/Episode**: `Show Name Season 1 Episode 1.mkv`

---

## 🖼️ Local Assets & Metadata

StreamOS prioritizes local files over TMDB scraping. This is ideal for offline use or custom libraries.

### Supported Local Files:
- **Posters**: `poster.jpg`, `folder.jpg`, `cover.jpg`
- **Backdrops**: `backdrop.jpg`, `fanart.jpg`, `background.jpg`
- **Metadata**: `.nfo` files (XML format used by Kodi/Jellyfin/Emby)

### Sample `.nfo` Content:
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<movie>
    <title>Inception</title>
    <year>2010</year>
    <plot>A thief who steals corporate secrets through the use of dream-sharing technology...</plot>
    <director>Christopher Nolan</director>
    <actor>
        <name>Leonardo DiCaprio</name>
        <role>Cobb</role>
    </actor>
</movie>
```

---

## 🚫 Ignored Files

StreamOS will automatically ignore files containing the following patterns (configurable in `backend/app/config.py`):
- `blue`, `green`, `red` (Commonly used for test clips)
- Non-video files (anything other than `.mp4`, `.mkv`, `.avi`)

---

## 💡 Pro Tips
1. **Be Consistent**: Stick to one naming convention for your entire library.
2. **Use Years**: Including the year in parentheses `(2024)` drastically improves TMDB matching accuracy.
3. **Clean Filenames**: Avoid long, "noisy" filenames like `Movie.Title.2024.1080p.BluRay.x264-GRP.mkv`. The scanner handles them, but clean names are more reliable.
