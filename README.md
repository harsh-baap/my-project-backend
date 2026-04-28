# 🚀 SafeGuard AI - Multi-Threat Detection System

An advanced real-time AI system for simultaneous detection of weapons, garbage dumping, and hazards using YOLOv8 models deployed on Docker.

## 📋 Project Features

- **🔫 Weapon Detection** - Real-time detection of dangerous objects
- **🗑️ Garbage Monitoring** - Identifies illegal dumping and waste
- **🔥 Hazard Alerts** - Recognizes fire, smoke, and dangerous situations
- **📹 Video Processing** - Upload videos for batch detection with results visualization
- **⚡ Simultaneous Detection** - Multiple AI models run in parallel for comprehensive threat analysis
- **📊 Unified Dashboard** - Centralized monitoring and management system
- **🔐 User Authentication** - Secure login and session management
- **🌐 REST API** - Full API for integration with other systems

## 🏗️ System Architecture

```
Frontend (HTML/JS) 
    ↓
Backend (Node.js/Express) ← MongoDB
    ↓
Detection API (Python/Flask)
    ↓
YOLOv8 Models (Weapon, Garbage, Hazard)
```

## 📦 Tech Stack

### Frontend
- HTML5, CSS3, JavaScript
- Modern UI with glassmorphism design

### Backend
- Node.js + Express.js
- MongoDB for user data
- Passport.js authentication

### Detection Service
- Python 3.10
- Flask API
- YOLOv8 (Ultralytics)
- OpenCV for video processing

### Deployment
- Docker & Docker Compose
- Nginx reverse proxy
- Multi-container orchestration

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (latest version)
- 4GB RAM minimum
- 10GB storage (for models and processing)

### Installation

1. **Clone or extract the project**
```bash
cd path/to/your/project
```

2. **Configure environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or edit with your editor
```

3. **Start all services**

**On Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**On Windows:**
```batch
start.bat
```

Or manually:
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:80
- Backend API: http://localhost:3000
- Detection API: http://localhost:5000

## 📖 Usage Guide

### Video Processing Workflow

1. **Upload Video**
   - Go to http://localhost:80
   - Use the video upload section (drag & drop or click)
   - Supported formats: MP4, AVI, MOV, MKV, FLV, WMV
   - Max file size: 500 MB

2. **Processing**
   - System processes video frame-by-frame
   - All three models run simultaneously for each frame
   - Detection annotations are added to output video
   - Processing time depends on video length and system specs

3. **View Results**
   - Track processing status in real-time
   - See detection statistics once complete:
     - Number of weapons detected
     - Number of garbage items detected
     - Number of hazards detected
     - Total frames processed
     - Resolution and FPS

4. **Download Results**
   - Download annotated video with all detections highlighted
   - Clean up files after download to free space

### API Endpoints

#### Detection Service (Port 5000)
```
GET  /api/health          - Health check
GET  /api/models          - List available models
POST /api/upload          - Upload video for processing
GET  /api/job/<id>        - Get job status
GET  /api/download/<id>   - Download processed video
DELETE /api/cleanup/<id>  - Clean up job files
GET  /api/jobs            - List all jobs
```

#### Backend Service (Port 3000)
```
POST /register            - User registration
POST /login               - User login
GET  /logout              - User logout
GET  /dashboard           - User dashboard (protected)
GET  /api/health          - Backend health check
GET  /api/models          - Forward to detection service
POST /api/upload          - Forward video upload
GET  /api/job/<id>        - Forward job status
GET  /api/download/<id>   - Forward video download
DELETE /api/cleanup/<id>  - Forward cleanup
GET  /api/jobs            - Forward job list
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Flask Detection API
FLASK_PORT=5000
FLASK_DEBUG=False
FLASK_ENV=production

# MongoDB
MONGO_URI=mongodb://admin:admin123@mongo:27017/project
SESSION_SECRET=your_secure_secret_key_here

# File Upload
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
MAX_FILE_SIZE=524288000  # 500 MB in bytes

# Models
MODELS_PATH=DataModel/models

# API Settings
PYTHON_API_URL=http://localhost:5000
```

## 📁 Project Structure

```
project/
├── frontend/
│   └── index.html              # Main UI
├── backend/
│   ├── app.js                  # Express app
│   ├── package.json            # Node dependencies
│   ├── bin/
│   │   └── www                 # Server entry point
│   ├── models/
│   │   └── User.js             # MongoDB user model
│   ├── routes/
│   │   ├── index.js            # Auth routes
│   │   └── api.js              # API routes
│   ├── views/                  # EJS templates
│   └── public/                 # Static files
├── DataModel/
│   └── models/
│       ├── weapon.pt           # Weapon detection model
│       ├── garbage.pt          # Garbage detection model
│       └── hazard.pt           # Hazard detection model
├── video_detector.py           # Detection module
├── app.py                      # Flask detection API
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Python container
├── Dockerfile.backend          # Node.js container
├── docker-compose.yml          # Container orchestration
├── nginx.conf                  # Web server config
├── .env                        # Environment variables
└── README.md                   # This file
```

## 🐳 Docker Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f detection-api
docker-compose logs -f mongo
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific
docker-compose restart backend
docker-compose restart detection-api
```

