# Phala Network Deployment Checklist

## Overview

This checklist provides step-by-step instructions for deploying Tuxedo AI to Phala Network's Trusted Execution Environment (TEE) using the Phala Cloud CLI.

**VibeVM vs CLI Recommendation:** Use the **Phala Cloud CLI** for production deployments. VibeVM is primarily for demos and development, while CLI provides proper automation, versioning, and CI/CD integration.

## Prerequisites

### ✅ Account Setup
- [ ] Phala Cloud account created with credits available
- [ ] Phala Cloud API key obtained from dashboard
- [ ] Docker Hub account (for private images if needed)

### ✅ Local Development
- [ ] Docker installed locally
- [ ] Node.js 18+ installed
- [ ] Project builds successfully: `npm run build`
- [ ] Docker images build successfully: `docker build -f Dockerfile.backend -t tuxedo-backend .`

## Step 1: Install Phala CLI

### Option A: Using npx (Recommended)
```bash
# Install globally
npm install -g @phala-cloud/cli

# Or use with npx (no installation needed)
npx phala --help
```

### Option B: Direct installation
```bash
curl -sSL https://install.phala.network | bash
```

### Authentication
```bash
# Login with API key from Phala Cloud dashboard
phala auth login
# Enter your API key when prompted

# Verify authentication
phala account status
```

## Step 2: Prepare Docker Compose Configuration

### ✅ Create Phala-specific docker-compose file

Create `docker-compose.phala.yaml`:

```yaml
version: '3.8'

services:
  tuxedo-backend:
    image: your-dockerhub-username/tuxedo-backend:latest
    container_name: tuxedo-backend
    ports:
      - "8000:8000"
    volumes:
      - phala-data:/app/data  # Persistent TEE encrypted storage
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=https://openrouter.ai/api/v1
      - PRIMARY_MODEL=openai/gpt-oss-120b:exacto
      - STELLAR_NETWORK=testnet
      - HORIZON_URL=https://horizon-testnet.stellar.org
      - SOROBAN_RPC_URL=https://soroban-testnet.stellar.org
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  tuxedo-frontend:
    image: your-dockerhub-username/tuxedo-frontend:latest
    container_name: tuxedo-frontend
    ports:
      - "80:8080"
    depends_on:
      - tuxedo-backend
    environment:
      - VITE_STELLAR_NETWORK=testnet
      - VITE_HORIZON_URL=https://horizon-testnet.stellar.org
      - VITE_RPC_URL=https://soroban-testnet.stellar.org
      - VITE_API_URL=http://localhost:8000
    restart: unless-stopped

volumes:
  phala-data:
    driver: local
```

### ✅ Update Database Configuration

Update `backend/database.py` to use persistent storage:

```python
class DatabaseManager:
    def __init__(self, db_path: str = "/app/data/chat_threads.db"):
        self.db_path = db_path
        self.init_database()
```

## Step 3: Build and Push Docker Images

### ✅ Backend Docker Image
```bash
# Build backend image
docker build -f Dockerfile.backend -t your-dockerhub-username/tuxedo-backend:latest .

# Tag with version for updates
docker tag your-dockerhub-username/tuxedo-backend:latest your-dockerhub-username/tuxedo-backend:v1.0.0

# Push to Docker Hub
docker push your-dockerhub-username/tuxedo-backend:latest
docker push your-dockerhub-username/tuxedo-backend:v1.0.0
```

### ✅ Frontend Docker Image
```bash
# Build frontend image
docker build -f Dockerfile.frontend -t your-dockerhub-username/tuxedo-frontend:latest .

# Tag with version
docker tag your-dockerhub-username/tuxedo-frontend:latest your-dockerhub-username/tuxedo-frontend:v1.0.0

# Push to Docker Hub
docker push your-dockerhub-username/tuxedo-frontend:latest
docker push your-dockerhub-username/tuxedo-frontend:v1.0.0
```

## Step 4: Deploy to Phala Cloud

### ✅ Create CVM (Confidential Virtual Machine)
```bash
# Deploy using CLI
phala cvms create \
  -n tuxedo-ai \
  -c ./docker-compose.phala.yaml \
  --region us-west

# Alternative with specific settings
phala cvms create \
  --name tuxedo-ai \
  --compose-file ./docker-compose.phala.yaml \
  --cpu 2 \
  --memory 4GB \
  --region us-west
```

### ✅ Verify Deployment
```bash
# List all CVMs
phala cvms list

# Check deployment status
phala cvms status tuxedo-ai

# View logs
phala cvms logs tuxedo-ai

# Access container shell (if needed)
phala cvms shell tuxedo-ai
```

## Step 5: Configure Environment Variables

### ✅ Set Secure Environment Variables
```bash
# Update environment variables
phala cvms update \
  -n tuxedo-ai \
  -e OPENAI_API_KEY=your-actual-api-key \
  -e OTHER_VAR=value

# Or update via dashboard for sensitive values
# Go to Phala Cloud Dashboard → Your CVM → Environment Variables
```

### ✅ Verify Services
```bash
# Check health endpoint
curl https://your-cvm-url.phala.network/health

# Check frontend
open https://your-cvm-url.phala.network
```

## Step 6: Database Persistence Verification

### ✅ Verify SQLite Persistence
```bash
# Access backend container
phala cvms shell tuxedo-ai

# Check database exists
ls -la /app/data/

# Verify database tables
sqlite3 /app/data/chat_threads.db ".tables"

# Exit container
exit
```

### ✅ Test Data Persistence
1. Create a chat thread via the web interface
2. Restart the CVM: `phala cvms restart tuxedo-ai`
3. Verify chat thread still exists

