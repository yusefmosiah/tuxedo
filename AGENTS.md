# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Backend Development

```bash
# Setup virtual environment (from project root)
cd backend

# Use UV for environment management
uv sync  # Creates .venv and installs all dependencies

# Always activate environment before working
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start backend server
python main.py

# Test Ghostwriter pipeline
python test_ghostwriter.py

# Test WebSearch integration
python test_websearch.py
```

## Frontend Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Lint and format
npm run lint
npm run format

# Install dependencies
npm install
```

### Starting Both Services

```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend (from backend directory)
source .venv/bin/activate && python main.py
```
