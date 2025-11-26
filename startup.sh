#!/bin/bash
set -e

# Frontend setup
echo "Installing frontend dependencies..."
npm install

# Backend setup
echo "Setting up backend environment..."
cd backend
uv sync
cd ..

# Start both services
echo "Starting frontend and backend servers..."
npm run dev:full
