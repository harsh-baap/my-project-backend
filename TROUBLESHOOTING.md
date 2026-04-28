# 🔧 Troubleshooting Guide

## Issues & Solutions

### 1. Docker Services Won't Start

**Problem:** `docker-compose up -d` fails or services don't start

**Solutions:**

```bash
# Check if Docker is running
docker ps

# View detailed error logs
docker-compose logs

# Rebuild images without cache
docker-compose build --no-cache

# Start with verbose output
docker-compose up

# Remove and restart
docker-compose down -v
docker-compose up -d
```

**Common Causes:**
- Docker daemon not running
- Port already in use
- Insufficient disk space
- Out of memory

---

### 2. Port Already in Use

**Problem:** `Error: listen EADDRINUSE: address already in use :::3000`

**Solutions:**

**On Windows:**
```cmd
# Find process using port
netstat -ano | findstr :3000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

**On Mac/Linux:**
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>

# Or free the port
sudo fuser -k 3000/tcp
```

**Permanent solution:**
Edit `docker-compose.yml` and change port mappings:
```yaml
ports:
  - "3001:3000"  # Use different port
```

---

### 3. Video Upload Fails

**Problem:** Upload returns 400 or 413 error

**Solutions:**

**413 - File Too Large**
```bash
# Check file size
ls -lh Data/garbage.mp4

# Max is 500 MB
# Split large files:
ffmpeg -i large_video.mp4 -c copy -segment_time 600 -f segment output_%03d.mp4
```

**400 - Invalid Format**
```bash
# Check video codec
ffprobe Data/garbage.mp4

# Convert to supported format
ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4
```

**Upload Timeout**
- Edit `nginx.conf`: increase `client_max_body_size`
- Edit `docker-compose.yml`: increase timeout values
- Split video into smaller parts

---

### 4. Detection API Not Responding

**Problem:** `/api/upload` returns connection error

**Solutions:**

```bash
# Check if API is running
curl http://localhost:5000/api/health

# Check logs
docker-compose logs detection-api

# Verify models exist
docker-compose exec detection-api ls DataModel/models/

# Restart service
docker-compose restart detection-api
```

**If models missing:**
```bash
# Download models manually
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Copy to DataModel/models/
# Rename to: garbage.pt, hazard.pt, weapondetect.pt
```

---

### 5. MongoDB Connection Failed

**Problem:** `MongoServerError: connect ECONNREFUSED`

**Solutions:**

```bash
# Check if MongoDB is running
docker-compose ps mongo

# View logs
docker-compose logs mongo

# Restart MongoDB
docker-compose restart mongo

# Check connection string in .env
# Should be: mongodb://admin:admin123@mongo:27017/project
```

**If credentials wrong:**
```bash
# Update .env
MONGO_URI=mongodb://admin:newpassword@mongo:27017/project

# Restart backend
docker-compose restart backend
```

---

### 6. High Memory Usage

**Problem:** System becomes slow during video processing

**Solutions:**

```bash
# Monitor resources
docker stats

# Check how much memory services use
docker stats --no-stream

# Reduce max file size in .env
MAX_FILE_SIZE=268435456  # 256 MB instead of 500 MB

# Process smaller videos or one at a time

# Increase swap memory (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**In docker-compose.yml:**
```yaml
services:
  detection-api:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

---

### 7. Video Processing Hangs/Freezes

**Problem:** Job stuck on "processing" status

**Solutions:**

```bash
# Check detection-api logs
docker-compose logs -f detection-api

# Kill container and restart
docker-compose restart detection-api

# Check for corrupted videos
ffprobe Data/garbage.mp4

# Try with different video
python combined_detection.py --input Data/weapon.mp4 --output outputs/test.mp4
```

---

### 8. Frontend Not Loading

**Problem:** http://localhost blank or 404

**Solutions:**

```bash
# Check if Nginx is running
docker-compose ps frontend

# Check Nginx logs
docker-compose logs nginx

# Verify frontend file exists
ls frontend/index.html

# Restart Nginx
docker-compose restart frontend

# Test with direct port
curl http://localhost:80
```

---

### 9. Authentication Issues

**Problem:** Login/registration not working

**Solutions:**

```bash
# Check if backend is running
curl http://localhost:3000/api/health

# Check backend logs
docker-compose logs backend

# Verify session configuration
# Check .env SESSION_SECRET is set

# Clear browser cookies
# And try again

# Restart backend
docker-compose restart backend
```

---

### 10. CORS Errors

