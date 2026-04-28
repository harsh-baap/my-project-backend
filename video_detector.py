"""
Video Detection Module - Simultaneous multi-model detection
Supports: video files, webcam, and real-time streaming
"""

from ultralytics import YOLO
import cv2
import os
from pathlib import Path
import json
from datetime import datetime

class VideoDetector:
    def __init__(self, models_path="DataModel/models"):
        """Initialize all detection models"""
        self.models_path = models_path

        self.garbage_model = self._try_load_model("garbage.pt")
        self.hazard_model = self._try_load_model("hazard.pt")

        # Weapon weights name varies across docs/repos; support both.
        self.weapon_model = (
            self._try_load_model("weapondetect.pt")
            or self._try_load_model("weapon.pt")
        )

        self.models = {}
        if self.garbage_model:
            self.models["garbage"] = self.garbage_model
        if self.hazard_model:
            self.models["hazard"] = self.hazard_model
        if self.weapon_model:
            self.models["weapon"] = self.weapon_model

        if not self.models:
            raise FileNotFoundError(
                f"No YOLO model weights found in '{models_path}'. "
                "Expected at least one of: garbage.pt, hazard.pt, weapondetect.pt/weapon.pt"
            )

    def _try_load_model(self, filename: str):
        model_path = os.path.join(self.models_path, filename)
        if not os.path.exists(model_path):
            return None
        return YOLO(model_path)

    def detect_on_frame(self, frame, imgsz=320, conf=0.6, iou=0.45):
        """Run all available models on a single frame."""
        results = {}
        for model_name, model in self.models.items():
            # Ultralytics returns a list[Results]
            results[model_name] = model(frame, imgsz=imgsz, conf=conf, iou=iou, verbose=False)
        return results

    def flatten_detections(self, results):
        """
        Convert Ultralytics results into a flat, JSON-friendly list.
        Each detection: {model, class, class_id, conf, xyxy}.
        """
        flat = []
        for model_name, model_results in (results or {}).items():
            if not model_results:
                continue
            r0 = model_results[0]
            names = getattr(r0, "names", {}) or {}
            boxes = getattr(r0, "boxes", None)
            if boxes is None or len(boxes) == 0:
                continue

            xyxy = boxes.xyxy.tolist() if getattr(boxes, "xyxy", None) is not None else []
            conf = boxes.conf.tolist() if getattr(boxes, "conf", None) is not None else []
            cls = boxes.cls.tolist() if getattr(boxes, "cls", None) is not None else []

            for i in range(len(xyxy)):
                class_id = int(cls[i]) if i < len(cls) else -1
                flat.append(
                    {
                        "model": model_name,
                        "class": names.get(class_id, str(class_id)),
                        "class_id": class_id,
                        "conf": float(conf[i]) if i < len(conf) else None,
                        "xyxy": [float(v) for v in xyxy[i]],
                    }
                )
        return flat

    def plot_results(self, frame, results):
        """Plot all detection results on frame"""
        output = frame.copy()
        for model_name, model_results in results.items():
            if model_results and len(model_results) > 0:
                output = model_results[0].plot(img=output)
        return output

    def process_video_file(self, input_path, output_path=None, imgsz=320):
        """
        Process a video file with simultaneous detection
        
        Args:
            input_path: Path to input video
            output_path: Path to save output video (optional)
            imgsz: Detection image size
            
        Returns:
            dict with detection statistics
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Video file not found: {input_path}")

        cap = cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {input_path}")

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Setup video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0
        detections = {name: 0 for name in self.models.keys()}
        detections["total_frames"] = 0
        
        # Optional hook for callers (e.g., dashboard live preview)
        progress_callback = None
        if isinstance(imgsz, dict):
            # Back-compat: allow passing options as dict without breaking callers
            progress_callback = imgsz.get("progress_callback")
            imgsz = imgsz.get("imgsz", 320)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                detections["total_frames"] = frame_count

                # Run detection
                try:
                    results = self.detect_on_frame(frame, imgsz=imgsz)
                    output_frame = self.plot_results(frame, results)
                    
                    # Count detections
                    for model_name, model_results in results.items():
                        if model_results and len(model_results) > 0:
                            detections[model_name] += len(model_results[0].boxes)
                    
                    # Write to output video
                    if writer:
                        writer.write(output_frame)

                    if progress_callback:
                        try:
                            progress_callback(frame_count, total_frames, output_frame)
                        except Exception:
                            # Preview updates must never break processing
                            pass
                        
                except Exception as e:
                    print(f"Error processing frame {frame_count}: {str(e)}")
                    if writer:
                        writer.write(frame)
                    continue

                # Progress callback
                progress = (frame_count / total_frames) * 100
                if frame_count % 30 == 0:  # Every 30 frames
                    print(f"Processing: {progress:.1f}% ({frame_count}/{total_frames})")

        finally:
            cap.release()
            if writer:
                writer.release()

        return {
            "status": "success",
            "input_file": input_path,
            "output_file": output_path,
            "total_frames": frame_count,
            "fps": fps,
            "resolution": f"{width}x{height}",
            "detections": detections,
            "detections_summary": {
                "weapons": int(detections.get("weapon", 0)),
                "garbage": int(detections.get("garbage", 0)),
                "hazards": int(detections.get("hazard", 0)),
                "total": int(
                    (detections.get("weapon", 0))
                    + (detections.get("garbage", 0))
                    + (detections.get("hazard", 0))
                ),
            },
            "timestamp": datetime.now().isoformat()
        }

    def process_webcam(self, duration=None, display=True):
        """
        Process webcam feed with simultaneous detection
        
        Args:
            duration: Duration in seconds (None for infinite)
            display: Whether to display the feed
        """
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            raise ValueError("Cannot open webcam")

        frame_count = 0
        detections = {"garbage": 0, "hazard": 0, "weapon": 0}
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1

                # Run simultaneous detection
                results = self.detect_on_frame(frame)
                output_frame = self.plot_results(frame, results)

                # Count detections
                for model_name, model_results in results.items():
                    if model_results and len(model_results) > 0:
                        detections[model_name] += len(model_results[0].boxes)

                if display:
                    cv2.imshow("Combined Detection", output_frame)

                if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                    break

                if duration and frame_count > (30 * duration):  # Assuming 30 FPS
                    break

        finally:
            cap.release()
            if display:
                cv2.destroyAllWindows()

        return {
            "status": "success",
            "total_frames": frame_count,
            "detections": detections
        }


# Command-line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Detection with Multiple Models")
    parser.add_argument("--input", type=str, help="Input video file path")
    parser.add_argument("--output", type=str, help="Output video file path")
    parser.add_argument("--webcam", action="store_true", help="Use webcam instead of file")
    parser.add_argument("--models-path", type=str, default="DataModel/models", help="Path to models directory")
    
    args = parser.parse_args()
    
    detector = VideoDetector(models_path=args.models_path)
    
    if args.webcam:
        result = detector.process_webcam()
    elif args.input:
        result = detector.process_video_file(args.input, args.output)
    else:
        print("Please specify --input or --webcam")
        parser.print_help()
        exit(1)
    
    print(json.dumps(result, indent=2))
