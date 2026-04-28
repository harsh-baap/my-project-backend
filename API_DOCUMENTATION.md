# 🔌 SafeGuard AI - API Documentation

## Overview

SafeGuard AI provides two main APIs:
- **Detection API** (Python Flask) - Port 5000
- **Backend API** (Node.js Express) - Port 3000

All endpoints return JSON responses.

---

## Detection API (Port 5000)

Python Flask API for video processing and object detection.

### Authentication
No authentication required (internal use).

### Base URL
```
http://localhost:5000
```

---

## Endpoints

### 1. Health Check

**GET** `/api/health`

Check if detection service is running.

**Response:**
```json
{
  "status": "ok",
  "detector_initialized": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:** 200

---

### 2. Get Available Models

**GET** `/api/models`

Get list of available detection models.

**Response:**
```json
{
  "status": "success",
  "models": ["garbage", "hazard", "weapon"],
  "models_path": "DataModel/models",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:** 200

---

### 3. Upload Video

**POST** `/api/upload`

Upload a video file for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `video` (file)

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| video | file | Yes | Video file (MP4, AVI, MOV, MKV, FLV, WMV) |

**Max Size:** 500 MB

**Response:**
```json
{
  "status": "processing",
  "job_id": "20240115101500_example_video",
  "message": "Video uploaded and processing started",
  "input_file": "example_video.mp4"
}
```

**Status Codes:**
- 202: Accepted, processing started
- 400: No file or invalid format
- 413: File too large
- 500: Server error

**Example:**
```bash
curl -X POST \
  -F "video=@/path/to/video.mp4" \
  http://localhost:5000/api/upload
```

---

### 4. Get Job Status

**GET** `/api/job/{job_id}`

Get status and results of a processing job.

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| job_id | string | URL | Job ID from upload response |

**Response (Processing):**
```json
{
  "job_id": "20240115101500_video",
  "status": "processing",
  "uploaded_at": "2024-01-15T10:15:00Z",
  "result": null,
  "error": null
}
```

**Response (Completed):**
```json
{
  "job_id": "20240115101500_video",
  "status": "completed",
  "uploaded_at": "2024-01-15T10:15:00Z",
  "result": {
    "status": "success",
    "input_file": "/app/uploads/20240115_101500_video.mp4",
    "output_file": "/app/outputs/20240115_101500_video_detected.mp4",
    "total_frames": 300,
    "fps": 30,
    "resolution": "1920x1080",
    "detections": {
      "garbage": 15,
      "hazard": 8,
      "weapon": 0,
      "total_frames": 300
    },
    "timestamp": "2024-01-15T10:20:00Z"
  },
  "error": null
}
```

**Status Codes:** 200, 404

**Example:**
```bash
curl http://localhost:5000/api/job/20240115101500_video
```

---

### 5. Download Processed Video

**GET** `/api/download/{job_id}`

Download the processed video with detection annotations.

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| job_id | string | URL | Job ID |

**Response:** Video file (mp4)

**Status Codes:** 200, 400, 404

**Example:**
```bash
curl -O http://localhost:5000/api/download/20240115101500_video \
  -H "Content-Disposition: attachment"
```

---

### 6. List All Jobs

**GET** `/api/jobs`

Get list of all processing jobs.

**Response:**
```json
{
  "total_jobs": 3,
  "jobs": {
    "20240115101500_video1": {
      "status": "completed",
      "uploaded_at": "2024-01-15T10:15:00Z",
      "error": null
    },
    "20240115101600_video2": {
      "status": "processing",
      "uploaded_at": "2024-01-15T10:16:00Z",
      "error": null
    },
    "20240115101700_video3": {
      "status": "failed",
      "uploaded_at": "2024-01-15T10:17:00Z",
      "error": "Invalid video format"
    }
  }
}
```

**Status Codes:** 200

---

### 7. Clean Up Job

**DELETE** `/api/cleanup/{job_id}`

Delete job files and remove from tracking.

**Parameters:**
| Name | Type | Location | Description |
|------|------|----------|-------------|
| job_id | string | URL | Job ID |

**Response:**
```json
{
  "status": "success",
  "message": "Job cleaned up"
}
```

**Status Codes:** 200, 404

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/cleanup/20240115101500_video
```

---

## Backend API (Port 3000)

Node.js Express API for user management and authentication.

### Base URL
```
http://localhost:3000
```

---

## Authentication Routes

### 1. Register User

**POST** `/register`

Register a new user account.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response (Success):**
- Redirect to `/dashboard`
- Sets session cookie

**Response (Error):**
- Redirect to `/register` with error message

**Example:**
```bash
curl -X POST http://localhost:3000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password_123"
  }'