## Step 7: Updates and Maintenance

### ✅ Update Application
```bash
# Build new version with incremented tag
docker build -f Dockerfile.backend -t your-dockerhub-username/tuxedo-backend:v1.0.1 .
docker push your-dockerhub-username/tuxedo-backend:v1.0.1

# Update docker-compose.yaml with new image tag
# Update deployment
phala cvms update \
  -n tuxedo-ai \
  -c ./docker-compose.phala.yaml

# Monitor update progress
phala cvms logs -f tuxedo-ai
```

### ✅ Backup Strategy
```bash
# Create data backup
phala cvms exec tuxedo-ai -- tar -czf /tmp/backup.tar.gz -C /app data/

# Download backup
phala cvms download tuxedo-ai /tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz
```

## Troubleshooting

### 🔍 Common Issues

**Deployment Fails:**
```bash
# Check compose file syntax
docker-compose -f docker-compose.phala.yaml config

# Verify images exist
docker pull your-dockerhub-username/tuxedo-backend:latest

# Check quota and credits
phala account status
```

**Container Won't Start:**
```bash
# View detailed logs
phala cvms logs tuxedo-ai --tail 100

# Check resource usage
phala cvms stats tuxedo-ai
```

**Database Connection Issues:**
```bash
# Access container and check database
phala cvms shell tuxedo-ai
cd /app/data
ls -la
sqlite3 chat_threads.db ".schema"
```

**Network Issues:**
```bash
# Check port mappings
phala cvms exec tuxedo-ai -- netstat -tlnp

# Test internal connectivity
phala cvms exec tuxedo-frontend -- curl http://tuxedo-backend:8000/health
```

## Security Best Practices

### 🔒 TEE Security
- [ ] Verify TEE attestation at `https://proof.t16z.com`
- [ ] Use environment variables for secrets (never hardcode)
- [ ] Enable health checks for monitoring
- [ ] Regularly update Docker images
- [ ] Monitor logs for unusual activity

### 🔒 API Security
- [ ] Use HTTPS endpoints
- [ ] Validate all user inputs
- [ ] Implement rate limiting
- [ ] Use secure API key management

## Cost Optimization

### 💰 Resource Management
- [ ] Monitor resource usage: `phala cvms stats tuxedo-ai`
- [ ] Right-size CPU and memory allocation
- [ ] Set up auto-shutdown for non-production environments
- [ ] Use appropriate instance regions

### 💰 Credits Management
- [ ] Monitor credit usage in dashboard
- [ ] Set up usage alerts
- [ ] Consider reserved instances for production

## CI/CD Integration

### 🚀 GitHub Actions Setup

Create `.github/workflows/phala-deploy.yml`:

```yaml
name: Deploy to Phala Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push backend
        run: |
          docker build -f Dockerfile.backend -t ${{ secrets.DOCKER_USERNAME }}/tuxedo-backend:${{ github.sha }} .
          docker push ${{ secrets.DOCKER_USERNAME }}/tuxedo-backend:${{ github.sha }}

      - name: Build and push frontend
        run: |
          docker build -f Dockerfile.frontend -t ${{ secrets.DOCKER_USERNAME }}/tuxedo-frontend:${{ github.sha }} .
          docker push ${{ secrets.DOCKER_USERNAME }}/tuxedo-frontend:${{ github.sha }}

      - name: Deploy to Phala
        env:
          PHALA_API_KEY: ${{ secrets.PHALA_API_KEY }}
        run: |
          phala auth login
          # Update docker-compose with new image tags
          sed -i "s|:latest|:${{ github.sha }}|g" docker-compose.phala.yaml
          phala cvms update -n tuxedo-ai -c docker-compose.phala.yaml
```

### Required GitHub Secrets
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `PHALA_API_KEY`
- `OPENAI_API_KEY`

## Post-Deployment Verification

### ✅ Health Checks
- [ ] Backend health endpoint: `/health`
- [ ] Frontend loads correctly
- [ ] Database connectivity works
- [ ] AI chat functionality works
- [ ] Stellar tools work correctly
- [ ] CORS properly configured

### ✅ Performance Monitoring
- [ ] Response times acceptable
- [ ] Memory usage stable
- [ ] CPU usage within limits
- [ ] Error rates low

## Rollback Plan

### 🔄 Emergency Rollback
```bash
# Update docker-compose.yaml with previous working image tag
phala cvms update -n tuxedo-ai -c docker-compose.phala.yaml.rollback

# Or restart to previous state
phala cvms restart tuxedo-ai
```

### 🔄 Data Recovery
```bash
# Restore from backup
phala cvms upload tuxedo-ai ./backup-latest.tar.gz /tmp/
phala cvms exec tuxedo-ai -- tar -xzf /tmp/backup-latest.tar.gz -C /app/
phala cvms restart tuxedo-ai
```

## Next Steps

### 🎯 Future Enhancements
- [ ] Vector database integration (ChromaDB, FAISS)
- [ ] Performance monitoring and alerting
- [ ] Multi-region deployment
- [ ] Load balancing for high availability
- [ ] Advanced security configurations

---

## Quick Reference Commands

```bash
# Essential CLI Commands
phala auth login                    # Authenticate
phala cvms create -n name -c file   # Deploy
phala cvms list                     # List CVMs
phala cvms status name              # Check status
phala cvms logs name                # View logs
phala cvms update -n name -c file   # Update
phala cvms restart name             # Restart
phala cvms delete name              # Delete
phala account status                # Check credits
```

---

**Deployment Date:** ___________
**Deployed By:** _________________
**Version:** ____________________
**CVM URL:** ____________________
**Notes:** _______________________