# Deployment Guide

This guide covers deployment options for the Tuxedo AI agent.

## 🚀 Quick Start

### Local Development
```bash
# Clone and setup
git clone <repository>
cd blend-pools

# Frontend (Terminal 1)
npm run dev

# Backend (Terminal 2)
cd backend
source .venv/bin/activate
python main.py
```

### Docker Development
```bash
# Development mode with hot reload
docker compose --profile dev up

# Production mode
docker compose up -d
```

## 📋 Deployment Options

### 1. Local Development
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **Use case**: Development and testing

### 2. Docker Production
- **Frontend**: http://localhost:80
- **Backend**: http://localhost:8000
- **Use case**: Staging and production

### 3. Phala TEE Deployment
- **Use case**: Secure production deployment
- **See**: [PHALA_DEPLOYMENT.md](./PHALA_DEPLOYMENT.md)

## 🔧 Environment Configuration

### Frontend Environment (.env.local)
```env
VITE_STELLAR_NETWORK=testnet
VITE_HORIZON_URL=https://horizon-testnet.stellar.org
VITE_RPC_URL=https://soroban-testnet.stellar.org
VITE_API_URL=http://localhost:8000
```

### Backend Environment (.env)
```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.redpill.ai/v1
STELLAR_NETWORK=testnet
HORIZON_URL=https://horizon-testnet.stellar.org
SOROBAN_RPC_URL=https://soroban-testnet.stellar.org
```

## 🐳 Docker Configuration

### Services
- **Frontend**: React + Vite served via `serve`
- **Backend**: FastAPI + Python
- **Network**: Internal Docker network

### Port Mapping
- Frontend: 80:8080 (external:container)
- Backend: 8000:8000

### Health Checks
- Frontend: HTTP GET to / (every 30s)
- Backend: HTTP GET to /health (every 30s)

## 🔍 Verification

### Health Checks
```bash
# Frontend health
curl http://localhost:80

# Backend health
curl http://localhost:8000/health

# API docs
curl http://localhost:8000/docs
```

### AI Agent Test
```bash
# Test AI agent functionality
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the Stellar network status?"}'
```

## 🚨 Troubleshooting

### Common Issues

**Backend not starting**
- Check OPENAI_API_KEY in .env
- Verify Python dependencies
- Check port 8000 availability

**Frontend can't reach backend**
- Verify API_URL configuration
- Check docker network connectivity
- Ensure backend is healthy

**Build failures**
- Clear node_modules and npm ci
- Check Python version (3.11+)
- Verify Docker build logs

### Performance Tuning

**Backend**
- Enable uvicorn workers for production
- Configure connection pooling
- Monitor memory usage

**Frontend**
- Use production build optimizations
- Enable proper caching headers
- Monitor bundle size

## 📚 Additional Resources

- [Architecture Documentation](./ARCHITECTURE.md)
- [Development Guide](./CLAUDE.md)
- [Docker Configuration](./DOCKER.md)
- [Phala TEE Deployment](./PHALA_DEPLOYMENT.md)