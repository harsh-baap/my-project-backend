# 🚀 SafeGuard AI - Deployment Guide

## Quick Start (5 minutes)

### Option 1: Docker Compose (Recommended)

**Requirements:**
- Docker Desktop installed
- 8GB RAM minimum

**Steps:**

```bash
# 1. Navigate to project directory
cd /path/to/project

# 2. Create environment file
cp .env.example .env

# 3. Edit .env if needed (optional - defaults work)
nano .env

# 4. Start all services
docker-compose up -d

# 5. Verify services
docker-compose ps

# 6. Access the application
# Frontend: http://localhost:80
# Dashboard: http://localhost/dashboard  
# API: http://localhost:3000
```

**View logs:**
```bash
docker-compose logs -f              # All services
docker-compose logs -f backend      # Backend only
docker-compose logs -f detection-api # Detection API only
docker-compose logs -f mongo        # MongoDB only
```

**Stop services:**
```bash
docker-compose down          # Stop
docker-compose down -v       # Stop and remove volumes
```

---

### Option 2: Local Development (Python + Node.js)

**Requirements:**
- Python 3.10+
- Node.js 18+
- MongoDB running locally

**Setup Python:**

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Flask API
python app.py
# Runs on http://localhost:5000
```

**Setup Node.js:**

```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies
npm install

# 3. Start backend
npm start
# Runs on http://localhost:3000
```

**Frontend:**
- Simply open `frontend/index.html` in a browser
- Or use a simple HTTP server: `python -m http.server 8000`

---

## Cloud Deployment

### AWS Deployment

#### Using CloudFormation

```yaml
# 1. Create ECR repositories for your images
aws ecr create-repository --repository-name safeguard-detection
aws ecr create-repository --repository-name safeguard-backend

# 2. Build and push images
docker build -t safeguard-detection:latest .
docker tag safeguard-detection:latest <account>.dkr.ecr.<region>.amazonaws.com/safeguard-detection:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/safeguard-detection:latest

docker build -t safeguard-backend:latest -f Dockerfile.backend .
docker tag safeguard-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/safeguard-backend:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/safeguard-backend:latest

# 3. Create ECS cluster and deploy
# Use CloudFormation template or ECS console
```

#### Using ECS Fargate

1. Create ECS cluster
2. Create task definitions for each service
3. Create services for detection-api, backend, and frontend
4. Configure RDS for MongoDB alternatives
5. Set up Application Load Balancer (ALB)
6. Configure auto-scaling

### Azure Deployment

#### Using Azure Container Instances

```bash
# 1. Build and push to Azure Container Registry
az acr build --registry <registry-name> --image safeguard-detection:latest .
az acr build --registry <registry-name> --image safeguard-backend:latest -f Dockerfile.backend .

# 2. Deploy using Docker Compose on Azure
az container create \
  --resource-group <group> \
  --name safeguard-ai \
  --image <registry>.azurecr.io/safeguard-deployment:latest \
  --environment-variables \
    MONGO_URI="$(cat .env | grep MONGO_URI)" \
  --ports 80 3000 5000
```

#### Using Azure App Service + Container

```bash
# 1. Create App Service
az appservice plan create \
  --name safeguard-plan \
  --resource-group <group> \
  --sku B2 --is-linux

# 2. Create web app
az webapp create \
  --resource-group <group> \
  --plan safeguard-plan \
  --name safeguard-ai

# 3. Configure for containers
az webapp config container set \
  --name safeguard-ai \
  --resource-group <group> \
  --docker-custom-image-name <registry>.azurecr.io/safeguard-backend:latest
```

### Google Cloud Deployment

#### Using Cloud Run

```bash
# 1. Build and push
gcloud builds submit --tag gcr.io/<project>/safeguard-detection
gcloud builds submit --tag gcr.io/<project>/safeguard-backend -f Dockerfile.backend

# 2. Deploy detection API
gcloud run deploy safeguard-detection \
  --image gcr.io/<project>/safeguard-detection \
  --platform managed \
  --region us-central1 \
  --memory 4Gi

# 3. Deploy backend
gcloud run deploy safeguard-backend \
  --image gcr.io/<project>/safeguard-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars PYTHON_API_URL=https://safeguard-detection-xxx.run.app
```

#### Using GKE (Kubernetes)

```bash
# 1. Create cluster
gcloud container clusters create safeguard-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2

