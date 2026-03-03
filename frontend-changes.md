# Frontend Code Quality Changes

## Summary

Added frontend code quality tooling (Prettier + ESLint) with configuration files, npm scripts, and developer shell scripts.

---

## New Files

### `frontend/package.json`
- Defines the frontend as an npm package (`ragchatbot-frontend`)
- Dev dependencies: `prettier@^3.3.3`, `eslint@^8.57.0`
- npm scripts:
  - `npm run format` — auto-format all JS/HTML/CSS files with Prettier
  - `npm run format:check` — check formatting without modifying files (CI-safe)
  - `npm run lint` — run ESLint on all JS files
  - `npm run quality` — run both format:check and lint (full quality gate)

### `frontend/.prettierrc`
Prettier configuration matching the existing code style:
- `printWidth: 100` — line wrap at 100 characters
- `tabWidth: 4` — 4-space indentation (consistent with existing code)
- `singleQuote: true` — single quotes (consistent with existing code)
- `trailingComma: "es5"` — trailing commas where valid in ES5
- `endOfLine: "lf"` — consistent Unix line endings

### `frontend/.eslintrc.js`
ESLint configuration for browser-side vanilla JavaScript:
- Environment: `browser`, `es2021`
- Extends `eslint:recommended` ruleset
- `marked` declared as a global readonly (CDN-loaded library)
- Key rules enforced:
  - `no-var` — enforce `const`/`let` over `var`
  - `prefer-const` — use `const` when variable is never reassigned
  - `eqeqeq` — require strict equality (`===`)
  - `curly` — require braces for all control structures
  - `no-trailing-spaces` — no trailing whitespace
  - `no-multiple-empty-lines` — max 1 blank line, 0 at EOF
  - `quotes` — single quotes enforced
  - `semi` — semicolons required

### `frontend/scripts/check-quality.sh`
Shell script to run all quality checks in sequence:
1. Auto-installs npm dependencies if `node_modules` is missing
2. Runs `npm run format:check` (Prettier)
3. Runs `npm run lint` (ESLint)
4. Exits with error if any check fails

### `frontend/scripts/format.sh`
Shell script for auto-formatting:
1. Auto-installs npm dependencies if `node_modules` is missing
2. Runs `npm run format` to reformat all frontend files in-place

---

## Modified Files

### `frontend/script.js`
Applied formatting consistency:
- Removed trailing whitespace on line 19 (after `newChatBtn` assignment)
- Removed double blank lines (lines 35–36, after `keypress` listener setup)
- Removed extra blank line after closing brace of `setupEventListeners`
- Removed trailing whitespace after `response.json()` assignment

---

## Usage

### Install dependencies (first time)
```bash
cd frontend
npm install
```

### Auto-format all frontend files
```bash
cd frontend && npm run format
# or use the script:
./frontend/scripts/format.sh
```

### Check formatting (no file changes)
```bash
cd frontend && npm run format:check
```

### Lint JavaScript
```bash
cd frontend && npm run lint
```

### Run all quality checks
```bash
cd frontend && npm run quality
# or use the script:
./frontend/scripts/check-quality.sh
```

---

# Testing Framework Changes

## Summary

Enhanced the existing testing framework for the RAG chatbot backend with API endpoint tests, shared fixtures, and cleaner pytest configuration.

## Files Added

### `backend/tests/helpers.py`
Test app factory (`build_test_app`) that creates a minimal FastAPI app mirroring the production endpoints in `app.py` but without the static file mount. This allows endpoint tests to run in CI/test environments where the `frontend/` directory doesn't exist.

### `backend/tests/conftest.py`
Shared pytest fixtures available to all test modules:
- `mock_rag` — `MagicMock` of `RAGSystem` with sensible defaults (session creation, query response, course analytics).
- `client` — `TestClient` wired to the test app using the `mock_rag` fixture.
- `sample_query_payload` — A basic `/api/query` request body.
- `sample_query_payload_with_session` — A `/api/query` request body that includes an existing session ID.

### `backend/tests/test_api_endpoints.py`
16 tests across three endpoint classes:

**`TestQueryEndpoint` (POST /api/query)**
- Returns 200 with `answer`, `sources`, and `session_id` fields.
- Answer text and source data match mock return values.
- Auto-creates a session when none is supplied.
- Uses the provided `session_id` without calling `create_session`.
- Calls `rag.query` with the correct arguments.
- Returns 422 when the required `query` field is missing.
- Returns 500 with the exception message when the RAG system raises.
- Handles backward-compatible plain-string sources (sets `link` to `null`).
- Handles an empty sources list.

**`TestCoursesEndpoint` (GET /api/courses)**
- Returns 200 with `total_courses` and `course_titles`.
- Calls `get_course_analytics` exactly once.
- Returns 500 with the exception message on error.
- Returns an empty catalog correctly.

**`TestDeleteSessionEndpoint` (DELETE /api/session/{session_id})**
- Returns `{"status": "ok"}` with a 200 status.
- Calls `session_manager.delete_session` with the correct session ID.

## Files Modified

### `pyproject.toml`
- Added `httpx>=0.28.0` to `[dependency-groups] dev` (required by FastAPI's `TestClient`).
- Added `[tool.pytest.ini_options]` section:
  - `testpaths = ["backend/tests"]` — pytest discovers tests without specifying the path manually.
  - `pythonpath = ["backend", "backend/tests"]` — makes backend modules and test helpers importable without manual `sys.path` manipulation.
  - `addopts = "-v"` — verbose output by default.

---

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