```

---

### 2. Login User

**POST** `/login`

Authenticate user credentials.

**Request:**
```json
{
  "username": "john_doe",
  "password": "secure_password_123"
}
```

**Response (Success):**
- Redirect to `/dashboard`
- Sets authentication session

**Response (Error):**
- Redirect to `/login` with error message

---

### 3. Logout User

**GET** `/logout`

End user session.

**Response:**
- Redirect to `/login`
- Clears session

---

### 4. Get Dashboard

**GET** `/dashboard`

Get user dashboard (requires authentication).

**Authentication:** Required (session cookie)

**Response:** HTML dashboard page

**Status Codes:** 200 (authenticated), 302 (redirect to login)

---

## Detection Routes (via Backend)

### 1. Health Check

**GET** `/api/health`

Check detection service status through backend.

**Response:**
```json
{
  "status": "ok",
  "detector_initialized": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 2. Get Models

**GET** `/api/models`

Get available detection models.

**Response:**
```json
{
  "status": "success",
  "models": ["garbage", "hazard", "weapon"],
  "models_path": "DataModel/models",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 3. Upload Video

**POST** `/api/upload`

Upload video for processing (requires authentication).

**Authentication:** Required

**Request:**
- Content-Type: `multipart/form-data`
- Body: `video` file

**Response:**
```json
{
  "status": "processing",
  "job_id": "20240115101500_example",
  "message": "Video uploaded and processing started",
  "user": "john_doe"
}
```

**Status Codes:** 202, 400, 413, 500

---

### 4. Get Job Status

**GET** `/api/job/{job_id}`

Get processing job status (requires authentication).

**Authentication:** Required

**Response:** Same as Detection API

---

### 5. List Jobs

**GET** `/api/jobs`

List all processing jobs (requires authentication).

**Authentication:** Required

**Response:** Same as Detection API

---

### 6. Download Video

**GET** `/api/download/{job_id}`

Download processed video (requires authentication).

**Authentication:** Required

**Response:** Video file

---

### 7. Clean Up Job

**DELETE** `/api/cleanup/{job_id}`

Delete job files (requires authentication).

**Authentication:** Required

**Request:** None

**Response:**
```json
{
  "status": "success",
  "message": "Job cleaned up"
}
```

---

## Error Responses

### Common Error Codes

**400 - Bad Request**
```json
{
  "error": "No video file provided"
}
```

**401 - Unauthorized**
```json
{
  "error": "Authentication required"
}
```

**404 - Not Found**
```json
{
  "error": "Job not found"
}
```

**413 - Payload Too Large**
```json
{
  "error": "File size exceeds 500 MB limit"
}
```

**500 - Internal Server Error**
```json
{
  "error": "Internal server error",
  "details": "Error message details"
}
```

**503 - Service Unavailable**
```json
{
  "status": "error",
  "message": "Detection service unavailable"
}
```

---

## Rate Limiting

Currently no rate limiting implemented. For production, add:

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', limiter);
```

---

## Best Practices

### 1. Error Handling
```javascript
try {
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error.error);
  }
} catch (error) {
  console.error('Network error:', error);
}
```

### 2. Polling Jobs
```javascript
async function waitForCompletion(jobId) {
  let status = 'processing';
  
  while (status === 'processing') {
    const response = await fetch(`/api/job/${jobId}`);
    const job = await response.json();
    status = job.status;
    
    if (status === 'completed') {
      return job.result;
    }
    
    // Wait 5 seconds before next poll
    await new Promise(r => setTimeout(r, 5000));
  }
}
```

### 3. File Upload with Progress
```javascript
function uploadWithProgress(file, onProgress) {
  const xhr = new XMLHttpRequest();
  const formData = new FormData();
  formData.append('video', file);

  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const progress = (e.loaded / e.total) * 100;
      onProgress(progress);
    }
  });

  xhr.open('POST', '/api/upload');
  xhr.send(formData);
}
```

---

## Rate Limit Response Example

```json
{
  "error": "Too many requests, please try again later"
}
```

HTTP Status: 429

---

## Webhook Events (Future)

Planned webhook support for job completion notifications:

```javascript
// Would trigger on job completion
POST /webhooks/job-completed
{
  "event": "job.completed",
  "job_id": "20240115101500_video",
  "status": "completed",
  "detections": {
    "garbage": 15,
    "hazard": 8,
    "weapon": 0
  },
  "timestamp": "2024-01-15T10:20:00Z"
}
```

---

## SDK / Client Libraries (Planned)

Planned implementations:
- [ ] JavaScript/TypeScript SDK
- [ ] Python SDK
- [ ] CLI Tool

---

## Changelog

### v1.0.0 (Current)
- ✅ Basic video upload and processing
- ✅ Multi-model simultaneous detection
- ✅ User authentication
- ✅ Job management
- ✅ Video download

### v1.1.0 (Planned)
- [ ] Batch processing API
- [ ] Webhook notifications
- [ ] Advanced filtering
- [ ] API keys for programmatic access
- [ ] Rate limiting

### v2.0.0 (Planned)
- [ ] Real-time streaming
- [ ] Custom model uploads
- [ ] Advanced analytics
- [ ] Mobile apps

---

**For more information, see README.md and DEPLOYMENT.md**
