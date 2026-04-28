"""
Flask API Server for Video Detection
Handles video uploads and simultaneous multi-model detection
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import threading
from datetime import datetime
from video_detector import VideoDetector
import traceback

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
MODELS_PATH = "DataModel/models"

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize detector
try:
    detector = VideoDetector(models_path=MODELS_PATH)
except Exception as e:
    print(f"Error initializing detector: {e}")
    detector = None

# Track processing jobs
processing_jobs = {}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video_background(job_id, input_path, output_path):
    """Process video in background thread"""
    try:
        if detector is None:
            raise Exception("Detector not initialized")

        # Live preview: write latest annotated frame while processing
        preview_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{job_id}_preview.jpg")

        def _progress_callback(frame_idx, total_frames, annotated_frame):
            try:
                # Update in-memory progress
                processing_jobs[job_id]['progress'] = {
                    "frame": int(frame_idx),
                    "total_frames": int(total_frames) if total_frames else None,
                    "percent": float((frame_idx / total_frames) * 100) if total_frames else None
                }

                # Write preview image occasionally
                if frame_idx % 15 == 0:
                    import cv2
                    cv2.imwrite(preview_path, annotated_frame)
                    processing_jobs[job_id]['preview_file'] = preview_path
            except Exception:
                pass

        result = detector.process_video_file(
            input_path,
            output_path,
            imgsz={"imgsz": 320, "progress_callback": _progress_callback},
        )
        processing_jobs[job_id]['status'] = 'completed'
        processing_jobs[job_id]['result'] = result
        
    except Exception as e:
        processing_jobs[job_id]['status'] = 'failed'
        processing_jobs[job_id]['error'] = str(e)
        traceback.print_exc()
    finally:
        # ensure progress exists
        processing_jobs[job_id].setdefault('progress', None)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "detector_initialized": detector is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models info"""
    if detector is None:
        return jsonify({"error": "Detector not initialized"}), 500
    
    return jsonify({
        "status": "success",
        "models": list(detector.models.keys()),
        "models_path": MODELS_PATH,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload and process video file"""
    try:
        # Check if file in request
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp + filename
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # Prepare output path
        output_filename = os.path.splitext(filename)[0] + "_detected.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Create job ID
        job_id = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + os.path.splitext(filename)[0]
        
        # Start background processing
        processing_jobs[job_id] = {
            'status': 'processing',
            'input_file': input_path,
            'output_file': output_path,
            'uploaded_at': datetime.now().isoformat(),
            'result': None,
            'error': None
        }
        
        thread = threading.Thread(
            target=process_video_background,
            args=(job_id, input_path, output_path)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "processing",
            "job_id": job_id,
            "message": "Video uploaded and processing started",
            "input_file": filename
        }), 202
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get processing job status"""
    if job_id not in processing_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    job = processing_jobs[job_id]
    return jsonify({
        "job_id": job_id,
        "status": job['status'],
        "result": job['result'],
        "error": job['error'],
        "uploaded_at": job['uploaded_at'],
        "progress": job.get('progress'),
        "has_preview": bool(job.get('preview_file')) and os.path.exists(job.get('preview_file', ''))
    })

@app.route('/api/preview/<job_id>', methods=['GET'])
def job_preview(job_id):
    """Get latest live preview frame for a job (jpg)."""
    if job_id not in processing_jobs:
        return jsonify({"error": "Job not found"}), 404

    preview_file = processing_jobs[job_id].get('preview_file')
    if not preview_file or not os.path.exists(preview_file):
        return jsonify({"error": "Preview not available"}), 404

    return send_file(preview_file, mimetype="image/jpeg", as_attachment=False)

@app.route('/api/_routes', methods=['GET'])
def list_routes():
    """Debug helper: list registered routes."""
    try:
        return jsonify({
            "routes": sorted([rule.rule for rule in app.url_map.iter_rules()])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<job_id>', methods=['GET'])
def download_result(job_id):
    """Download processed video"""
    if job_id not in processing_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    job = processing_jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({"error": f"Job status is {job['status']}, not completed"}), 400
    
    output_file = job['output_file']
    if not os.path.exists(output_file):
        return jsonify({"error": "Output file not found"}), 404
    
    return send_file(
        output_file,
        mimetype='video/mp4',
        as_attachment=True,
        download_name=os.path.basename(output_file)
    )

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all processing jobs"""
    return jsonify({
        "total_jobs": len(processing_jobs),
        "jobs": {
            job_id: {
                "status": job['status'],
                "uploaded_at": job['uploaded_at'],
                "error": job['error']
            }
            for job_id, job in processing_jobs.items()
        }
    })

@app.route('/api/cleanup/<job_id>', methods=['DELETE'])
def cleanup_job(job_id):
    """Clean up job files"""
    if job_id not in processing_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    job = processing_jobs[job_id]
    
    # Delete files
    try:
        if os.path.exists(job['input_file']):
            os.remove(job['input_file'])
        if os.path.exists(job['output_file']):
            os.remove(job['output_file'])
    except Exception as e:
        print(f"Error deleting files: {e}")
    
    # Remove from memory
    del processing_jobs[job_id]
    
    return jsonify({"status": "success", "message": "Job cleaned up"})

@app.route('/api/data-videos', methods=['GET'])
def list_data_videos():
    """List all videos in Data folder"""
    data_folder = "Data"
    if not os.path.exists(data_folder):
        return jsonify({"error": "Data folder not found"}), 404
    
    videos = []
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}
    
    try:
        for file in os.listdir(data_folder):
            if os.path.splitext(file)[1].lower() in video_extensions:
                file_path = os.path.join(data_folder, file)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                videos.append({
                    "filename": file,
                    "path": file_path,
                    "size_mb": round(file_size, 2)
                })
        
        return jsonify({
            "status": "success",
            "count": len(videos),
            "videos": videos
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-data-video', methods=['POST'])
def process_data_video():
    """Process a video from Data folder"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"error": "Filename required"}), 400
        
        input_path = os.path.join("Data", filename)
        
        if not os.path.exists(input_path):
            return jsonify({"error": f"Video not found: {filename}"}), 404
        
        # Prepare output path
        output_filename = os.path.splitext(filename)[0] + "_detected.mp4"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Create job ID
        job_id = datetime.now().strftime("%Y%m%d%H%M%S") + "_data_" + os.path.splitext(filename)[0]
        
        # Start background processing
        processing_jobs[job_id] = {
            'status': 'processing',
            'input_file': input_path,
            'output_file': output_path,
            'uploaded_at': datetime.now().isoformat(),
            'result': None,
            'error': None,
            'source': 'data_folder'
        }
        
        thread = threading.Thread(
            target=process_video_background,
            args=(job_id, input_path, output_path)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "processing",
            "job_id": job_id,
            "message": f"Processing video from Data folder: {filename}",
            "input_file": filename
        }), 202
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large"""
    return jsonify({"error": f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024} MB"}), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal errors"""
    return jsonify({"error": "Internal server error", "details": str(e)}), 500

# ============================================================
# REAL-TIME DETECTION ENDPOINTS
# ============================================================

@app.route('/api/detect/frame', methods=['POST'])
def detect_frame():
    """Detect objects in a single frame"""
    try:
        data = request.get_json()
        image_data = data.get('image_data')
        model_type = data.get('model_type', 'all')
        conf = data.get('conf', 0.6)
        iou = data.get('iou', 0.45)
        
        if not image_data or not detector:
            return jsonify({"error": "Missing image data or detector not initialized"}), 400
        
        # Decode base64 image and detect
        import base64
        import cv2
        import numpy as np
        
        # Accept raw base64 OR data URLs like "data:image/jpeg;base64,..."
        if isinstance(image_data, str) and "," in image_data and image_data.strip().startswith("data:"):
            image_data = image_data.split(",", 1)[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Clamp conf/iou to sane ranges
        try:
            conf = float(conf)
        except Exception:
            conf = 0.6
        try:
            iou = float(iou)
        except Exception:
            iou = 0.45
        conf = max(0.05, min(0.95, conf))
        iou = max(0.05, min(0.95, iou))

        raw_results = detector.detect_on_frame(frame, conf=conf, iou=iou)
        flat = detector.flatten_detections(raw_results)
        summary = {
            "weapons": len([d for d in flat if d.get('model') == 'weapon']),
            "garbage": len([d for d in flat if d.get('model') == 'garbage']),
            "hazards": len([d for d in flat if d.get('model') == 'hazard']),
            "total": len(flat),
        }

        return jsonify({
            "status": "success",
            "detections": flat,
            "detections_summary": summary,
            "params": {"conf": conf, "iou": iou},
            # Back-compat for any older UI code
            "weapon_count": summary["weapons"],
            "garbage_count": summary["garbage"],
            "hazard_count": summary["hazards"],
        })
    except Exception as e:
        print(f"Frame detection error: {e}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/detect/video', methods=['POST'])
def detect_video():
    """Detect objects in video file"""
    try:
        data = request.get_json()
        video_path = data.get('video_path')
        
        if not video_path or not os.path.exists(video_path):
            return jsonify({"error": "Invalid video path"}), 400
        
        if not detector:
            return jsonify({"error": "Detector not initialized"}), 500
        
        # Process video (no output file requested in this endpoint)
        results = detector.process_video_file(video_path)
        
        return jsonify({
            "status": "success",
            "video_path": video_path,
            "total_frames": results.get('total_frames', 0),
            "detections_summary": results.get("detections_summary", {
                "weapons": 0,
                "garbage": 0,
                "hazards": 0,
                "total": 0
            }),
            "detection_frames": results.get('detection_frames', [])
        })
    except Exception as e:
        print(f"Video detection error: {e}")
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/detect/stats', methods=['GET'])
def get_detection_stats():
    """Get overall detection statistics"""
    try:
        # Aggregate stats from all processed jobs
        weapon_total = 0
        garbage_total = 0
        hazard_total = 0
        
        for job_id, job in processing_jobs.items():
            if job['result'] and 'detections_summary' in job['result']:
                summary = job['result']['detections_summary']
                weapon_total += summary.get('weapons', 0)
                garbage_total += summary.get('garbage', 0)
                hazard_total += summary.get('hazards', 0)
        
        return jsonify({
            "weapons": weapon_total,
            "garbage": garbage_total,
            "hazards": hazard_total,
            "total_detections": weapon_total + garbage_total + hazard_total,
            "total_processed_videos": len(processing_jobs)
        })
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({
            "weapons": 0,
            "garbage": 0,
            "hazards": 0,
            "total_detections": 0
        })

@app.route('/api/models/status', methods=['GET'])
def get_models_status():
    """Get ML models status"""
    try:
        if not detector:
            return jsonify({"error": "Detector not initialized"}), 500
        
        return jsonify({
            "status": "ready",
            "models": {
                "weapon_detect": {
                    "status": "loaded" if "weapon" in detector.models else "missing",
                    "model_path": os.path.join(MODELS_PATH, "weapondetect.pt"),
                    "version": "YOLOv8"
                },
                "garbage_detect": {
                    "status": "loaded" if "garbage" in detector.models else "missing",
                    "model_path": os.path.join(MODELS_PATH, "garbage.pt"),
                    "version": "YOLOv8"
                },
                "hazard_detect": {
                    "status": "loaded" if "hazard" in detector.models else "missing",
                    "model_path": os.path.join(MODELS_PATH, "hazard.pt"),
                    "version": "YOLOv8"
                }
            }
        })
    except Exception as e:
        print(f"Models status error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/detect/batch', methods=['POST'])
def detect_batch():
    """Batch detect multiple videos"""
    try:
        data = request.get_json()
        video_paths = data.get('video_paths', [])
        
        if not video_paths:
            return jsonify({"error": "No video paths provided"}), 400
        
        results = []
        for video_path in video_paths:
            try:
                if os.path.exists(video_path):
                    detections = detector.process_video_file(video_path)
                    results.append({
                        "video_path": video_path,
                        "success": True,
                        "detections": detections
                    })
                else:
                    results.append({
                        "video_path": video_path,
                        "success": False,
                        "error": "Video file not found"
                    })
            except Exception as e:
                results.append({
                    "video_path": video_path,
                    "success": False,
                    "error": str(e)
                })
        
        return jsonify({
            "status": "completed",
            "total_videos": len(video_paths),
            "successful": len([r for r in results if r.get('success')]),
            "results": results
        })
    except Exception as e:
        print(f"Batch detection error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
