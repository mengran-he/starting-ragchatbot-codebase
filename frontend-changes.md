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