**Problem:** `Access to XMLHttpRequest blocked by CORS policy`

**Solutions:**

**In app.js, update CORS:**
```javascript
app.use(cors({
  origin: ['http://localhost:80', 'http://localhost:3000'],
  credentials: true
}));
```

Or allow all:
```javascript
app.use(cors({
  origin: true,
  credentials: true
}));
```

**Restart backend:**
```bash
docker-compose restart backend
```

---

### 11. Python Dependencies Not Installing

**Problem:** `pip install -r requirements.txt` fails

**Solutions:**

```bash
# Update pip first
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Install one by one to find problematic package
pip install ultralytics
pip install opencv-python
pip install torch
```

**If torch fails (common):**
```bash
# Install CPU-only PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Or with GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

### 12. Node Dependencies Not Installing

**Problem:** `npm install` fails in backend

**Solutions:**

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Or use yarn
yarn install
```

---

### 13. Files Not Persisting

**Problem:** Uploaded files disappear after restart

**Solutions:**

**Ensure volumes in docker-compose.yml:**
```yaml
volumes:
  - ./uploads:/app/uploads
  - ./outputs:/app/outputs
```

**Check if directories exist:**
```bash
ls -la uploads/
ls -la outputs/

# Create if missing
mkdir -p uploads outputs
```

---

### 14. Database Data Lost

**Problem:** User data disappeared after restart

**Solutions:**

**Add MongoDB volume:**
```yaml
mongo:
  volumes:
    - mongo-data:/data/db

volumes:
  mongo-data:
```

**Existing data recovery:**
```bash
# Backup before changes
docker exec safeguard-mongodb mongodump --out /backup

# Restore if needed
docker exec safeguard-mongodb mongorestore /backup
```

---

### 15. Slow Video Processing

**Problem:** Video processing takes too long

**Solutions:**

```bash
# Monitor CPU/GPU usage
docker stats

# Reduce image size during processing
# Edit video_detector.py parameter imgsz to lower value

# Process lower resolution video
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4

# Use GPU if available (CUDA)
# Install: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

### 16. 502 Bad Gateway

**Problem:** Nginx shows "502 Bad Gateway"

**Solutions:**

```bash
# Check backend is running
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Verify backend is listening on port 3000
docker-compose exec backend netstat -tlnp

# Restart everything in order
docker-compose restart mongo
docker-compose restart detection-api  
docker-compose restart backend
docker-compose restart frontend
```

---

## Keeping Logs

### Save All Logs

```bash
# Timestamp output
docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).log

# Follow specific service
docker-compose logs -f backend > backend_logs.log &

# Export for analysis
docker-compose logs > docker_compose.log
```

---

## Performance Optimization

### For Video Processing

```python
# In app.py or video_detector.py
# Use smaller image size
results = model(frame, imgsz=320)  # Instead of 640

# Reduce confidence threshold
results = model(frame, conf=0.5)   # Instead of default

# Use FP16 (half precision)
model = YOLO('model.pt')
model.to('cuda', fp16=True)
```

### For Database

```javascript
// Add indexes in MongoDB
db.jobs.createIndex({ status: 1 });
db.jobs.createIndex({ createdAt: -1 });
db.users.createIndex({ email: 1 }, { unique: true });
```

---

## Getting Help

### Check Logs (First Step Always)

```bash
# All services
docker-compose logs -f

# Last 50 lines
docker-compose logs --tail=50

# Specific time
docker-compose logs --since 2024-01-15T10:00:00
```

### Test Endpoints

```bash
# Health checks
curl http://localhost:5000/api/health
curl http://localhost:3000/api/health
curl http://localhost:80/health

# List jobs
curl http://localhost:5000/api/jobs

# Check models
curl http://localhost:5000/api/models
```

### System Information

```bash
# Docker version
docker --version

# System resources
df -h
free -h

# Network ports
netstat -tlnp | grep -E ':3000|:5000|:80|:27017'
```

---

## Emergency Recovery

```bash
# Full reset (WARNING: Data will be lost!)
docker-compose down -v
docker system prune -a --volumes
docker-compose up -d

# Backup before reset
docker-compose exec mongo mongodump --out /backup
```

---

## Still Having Issues?

1. **Check logs first** - 90% of issues are in logs
2. **Verify configuration** - Check .env and docker-compose.yml
3. **Test components** - Test each service independently
4. **Search online** - Most errors have known solutions
5. **Ask for help** - Provide full logs and error messages

---

**Remember: Most problems are configuration or resource related, not code issues!**