### Stop Services
```bash
# Stop running
docker-compose stop

# Stop and remove
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

### Clean Up
```bash
# Remove unused images
docker image prune

# Remove unused containers
docker container prune

# Remove all from project
docker-compose down -v
docker rmi $(docker images -q)
```

## 🔍 Monitoring & Troubleshooting

### Check Service Health
```bash
# Check detection API
curl http://localhost:5000/api/health

# Check backend
curl http://localhost:3000/api/health

# Check frontend
curl http://localhost:80/health
```

### Common Issues

**1. Video upload fails**
- Check file size (max 500 MB)
- Verify file format is supported
- Check disk space in `uploads/` directory
- View logs: `docker-compose logs detection-api`

**2. Models not loading**
- Verify models exist in `DataModel/models/`
- Check file permissions: `chmod 644 DataModel/models/*.pt`
- View logs: `docker-compose logs detection-api`

**3. MongoDB connection fails**
- Verify MongoDB is running: `docker-compose ps`
- Check credentials in .env
- View logs: `docker-compose logs mongo`

**4. Frontend not loading**
- Check Nginx: `docker-compose logs frontend`
- Verify port 80 is not in use: `netstat -an | grep 80`
- Clear browser cache

**5. High memory usage**
- Reduce max file size in .env
- Process multiple small videos instead of one large video
- Check available disk space

## 🔐 Security Notes

- Change `SESSION_SECRET` in .env to a random value
- Change MongoDB credentials
- Use HTTPS in production (configure reverse proxy)
- Implement rate limiting for API
- Keep Docker images updated
- Regular backup of MongoDB data

## 🚀 Deployment

### CloudwaysLocal Deployment
```bash
docker-compose -f docker-compose.yml up -d
```

### Cloud Deployment (AWS/Azure/GCP)
1. Build and push images to container registry:
```bash
docker build -t your-registry/safeguard-detection:latest .
docker build -t your-registry/safeguard-backend:latest -f Dockerfile.backend .
docker push your-registry/safeguard-detection:latest
docker push your-registry/safeguard-backend:latest
```

2. Update docker-compose.yml with registry URLs
3. Deploy using container orchestration (Kubernetes, Docker Swarm, etc.)

### Production Checklist
- [ ] Set FLASK_DEBUG=False
- [ ] Set FLASK_ENV=production
- [ ] Change all secret keys
- [ ] Configure MongoDB backup
- [ ] Set up monitoring and logging
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set resource limits in docker-compose.yml
- [ ] Test with large video files
- [ ] Implement rate limiting

## 📊 Performance Tips

1. **Video Processing**
   - Larger models = slower but more accurate
   - Reduce resolution for faster processing
   - Process multiple videos in parallel (separate uploads)

2. **System Resources**
   - Minimum: 4GB RAM, 4 CPU cores
   - Recommended: 8GB RAM, 8 CPU cores
   - SSD storage for faster I/O

3. **Database**
   - Regular MongoDB maintenance
   - Index optimization
   - Periodic backups

## 📝 Model Information

- **Weapon Detection**: YOLOv8n (nano) - Optimized for speed
- **Garbage Detection**: YOLOv8n - Real-time processing
- **Hazard Detection**: YOLOv8n - Fire/smoke/risk detection

Each model runs independently and in parallel, allowing comprehensive threat analysis in a single pass.

## 🤝 Contributing

To improve this project:
1. Test thoroughly with various video inputs
2. Report issues with detailed logs
3. Submit improvements via pull requests
4. Update documentation for any changes

## 📄 License

[Your License Here]

## 📞 Support

For issues and questions:
- Check logs: `docker-compose logs`
- Review README documentation
- Check API endpoints health

## 🎯 Future Enhancements

- [ ] Real-time live stream processing
- [ ] Custom model training
- [ ] Advanced analytics dashboard
- [ ] Alert notifications (email/SMS)
- [ ] Multi-region deployment
- [ ] GPU acceleration support
- [ ] Redis caching for performance
- [ ] Advanced threat analysis with ML

---

**SafeGuard AI - Protecting Through Technology** ⚡
#   m y - p r o j e c t - b a c k e n d  
 