#!/usr/bin/env bash
# Frontend code quality checks
# Runs Prettier format check and ESLint on frontend files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")"

cd "$FRONTEND_DIR"

# Install dependencies if node_modules is missing
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "==> Checking formatting with Prettier..."
npm run format:check
echo "    Formatting OK"

echo "==> Linting with ESLint..."
npm run lint
echo "    Linting OK"

echo ""
echo "All quality checks passed."
