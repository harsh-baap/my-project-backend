# 🚀 SafeGuard AI - Quick Reference Card

## 5-Minute Setup

### Windows
```cmd
start.bat
```

### Mac/Linux
```bash
chmod +x start.sh
./start.sh
```

**Access Points:**
- Frontend: http://localhost:80
- Dashboard: http://localhost/dashboard
- API: http://localhost:3000
- Detection API: http://localhost:5000

---

## Common Commands

### View Logs
```bash
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

### Restart Specific Service
```bash
docker-compose restart backend
```

### Process Video Locally
```bash
python combined_detection.py --input Data/garbage.mp4
```

### Batch Process Videos
```bash
python batch_processor.py --input-dir Data/
```

---

## Supported Video Formats
✅ MP4, AVI, MOV, MKV, FLV, WMV  
⚠️ Max: 500 MB

## Detection Models
- 🔫 Weapon Detection
- 🗑️ Garbage Detection  
- 🔥 Hazard Detection

*(All run simultaneously)*

---

## Troubleshooting (Quick)

| Issue | Solution |
|-------|----------|
| Port in use | Kill process: `lsof -i :3000` then `kill -9 PID` |
| Video upload fails | Check file size < 500 MB |
| API not responding | `docker-compose restart detection-api` |
| Forgotten password | Check .env for DB credentials |
| High memory | Reduce MAX_FILE_SIZE in .env |

**Full troubleshooting:** See `TROUBLESHOOTING.md`

---

## Key Documents

| Document | Purpose |
|----------|---------|
| README.md | Main guide & features |
| DEPLOYMENT.md | Installation & deployment |
| API_DOCUMENTATION.md | API endpoints reference |
| TROUBLESHOOTING.md | Problem solving |
| CHANGES.md | What's new |

---

## API Endpoints (Main)

```
POST   /api/upload          Upload video
GET    /api/job/{id}        Get status
GET    /api/download/{id}   Download results
GET    /api/jobs            List all jobs
DELETE /api/cleanup/{id}    Delete job
GET    /api/health          Health check
```

---

## Environment Setup

```bash
# Create config
cp .env.example .env

# Edit if needed (optional - defaults work)
nano .env

# Start
docker-compose up -d
```

---

## File Structure

```
📁 Project Root
├── 🐍 app.py                (Flask API)
├── 📹 video_detector.py     (Detection module)
├── 🌐 frontend/             (Web interface)
├── 🔙 backend/              (Node.js server)
├── 📦 DataModel/            (AI models)
├── 📁 uploads/              (Input videos)
├── 📁 outputs/              (Results)
└── 📄 docker-compose.yml    (Orchestration)
```

---

## Development Commands

```bash
# Python virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Run Flask API directly
python app.py

# Run Node backend
cd backend && npm install && npm start

# Test commands
curl http://localhost:5000/api/health
curl http://localhost:3000/api/health
```

---

## Performance Tips

- ✅ Process videos < 100 MB for faster results
- ✅ Batch process multiple videos together
- ✅ Use imgsz=320 for faster detection
- ✅ Enable GPU if available

---

## Security Checklist

- [ ] Change SESSION_SECRET in .env
- [ ] Change MongoDB password
- [ ] Use HTTPS in production
- [ ] Enable firewall rules
- [ ] Regular backups

---

## Getting Help

1. **Check logs:** `docker-compose logs -f`
2. **Health check:** `curl http://localhost:5000/api/health`
3. **See TROUBLESHOOTING.md** for common issues
4. **Check docker ps:** `docker-compose ps`

---

## Database (MongoDB)

```bash
# Connect to MongoDB
docker exec -it safeguard-mongodb mongosh

# Show databases
show dbs

# Use project database
use project

# Show collections
show collections

# Find users
db.users.find()
```

---

## Video Processing Status Codes

| Status | Meaning |
|--------|---------|
| 🔵 processing | Currently processing |
| 🟢 completed | Done - ready to download |
| 🔴 failed | Error occurred - check logs |

---

## Upload Limits

- Max file size: **500 MB**
- Max framesize: Adjusted automatically
- Resolution: Supports any
- FPS: Supports any

---

## Supported CLI Modes

```bash
# Single file
python combined_detection.py --input file.mp4 --output result.mp4

# Batch directory
python batch_processor.py --input-dir Data/

# Webcam
python combined_detection.py --webcam

# Models location
python combined_detection.py --models-path custom/path/
```

---

## Docker Useful Commands

```bash
# Start all
docker-compose up -d

# Stop all
docker-compose down

# Remove everything
docker-compose down -v

# Show running
docker-compose ps

# View resource usage
docker stats

# Clean up unused
docker system prune -a

# View events
docker-compose events
```

---

## Network Ports

| Port | Service | Access |
|------|---------|--------|
| 80 | Nginx Frontend | http://localhost |
| 3000 | Node.js Backend | http://localhost:3000 |
| 5000 | Flask API | http://localhost:5000 |
| 27017 | MongoDB | localhost (internal) |

---

## Default Credentials

| Service | User | Password |
|---------|------|----------|
| MongoDB | admin | admin123 |
| App | N/A | Register first |

*Change these in production!*

---

## Success Indicators

✅ Services running: `docker-compose ps` shows all UP  
✅ API responding: `curl http://localhost:5000/api/health` returns 200  
✅ Videos uploading: Can upload file in UI  
✅ Processing working: Job status changes from "processing" to "completed"  
✅ Download works: Can download annotated video  

---

## Estimated Processing Time

- **30 seconds video:** 1-2 minutes
- **1 minute video:** 2-3 minutes
- **5 minute video:** 10-15 minutes

*(Depends on system specs - faster with GPU)*

---

## Need Help?

📖 **Documentation**
- Full guide: See README.md
- Deployment help: See DEPLOYMENT.md
- API details: See API_DOCUMENTATION.md
- Issues: See TROUBLESHOOTING.md

🔍 **Debug**
```bash
docker-compose logs -f --tail=50
docker-compose logs backend
docker-compose logs detection-api
```

🏥 **Health Check**
```bash
curl http://localhost:5000/api/health
curl http://localhost:3000/api/health
```

---

**Status: ✅ Ready to Deploy**

*Print this card and keep it handy!*
