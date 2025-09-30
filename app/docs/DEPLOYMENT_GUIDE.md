# Deployment Guide

## Overview

This guide covers deploying the RCM SaaS Application to various cloud platforms and environments.

## Prerequisites

- Python 3.9 or higher
- Google Cloud Platform account
- Firebase project setup
- Domain name (for production)
- SSL certificate (for production)

## Environment Setup

### 1. Development Environment

```bash
# Clone repository
git clone <repository-url>
cd rcm-saas-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Run application
python app/main.py
```

### 2. Production Environment

```bash
# Install production dependencies
pip install gunicorn

# Set production environment variables
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
export JWT_SECRET_KEY=your-production-jwt-secret

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
```

## Google Cloud Platform Deployment

### 1. App Engine Deployment

#### Create app.yaml
```yaml
runtime: python39
env: standard

handlers:
- url: /.*
  script: auto

env_variables:
  FLASK_ENV: production
  SECRET_KEY: your-secret-key
  JWT_SECRET_KEY: your-jwt-secret
  FIREBASE_PROJECT_ID: mv20-a1a09
  FIREBASE_STORAGE_BUCKET: gs://mv20-a1a09.firebasestorage.app
```

#### Deploy
```bash
# Install Google Cloud SDK
# Authenticate
gcloud auth login

# Deploy to App Engine
gcloud app deploy
```

### 2. Cloud Run Deployment

#### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"]
```

#### Deploy
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/rcm-saas-app

# Deploy to Cloud Run
gcloud run deploy rcm-saas-app \
  --image gcr.io/PROJECT_ID/rcm-saas-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 3. Compute Engine Deployment

#### Create VM Instance
```bash
# Create VM instance
gcloud compute instances create rcm-saas-app \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=e2-medium \
  --zone=us-central1-a

# SSH into instance
gcloud compute ssh rcm-saas-app --zone=us-central1-a
```

#### Setup Application
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Clone and setup application
git clone <repository-url>
cd rcm-saas-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/rcm-saas-app.service
```

#### Systemd Service File
```ini
[Unit]
Description=RCM SaaS Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/rcm-saas-app
Environment="PATH=/path/to/rcm-saas-app/venv/bin"
ExecStart=/path/to/rcm-saas-app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## AWS Deployment

### 1. Elastic Beanstalk

#### Create requirements.txt for EB
```
Flask==2.3.3
gunicorn==21.2.0
firebase-admin==6.2.0
# ... other dependencies
```

#### Deploy
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init

# Create environment
eb create production

# Deploy
eb deploy
```

### 2. ECS with Fargate

#### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"]
```

#### Create task definition
```json
{
  "family": "rcm-saas-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "rcm-saas-app",
      "image": "your-account.dkr.ecr.region.amazonaws.com/rcm-saas-app:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ]
    }
  ]
}
```

## Azure Deployment

### 1. App Service

#### Create web.config
```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="D:\home\Python39\python.exe"
                  arguments="D:\home\site\wwwroot\app\main.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="D:\home\LogFiles\python.log"
                  startupTimeLimit="60"
                  startupRetryCount="3">
    </httpPlatform>
  </system.webServer>
</configuration>
```

#### Deploy
```bash
# Install Azure CLI
# Login to Azure
az login

# Create resource group
az group create --name rcm-saas-rg --location eastus

# Create app service plan
az appservice plan create --name rcm-saas-plan --resource-group rcm-saas-rg --sku B1

# Create web app
az webapp create --resource-group rcm-saas-rg --plan rcm-saas-plan --name rcm-saas-app --runtime "PYTHON|3.9"

# Deploy code
az webapp deployment source config --resource-group rcm-saas-rg --name rcm-saas-app --repo-url <repository-url> --branch main --manual-integration
```

## Docker Deployment

### 1. Local Docker

#### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"]
```

#### Build and Run
```bash
# Build image
docker build -t rcm-saas-app .

# Run container
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  rcm-saas-app
```

### 2. Docker Compose

#### Create docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key
      - JWT_SECRET_KEY=your-jwt-secret
      - FIREBASE_PROJECT_ID=mv20-a1a09
    volumes:
      - ./ServiceAccountKey.json:/app/ServiceAccountKey.json:ro
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
```

#### Deploy
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Kubernetes Deployment

### 1. Create Kubernetes Manifests

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rcm-saas-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rcm-saas-app
  template:
    metadata:
      labels:
        app: rcm-saas-app
    spec:
      containers:
      - name: rcm-saas-app
        image: rcm-saas-app:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: rcm-saas-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

#### service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: rcm-saas-app-service
spec:
  selector:
    app: rcm-saas-app
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

#### ingress.yaml
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rcm-saas-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: rcm-saas-app-service
            port:
              number: 80
```

### 2. Deploy to Kubernetes
```bash
# Apply manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Check status
kubectl get pods
kubectl get services
kubectl get ingress
```

## Monitoring and Logging

### 1. Application Monitoring

#### Health Checks
```python
# Add to app/main.py
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }

@app.route('/health/database')
def database_health():
    try:
        # Check database connection
        return {'status': 'healthy', 'database': 'connected'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

### 2. Logging Configuration

#### Production Logging
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug and not app.testing:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('RCM SaaS Application startup')
```

### 3. Monitoring Tools

- **Prometheus + Grafana**: Metrics collection and visualization
- **ELK Stack**: Log aggregation and analysis
- **Sentry**: Error tracking and performance monitoring
- **New Relic**: Application performance monitoring

## Security Considerations

### 1. Environment Variables
- Never commit secrets to version control
- Use environment variables for sensitive data
- Rotate secrets regularly
- Use secret management services

### 2. HTTPS Configuration
- Always use HTTPS in production
- Configure SSL certificates
- Use HSTS headers
- Implement proper CORS policies

### 3. Firewall and Network Security
- Configure firewall rules
- Use VPCs for network isolation
- Implement rate limiting
- Monitor network traffic

### 4. Database Security
- Use connection encryption
- Implement access controls
- Regular security updates
- Backup encryption

## Backup and Recovery

### 1. Database Backups
```bash
# Firestore backup
gcloud firestore export gs://your-backup-bucket/firestore-backup

# Restore from backup
gcloud firestore import gs://your-backup-bucket/firestore-backup
```

### 2. Application Backups
- Code repository backups
- Configuration backups
- SSL certificate backups
- Environment variable backups

### 3. Disaster Recovery
- Multi-region deployment
- Automated failover
- Data replication
- Recovery procedures

## Performance Optimization

### 1. Application Optimization
- Use connection pooling
- Implement caching
- Optimize database queries
- Use CDN for static assets

### 2. Infrastructure Optimization
- Auto-scaling configuration
- Load balancing
- Database optimization
- Monitoring and alerting

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check Firebase credentials
   - Verify network connectivity
   - Check service account permissions

2. **Authentication Issues**
   - Verify JWT secret key
   - Check token expiration
   - Validate user permissions

3. **Performance Issues**
   - Check resource utilization
   - Monitor database queries
   - Review application logs

### Debug Commands

```bash
# Check application logs
docker logs rcm-saas-app

# Check database connectivity
python -c "from app.database.firebase_client import FirebaseClient; print(FirebaseClient().health_check())"

# Test API endpoints
curl -X GET http://localhost:5000/health
```

## Maintenance

### 1. Regular Updates
- Update dependencies
- Apply security patches
- Update Python version
- Update infrastructure

### 2. Monitoring
- Monitor application performance
- Check error rates
- Review security logs
- Monitor resource usage

### 3. Backup Verification
- Test backup restoration
- Verify data integrity
- Check backup completeness
- Document recovery procedures
