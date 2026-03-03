# Frontend Changes

## Feature: Dark/Light Mode Theme Toggle Button

### Files Modified

- `frontend/index.html`
- `frontend/style.css`
- `frontend/script.js`

---

### index.html

- Added a `<button id="themeToggle">` element positioned outside the `.container`, fixed to the top-right of the viewport.
- The button contains two inline SVG icons:
  - **Sun icon** — displayed in dark mode; clicking switches to light mode.
  - **Moon icon** — displayed in light mode; clicking switches to dark mode.
- Both icons include `aria-hidden="true"` since the button itself carries an `aria-label`.
- Button has `aria-label="Toggle light/dark mode"` and `title="Toggle theme"` for accessibility.
- Bumped stylesheet cache-bust version (`style.css?v=12`) and script version (`script.js?v=11`).

---

### style.css

**Theme switching mechanism — `data-theme` attribute:**
- The dark theme is the default, defined on `:root`.
- The light theme is applied via `[data-theme="light"]` on the `<html>` element, overriding only the variables that differ.

**Dark theme variables (`:root` defaults):**
| Variable | Value |
|---|---|
| `--background` | `#0f172a` |
| `--surface` | `#1e293b` |
| `--surface-hover` | `#334155` |
| `--text-primary` | `#f1f5f9` |
| `--text-secondary` | `#94a3b8` |
| `--border-color` | `#334155` |
| `--assistant-message` | `#374151` |
| `--shadow` | `rgba(0,0,0,0.3)` |
| `--source-link-color` | `#60a5fa` |
| `--code-bg` | `rgba(0,0,0,0.2)` |

**Light theme overrides (`[data-theme="light"]`):**
| Variable | Light value |
|---|---|
| `--background` | `#f8fafc` |
| `--surface` | `#ffffff` |
| `--surface-hover` | `#f1f5f9` |
| `--text-primary` | `#0f172a` |
| `--text-secondary` | `#64748b` |
| `--border-color` | `#e2e8f0` |
| `--assistant-message` | `#f1f5f9` |
| `--shadow` | `rgba(0,0,0,0.1)` |
| `--welcome-bg` | `#eff6ff` |
| `--source-link-color` | `#1d4ed8` (WCAG AA on white) |
| `--code-bg` | `rgba(0,0,0,0.06)` |

**Accessibility improvement — source links and code blocks:**
- Source link colors were previously hardcoded (`#60a5fa`), which fails WCAG AA contrast on a white background.
- Replaced all hardcoded source-link and code-block colors with CSS variables (`--source-link-color`, `--source-link-bg`, `--source-link-border`, `--source-link-hover`, `--source-link-shadow`, `--code-bg`).
- Light mode uses `#1d4ed8` for source links (~5.9:1 contrast on white, passes WCAG AA).

**Smooth theme transitions:**
- Added `transition: background-color 0.3s ease, color 0.3s ease` to `body`.
- Added `transition` shorthand for `background-color`, `border-color`, `color`, `box-shadow` to key surfaces: `.sidebar`, `.chat-container`, `.message-content`, `#chatInput`, `.stat-item`, `.suggested-item`, `.source-link`, etc.

**Toggle button styles (`.theme-toggle`):**
- `position: fixed; top: 1rem; right: 1rem; z-index: 1000` — top-right placement.
- Circular shape (`border-radius: 50%`, `width/height: 40px`).
- Uses `--surface`, `--border-color`, and `--text-secondary` CSS variables so it adapts automatically to each theme.
- `:hover` scales up (`transform: scale(1.1)`) and shifts to `--primary-color`.
- `:focus` / `:focus-visible` show a clear focus ring for keyboard navigation.

**Icon animation:**
- Both `.sun-icon` and `.moon-icon` are `position: absolute` inside the button with `transition: transform 0.4s ease, opacity 0.3s ease`.
- Dark mode (default): sun fades in at `rotate(0deg) scale(1)`; moon fades out at `rotate(-90deg) scale(0.5)`.
- Light mode (`[data-theme="light"]`): moon fades in at `rotate(0deg) scale(1)`; sun fades out at `rotate(90deg) scale(0.5)`.

---

### script.js

- Added `themeToggle` to the DOM element references.
- Added an **IIFE** that runs before `DOMContentLoaded` to read `localStorage.getItem('theme')` and call `document.documentElement.setAttribute('data-theme', 'light')` immediately, preventing a flash of the wrong theme on page load.
- Registered a `click` listener on `#themeToggle` that:
  1. Reads the current `data-theme` attribute on `<html>` to determine the active theme.
  2. Sets or removes `data-theme="light"` on `document.documentElement` accordingly.
  3. Persists the chosen theme to `localStorage` (`'light'` or `'dark'`).
  4. Updates `aria-label` dynamically to reflect the next action ("Switch to dark mode" / "Switch to light mode").
