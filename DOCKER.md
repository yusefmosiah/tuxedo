# Docker Deployment Guide

This guide explains how to deploy Tuxedo using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ and Docker Compose 2.0+ installed
- OpenAI API key (required for the AI agent)

## Quick Start

### 1. Environment Setup

Copy the example environment files and fill in your configuration:

```bash
# Backend configuration
cp .env.backend.example .env.backend
# Edit .env.backend and add your OPENAI_API_KEY

# Frontend configuration (optional)
cp .env.frontend.example .env.frontend
# Edit .env.frontend if you need custom configuration
```

**Required**: You must set `OPENAI_API_KEY` in `.env.backend` for the application to work.

### 2. Production Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at:
- Frontend: http://localhost
- Backend API: http://localhost:8002
- API Documentation: http://localhost:8002/docs

### 3. Development Deployment

For development with hot reloading:

```bash
# Start backend only
docker-compose up -d backend

# Start frontend development server
docker-compose --profile dev up dev-frontend
```

The development frontend will be available at http://localhost:5173

## Services

### Backend Service
- **Container**: `tuxedo-backend`
- **Port**: 8002
- **Health Check**: `/health` endpoint
- **Environment**: Uses `.env.backend` file

### Frontend Service
- **Container**: `tuxedo-frontend`
- **Port**: 80 (HTTP), 443 (HTTPS ready)
- **Environment**: Uses `.env.frontend` file
- **Proxy**: API requests proxied to backend service

### Development Frontend (Optional)
- **Container**: `tuxedo-dev-frontend`
- **Port**: 5173
- **Hot Reload**: Enabled with volume mounts
- **Profile**: Use `--profile dev` to start

## Configuration

### Environment Variables

**Backend (.env.backend)**:
- `OPENAI_API_KEY` (required): Your OpenAI API key
- `OPENAI_BASE_URL`: API base URL, defaults to Redpill AI
- `STELLAR_NETWORK`: Stellar network, defaults to `testnet`
- `HORIZON_URL`: Stellar Horizon URL
- `SOROBAN_RPC_URL`: Soroban RPC URL

**Frontend (.env.frontend)**:
- `VITE_STELLAR_NETWORK`: Stellar network for frontend
- `VITE_HORIZON_URL`: Horizon URL for frontend
- `VITE_RPC_URL`: RPC URL for frontend
- `VITE_API_URL`: Backend API URL

### Volumes

- `backend_data`: Persistent data storage for backend
- `node_modules`: Cached Node.js dependencies for development

### Networks

Services communicate via `tuxedo-network` bridge network.

## Dockerfiles

### Frontend Dockerfile (`Dockerfile.frontend`)
Multi-stage build:
1. **Builder**: Node.js Alpine with dependencies and build
2. **Production**: Nginx Alpine serving static files

### Backend Dockerfile (`Dockerfile.backend`)
Single-stage with:
- Python 3.11 Slim base image
- uv for fast dependency installation
- Non-root user for security
- Health check endpoint

## Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs
docker-compose logs -f backend
```

### Health Checks
```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8002/health
```

## Troubleshooting

### Backend Issues
1. **OpenAI API Key**: Ensure `.env.backend` contains valid `OPENAI_API_KEY`
2. **Port Conflicts**: Check if port 8002 is already in use
3. **Dependencies**: Verify backend builds correctly with `docker-compose build backend`

### Frontend Issues
1. **Build Failures**: Check Node.js build logs
2. **API Connection**: Verify backend is healthy and network connectivity
3. **Static Files**: Ensure build completed successfully

### General Issues
1. **Docker Version**: Ensure Docker 20.10+ and Compose 2.0+
2. **Permissions**: Check Docker daemon permissions
3. **Resources**: Verify sufficient memory/disk space

## Production Considerations

### Security
- Frontend runs as non-root user
- Backend runs as non-root user
- Security headers configured in nginx
- No sensitive data in container images

### Performance
- Nginx serves static files efficiently
- Gzip compression enabled
- Static asset caching configured
- Health checks prevent unhealthy containers

### Scalability
- Services can be scaled independently:
```bash
docker-compose up -d --scale backend=2
```

- Load balancing would require external reverse proxy

## Maintenance

### Updates
```bash
# Pull latest images
docker-compose pull

# Rebuild with latest code
docker-compose build --no-cache

# Restart with updates
docker-compose up -d
```

### Cleanup
```bash
# Remove stopped containers and networks
docker-compose down

# Remove all containers, networks, volumes (CAUTION)
docker-compose down -v
```

### Backup
```bash
# Backup volumes
docker run --rm -v tuxedo-pools_backend_data:/data -v $(pwd):/backup alpine tar czf /backup/backend-data.tar.gz -C /data .
```