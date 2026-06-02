# StreamOS Design System & Style Guide 🎨

This guide outlines the visual language and "Liquid Glass" aesthetic used throughout StreamOS.

## 🏛️ Design Philosophy
The "Liquid Glass" design system focuses on **depth, transparency, and vibrant accents**. It draws inspiration from Apple's VisionOS and Netflix's "Cinematic" UI.

- **Glassmorphism**: Use of blurred backgrounds to create hierarchy.
- **Dynamic Glows**: Subtle red and cyan glows to indicate focus and interactivity.
- **Smooth Motion**: All transitions use a consistent cubic-bezier curve for a premium feel.

---

## 🎨 Color Palette

### Core Tokens (Midnight Theme)
| Token | Value | Description |
|-------|-------|-------------|
| `--bg-dark` | `#000000` | Deepest black for contrast |
| `--netflix-red` | `#E50914` | Primary action color |
| `--neon-cyan` | `#00FFFF` | Accent highlight / secondary action |
| `--glass-bg` | `rgba(255, 255, 255, 0.05)` | Base glass background |
| `--text-main` | `#FFFFFF` | Primary readable text |
| `--text-muted` | `#B3B3B3` | Secondary/metadata text |

### Cinematic Theme
The cinematic theme shifts towards deep blues and amber accents:
- **Background**: `linear-gradient(135deg, #0f172a 0%, #020617 100%)`
- **Primary**: `#8b5cf6` (Deep Purple)
- **Accent**: `#fbbf24` (Amber)

---

## 🏗️ Components

### Glass Card
Used for profiles, modals, and overlays.
```css
.glass {
  background: var(--glass-bg);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-main);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}
```

### Video Thumbnails
Thumbnails should maintain a consistent aspect ratio and provide immediate feedback on hover.
- **Normal**: `scale(1)`
- **Hover/Focus**: `scale(1.05)` + `box-shadow: 0 0 20px var(--netflix-red)`
- **Border Radius**: `12px` (standard)

### Typography
- **Primary Font**: `Inter`, `-apple-system`, `sans-serif`
- **Heading 1**: 2.5rem, Semi-bold, Letter-spacing -0.02em
- **Body**: 1rem, Regular, Line-height 1.5

---

## 📱 Layout & Spacing
- **Base Grid**: 8px system. All margins and paddings should be multiples of 8 (e.g., 8, 16, 24, 32, 48).
- **Safe Zones**: Ensure a 48px horizontal padding on TV/Desktop views to account for various screen edges.

---

## 🎬 Animation Tokens
All interactive elements should use the following transition for consistency:
- **Variable**: `--transition-smooth`
- **Value**: `all 0.4s cubic-bezier(0.25, 1, 0.5, 1)`
