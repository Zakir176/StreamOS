StreamOS Frontend - Production Architecture
---
### 💎 UI Design: "Liquid Glass"
- **Theme**: Dark Mode (Liquid Gradient #1a1a1a -> #000000)
- **Accents**: Netflix Red (#E50914) & Neon Cyan (#00FFFF)
- **Aesthetic**: 15px Glassmorphism cards, blurred backgrounds, Inter typography.

### 🔄 Profile Architecture
Users are managed via `localStorage` after selection:
- `profile_id`: Used for secure API requests (stream/thumbnail/library).
- `profile_name`: Displayed in the navigation bar.
- `profile_category`: Used to customize library headers (KIDS, TEEN, ADULT).

### 🚀 Tech Stack
- **Framework**: Vue 3 + Vite.
- **Routing**: Settings, Home, Library.
- **Styling**: Vanilla CSS with global `assets/styles.css` tokens.

✅ Implemented Components
- **Home**: Dynamic profile gate with scale-zooming glass icons.
- **Library**: Hero Billboard + infinite row-scroll with red glow hover effects.
- **Library Nav**: Profile dropdown with "Switch Profile", "Settings", and "Sign Out".
- **Settings**: Full CRUD for profiles + Click-to-Switch functionality.
- **VideoPlayer**: Minimalist back-arrow & back-button immersion.
