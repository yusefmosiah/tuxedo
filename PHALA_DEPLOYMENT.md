# Phala TEE Deployment Guide

This guide covers deploying Tuxedo AI agent to Phala's Trusted Execution Environment (TEE).

## 🏗️ Architecture Overview

Phala TEE provides secure, isolated execution environments with the following benefits:
- **Secure by default**: Encrypted memory and isolated execution
- **Verifiable**: Remote attestation of running code
- **Serverless**: Pay-per-use model with automatic scaling
- **Blockchain integration**: Direct access to smart contracts

## 📋 Prerequisites

### Requirements
- Phala wallet with sufficient tokens
- Docker Compose configuration ready
- Environment variables configured
- Basic understanding of blockchain concepts

### Accounts & Tokens
- Phala network account
- Test deployment tokens
- Access to Phala developer console

## 🔧 Configuration for Phala TEE

### Docker Compose Adjustments

The standard `docker-compose.yaml` is Phala-ready with these considerations:

```yaml
services:
  frontend:
    build:
      dockerfile: Dockerfile.frontend-fixed
    ports:
      - "80:8080"  # Phala expects port 80
    environment:
      - VITE_API_URL=http://backend:8000  # Internal network

  backend:
    build:
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"  # Direct backend access
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - STELLAR_NETWORK=testnet
```

### Environment Variables for TEE

**Frontend (.env.frontend):**
```env
VITE_STELLAR_NETWORK=testnet
VITE_HORIZON_URL=https://horizon-testnet.stellar.org
VITE_RPC_URL=https://soroban-testnet.stellar.org
VITE_API_URL=http://backend:8000
VITE_PHALA_TEE=true
```

**Backend (.env.backend):**
```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.redpill.ai/v1
STELLAR_NETWORK=testnet
HORIZON_URL=https://horizon-testnet.stellar.org
SOROBAN_RPC_URL=https://soroban-testnet.stellar.org
PHALA_TEE=true
PYTHONUNBUFFERED=1
```

## 🚀 Deployment Steps

### 1. Prepare Your Project
```bash
# Clone and setup
git clone <repository>
cd blend-pools

# Verify local setup
docker compose config
docker compose build
```

### 2. Configure Phala Environment
```bash
# Set environment variables
export OPENAI_API_KEY="your_api_key"
export PHALA_NETWORK="testnet"  # or "mainnet"

# Verify configuration
docker compose --env-file .env.backend config
```

### 3. Build for Phala
```bash
# Build production images
docker compose build --no-cache

# Test locally first
docker compose up -d
curl http://localhost/health
curl http://localhost:8000/health
```

### 4. Deploy to Phala
```bash
# Using Phala CLI
phala deploy blend-pools \
  --compose-file docker-compose.yaml \
  --env-file .env.backend \
  --network testnet

# Or via Phala Console
# Upload docker-compose.yaml and environment files
```

### 5. Configure Networking
```bash
# Set up domain (optional)
phala domain set your-domain.phala.app \
  --target frontend:80

# Configure SSL (Phala provides automatic TLS)
phala ssl enable your-domain.phala.app
```

## 🔍 Deployment Verification

### Health Checks
```bash
# Check Phala deployment status
phala status blend-pools

# Test frontend
curl https://your-domain.phala.app/

# Test backend
curl https://your-domain.phala.app/api/health

# Test AI agent
curl -X POST https://your-domain.phala.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from Phala TEE!"}'
```

### Monitoring
```bash
# View logs
phala logs blend-pools --follow

# Check resource usage
phala stats blend-pools

# Monitor costs
phala billing blend-pools
```

## 🔐 Security Considerations

### Secret Management
- Use Phala's built-in secret management
- Never commit API keys to repository
- Rotate keys regularly
- Use environment-specific configurations

### Network Security
- All traffic is encrypted by default in TEE
- Internal Docker network for service communication
- No direct database access from external networks
- Rate limiting and monitoring enabled

### Data Protection
- All memory is encrypted in TEE
- No persistent storage of sensitive data
- Regular backup of configuration only
- Audit logging for all operations

## 📊 Performance Optimization

### Resource Allocation
```yaml
# In docker-compose.yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Scaling Configuration
```bash
# Auto-scaling based on load
phala autoscale blend-pools \
  --min-replicas 1 \
  --max-replicas 5 \
  --cpu-threshold 70 \
  --memory-threshold 80
```

## 🔄 Updates and Maintenance

### Rolling Updates
```bash
# Update without downtime
phala deploy blend-pools \
  --image your-registry/tuxedo:latest \
  --strategy rolling

# Monitor update progress
phala status blend-pools --watch
```

### Backup and Recovery
```bash
# Export configuration
phala config export blend-pools > backup.yaml

# Restore configuration
phala config import blend-pools < backup.yaml
```

## 🚨 Troubleshooting

### Common Phala Issues

**Deployment fails**
- Check Docker image compatibility
- Verify environment variables
- Review Phala console logs

**Performance issues**
- Monitor resource utilization
- Check network connectivity
- Review TEE resource limits

**AI agent not responding**
- Verify OpenAI API key
- Check backend health status
- Review TEE network policies

### Debug Commands
```bash
# Detailed deployment info
phala describe blend-pools

# Resource usage breakdown
phala resources blend-pools

# Network connectivity test
phala network test blend-pools

# Event logs
phala events blend-pools --since 1h
```

## 📈 Cost Management

### Monitoring Costs
```bash
# Current billing period
phala billing current

# Cost breakdown by service
phala billing breakdown blend-pools

# Set cost alerts
phala billing alert --threshold 10 --currency USD
```

### Optimization Tips
- Use appropriate instance sizes
- Enable auto-scaling
- Monitor and optimize resource usage
- Regular cleanup of unused resources

## 📚 Additional Resources

- [Phala Documentation](https://docs.phala.network)
- [TEE Architecture Guide](https://docs.phala.network/tee)
- [Docker Integration Guide](./DOCKER.md)
- [General Deployment Guide](./DEPLOYMENT.md)
- [Architecture Overview](./ARCHITECTURE.md)

## 🆘 Support

For Phala-specific issues:
- Phala Discord community
- Phala support team
- Stack Overflow with `phala` tag
- GitHub issues in repository

For Tuxedo-specific issues:
- Create GitHub issue in this repository
- Check existing issues and documentation
- Join development Discord/Telegram