# 2. Deploy using kubectl
kubectl apply -f kubernetes-manifest.yaml
```

---

## Production Checklist

- [ ] **Environment Variables**
  - [ ] Change `SESSION_SECRET` to random value
  - [ ] Update MongoDB credentials
  - [ ] Set `FLASK_DEBUG=False`
  - [ ] Set `FLASK_ENV=production`
  - [ ] Configure `PYTHON_API_URL` for backend

- [ ] **Security**
  - [ ] Enable HTTPS/SSL (certificate)
  - [ ] Configure firewall rules
  - [ ] Set up API rate limiting
  - [ ] Enable MongoDB authentication
  - [ ] Use strong passwords

- [ ] **Monitoring**
  - [ ] Set up application logging
  - [ ] Configure error tracking (Sentry)
  - [ ] Set up health checks
  - [ ] Monitor resource usage

- [ ] **Backup**
  - [ ] Configure MongoDB backup
  - [ ] Backup user data regularly
  - [ ] Test restore procedures

- [ ] **Performance**
  - [ ] Enable gzip compression
  - [ ] Configure CDN for static files
  - [ ] Optimize database queries
  - [ ] Set resource limits

- [ ] **Scaling**
  - [ ] Configure auto-scaling policies
  - [ ] Load balancer setup
  - [ ] Database replication

---

## Environment Variables Reference

```env
# Flask Detection API
FLASK_PORT=5000
FLASK_DEBUG=False
FLASK_ENV=production

# Backend
NODE_ENV=production
BACKEND_PORT=3000

# Database
MONGO_URI=mongodb://user:pass@host:27017/project
MONGO_USER=admin
MONGO_PASSWORD=your_secure_password

# Session
SESSION_SECRET=your_very_secure_random_secret_key_here_change_this

# API
PYTHON_API_URL=http://detection-api:5000
BACKEND_URL=http://backend:3000

# Files
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
MAX_FILE_SIZE=524288000  # 500MB

# CORS
CORS_ORIGIN=http://localhost:80

# Models
MODELS_PATH=DataModel/models
```

---

## Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Find process using port
lsof -i :3000       # Mac/Linux
netstat -ano | findstr :3000  # Windows

# Kill process
kill -9 <PID>      # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

**2. Docker permission denied**
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

**3. MongoDB connection fails**
```bash
# Verify MongoDB is running
docker-compose logs mongo

# Check connection string in .env
# Format: mongodb://[username:password@]host[:port]/database
```

**4. High memory usage**
- Reduce MAX_FILE_SIZE
- Increase Docker memory limit
- Process videos smaller in size
- Restart services

**5. Upload timeout**
- Increase proxy timeout in nginx.conf
- Check disk space
- Reduce file size

---

## Performance Tuning

### For High Traffic

```yaml
# docker-compose.yml
services:
  detection-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
  
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### Database Optimization

```javascript
// Add indexes to MongoDB
db.users.createIndex({ email: 1 }, { unique: true });
db.jobs.createIndex({ status: 1 });
db.jobs.createIndex({ createdAt: -1 });
```

---

## Monitoring Commands

```bash
# Docker stats
docker stats

# View specific container
docker stats safeguard-backend

# Monitor logs in real-time
docker-compose logs -f --tail=50

# Check service health
curl http://localhost:3000/api/health
curl http://localhost:5000/api/health

# Database stats
docker exec safeguard-mongodb mongosh -e "db.stats()"
```

---

## Backup & Recovery

### MongoDB Backup

```bash
# Backup
docker exec safeguard-mongodb mongodump --out /backup

# Restore
docker exec safeguard-mongodb mongorestore /backup

# Export collection
docker exec safeguard-mongodb mongoexport \
  --collection users \
  --out users.json

# Import collection
docker exec safeguard-mongodb mongoimport \
  --collection users \
  --file users.json
```

### File Backup

```bash
# Backup uploads and outputs
tar -czf backup_$(date +%Y%m%d).tar.gz uploads/ outputs/

# Restore
tar -xzf backup_20240101.tar.gz
```

---

## Update & Maintenance

### Update Images

```bash
# Pull latest images
docker-compose pull

# Rebuild
docker-compose build --no-cache

# Restart
docker-compose up -d
```

### Clean Up

```bash
# Remove stopped containers
docker container prune

# Remove dangling images
docker image prune

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

---

## Support & Logs

### Export Logs

```bash
# Export all logs
docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).log

# Export specific service
docker-compose logs backend > backend_logs.log
```

### Debug Mode

Enable debug logging in .env:
```env
FLASK_DEBUG=True
NODE_DEBUG=express,mongodb
```

---

**Need Help?** Check the README.md for more information or review service logs for error details.
