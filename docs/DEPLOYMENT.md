# Deployment Guide

This guide covers deploying T&C Clarity to various environments and cloud platforms.

## Prerequisites

### Required Services
- PostgreSQL 14+
- Redis 7+
- Container registry
- Domain name with SSL certificate
- Cloud account (AWS/GCP/Azure)

### Required Tools
```bash
# Docker
curl -fsSL https://get.docker.com | sh

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# kubectl (for Kubernetes)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

## Environment Configuration

### Production Environment Variables

Create a `.env.production` file:

```bash
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=jwt-secret-key
ALLOWED_HOSTS=yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/tcclarity
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://redis.internal:6379/0

# Hugging Face
HUGGINGFACE_API_KEY=your_hf_api_key

# LangChain
LANGCHAIN_API_KEY=your_langchain_key
LANGCHAIN_TRACING_V2=true

# MLflow
MLFLOW_TRACKING_URI=http://mlflow.internal:5000

# Monitoring
PROMETHEUS_ENABLED=true
SENTRY_DSN=https://your-sentry-dsn

# File Storage
MAX_UPLOAD_SIZE=52428800  # 50MB
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET=tc-clarity-documents
```

## Docker Deployment

### Production Dockerfile

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y gcc postgresql-client
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose Production

```yaml
version: '3.8'

services:
  app:
    image: tc-clarity:latest
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - postgres
      - redis
      - chromadb
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: tcclarity
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  chromadb:
    image: chromadb/chroma:latest
    restart: unless-stopped
    volumes:
      - chroma_data:/chroma/chroma

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app

  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro

  grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  chroma_data:
  grafana_data:
```

### Deploy with Docker Compose

```bash
# Pull images
docker-compose -f docker-compose.production.yml pull

# Start services
docker-compose -f docker-compose.production.yml up -d

# Run migrations
docker-compose -f docker-compose.production.yml exec app alembic upgrade head

# Check logs
docker-compose -f docker-compose.production.yml logs -f app
```

## Cloud Deployments

### AWS (ECS)

**1. Create ECR Repository:**
```bash
aws ecr create-repository --repository-name tc-clarity

# Login and push
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag tc-clarity:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/tc-clarity:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/tc-clarity:latest
```

**2. Create RDS PostgreSQL:**
```bash
aws rds create-db-instance \
    --db-instance-identifier tc-clarity-db \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --master-username admin \
    --master-user-password SecurePassword \
    --allocated-storage 100 \
    --multi-az
```

**3. Create ElastiCache Redis:**
```bash
aws elasticache create-cache-cluster \
    --cache-cluster-id tc-clarity-redis \
    --cache-node-type cache.t3.medium \
    --engine redis \
    --num-cache-nodes 1
```

### Google Cloud (Cloud Run)

**1. Build and Deploy:**
```bash
# Build
gcloud builds submit --tag gcr.io/PROJECT_ID/tc-clarity

# Deploy
gcloud run deploy tc-clarity \
    --image gcr.io/PROJECT_ID/tc-clarity \
    --platform managed \
    --region us-central1 \
    --memory 4Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 10
```

**2. Set Up Cloud SQL:**
```bash
gcloud sql instances create tc-clarity-db \
    --database-version=POSTGRES_15 \
    --tier=db-custom-2-7680 \
    --region=us-central1
```

### Azure (Container Instances)

**1. Create Resources:**
```bash
az group create --name tc-clarity-rg --location eastus

# Create ACR
az acr create --resource-group tc-clarity-rg --name tcclarity --sku Standard

# Build and push
az acr build --registry tcclarity --image tc-clarity:latest .
```

**2. Deploy Container:**
```bash
az container create \
    --resource-group tc-clarity-rg \
    --name tc-clarity-app \
    --image tcclarity.azurecr.io/tc-clarity:latest \
    --cpu 2 \
    --memory 4 \
    --dns-name-label tc-clarity \
    --ports 8000
```

## Kubernetes Deployment

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Check status
kubectl get pods -n tc-clarity
kubectl logs -f deployment/tc-clarity-app -n tc-clarity
```

### Helm Deployment

```bash
# Install with Helm
helm install tc-clarity ./charts/tc-clarity \
  --namespace tc-clarity \
  --create-namespace \
  --values values.production.yaml

# Upgrade
helm upgrade tc-clarity ./charts/tc-clarity \
  --namespace tc-clarity

# Rollback
helm rollback tc-clarity 1
```

## Monitoring Setup

### Prometheus & Grafana

Access dashboards:
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

Import dashboards:
- API Performance
- System Resources
- LLM Metrics

## Backup Strategy

### Database Backup

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL | gzip > "backup_$DATE.sql.gz"
aws s3 cp "backup_$DATE.sql.gz" s3://tc-clarity-backups/
```

### Restore Database

```bash
#!/bin/bash
# restore.sh
aws s3 cp s3://tc-clarity-backups/$BACKUP_FILE /tmp/restore.sql.gz
gunzip < /tmp/restore.sql.gz | psql $DATABASE_URL
```

## Security Hardening

### SSL/TLS

```bash
# Let's Encrypt
sudo certbot --nginx -d yourdomain.com
sudo certbot renew --dry-run
```

### Firewall Rules

```bash
# UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check logs
docker logs tc-clarity-app
kubectl logs -f deployment/tc-clarity-app

# Check health
curl http://localhost:8000/health
```

**Database connection:**
```bash
# Test connection
psql $DATABASE_URL

# Check pool
docker exec -it tc-clarity-app python -c "from app.core.database import engine; print(engine.pool.status())"
```

**High memory:**
```bash
# Monitor resources
docker stats tc-clarity-app
kubectl top pods -n tc-clarity
```

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push
        run: |
          docker build -t tc-clarity:latest .
          docker push tc-clarity:latest
      
      - name: Deploy
        run: |
          # Deploy commands
```

## Post-Deployment Checklist

- [ ] All services running and healthy
- [ ] SSL certificates valid
- [ ] Database migrations completed
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] DNS records updated
- [ ] Performance testing completed
- [ ] Security audit passed

---

For deployment support, contact: devops@tc-clarity.com