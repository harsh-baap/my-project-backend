# 🚀 SafeGuard AI - Quick Start Guide

## Setup Instructions

### 1️⃣ Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Install Node.js Dependencies
```bash
cd backend
npm install
cd ..
```

### 3️⃣ Ensure MongoDB is Running
MongoDB must be running on `mongodb://localhost:27017`

For Windows:
```bash
# If installed via MongoDB installer
net start MongoDB

# Or if using WSL/local instance
mongod
```

### 4️⃣ Start Flask Detection API (Terminal 1)
```bash
python app.py
```
✅ Should show: "Running on http://0.0.0.0:5000"

### 5️⃣ Start Node.js Backend (Terminal 2)
```bash
cd backend
npm start
```
✅ Should show: "Server running on port 3000"

### 6️⃣ Open in Browser
```
http://localhost:3000
```

---

## ✅ One-command Local Start (Windows, no Docker)

If you do not have Docker installed, you can run the finalized website locally with one command:

```bat
start-local.bat
```

This starts:
- Detection API: `http://127.0.0.1:5000`
- Website + Backend: `http://127.0.0.1:3000`

Notes:
- Requires MongoDB running locally on port 27017.
- Close the two opened terminal windows to stop the services.

---

## 📋 System Architecture

```
BROWSER (Frontend SPA)
    ↓ http://localhost:3000
NODE.JS BACKEND (Express)
    ↓ http://localhost:5000
PYTHON FLASK API (Detection)
    ↓
YOLOv8 MODELS (Trained)
    ├── weapons
    ├── garbage
    └── hazards
```

---

## 🎯 How to Use

1. **Register/Login** - Create account or login
2. **Upload Video** - Drag & drop or click to select
3. **Wait for Processing** - Real-time status updates
4. **View Results** - See detection statistics
5. **Download** - Get annotated video with detections

---

## 🔧 Environment Variables

All configured in `.env`:
- `MONGO_URI` - MongoDB connection
- `FLASK_PORT` - Flask server port (5000)
- `API_HOST` - API host (0.0.0.0)
- `MODELS_PATH` - Path to trained models

---

## ✅ Models Included

- **weapondetect.pt** - Weapon detection
- **garbage.pt** - Garbage/waste detection
- **hazard.pt** - Fire/smoke/hazard detection

---

## 🐛 Troubleshooting

**"Cannot connect to port 5000"**
- Ensure Flask is running in Terminal 1

**"Cannot connect to port 3000"**
- Ensure Node.js backend is running in Terminal 2

**"MongoDB connection error"**
- Start MongoDB service or local instance

**"Models not found"**
- Check `DataModel/models/` directory contains `.pt` files

---

## 📚 API Endpoints

- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `POST /api/upload` - Upload video for detection
- `GET /api/jobs` - List all jobs
- `GET /api/job/:jobId` - Get specific job status
- `GET /api/download/:jobId` - Download results

---

**Ready to go! 🎉**
