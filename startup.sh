#!/bin/bash
set -e

echo "--- Setting up environment ---"

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# Install backend dependencies
echo "Installing backend dependencies..."
(cd backend && uv sync)

# Run frontend linter
echo "Running frontend linter..."
npm run lint

# Run backend tests
echo "Running backend tests..."
(cd backend && uv run pytest)

echo "--- Environment setup and verification complete ---"
