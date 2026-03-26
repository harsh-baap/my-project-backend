from ultralytics import YOLO
import cv2

# Load YOLO model (auto downloads)
model = YOLO("DataModel/models/weapondetect.pt")

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Perform detection
    results = model(frame)

    # Draw results
    annotated_frame = results[0].plot()

    # Show output
    cv2.imshow("YOLO Object Detection", annotated_frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
