import cv2
import numpy as np
from ultralytics import YOLO
import winsound

# Load YOLO model
model = YOLO("yolov8n.pt")

# Open video file
video_path = "assets/platform.mp4"
cap = cv2.VideoCapture(video_path)

alert_cooldown = 0

# ---------------------------------------------------------
# DANGER ZONE POLYGON (your latest calibration points)
# ---------------------------------------------------------
danger_zone = np.array([
    (1, 488), (181, 443), (317, 409), (424, 382),
    (461, 373), (475, 369), (471, 402), (398, 426),
    (271, 470), (156, 510), (69, 539), (0, 565),
    (2, 563), (2, 519)
], dtype=np.int32)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    display_frame = frame.copy()

    # ---------------------------------------------------------
    # OBJECT DETECTION
    # ---------------------------------------------------------
    results = model(frame, verbose=False)
    train_present = False

    # Detect train
    for r in results:
        for box in r.boxes:
            if model.names[int(box.cls[0])] == "train":
                train_present = True

    # Detect people
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            if model.names[cls_id] == "person":
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Filter out distant/small detections
                if (x2 - x1) * (y2 - y1) < 5000:
                    continue

                box_color = (0, 255, 0)  # green = safe

                if not train_present:
                    # Person’s feet point
                    feet_point = (int((x1 + x2) / 2), y2)

                    # Check if inside danger zone polygon
                    if cv2.pointPolygonTest(danger_zone, feet_point, False) >= 0:
                        box_color = (0, 0, 255)  # red = danger
                        cv2.putText(display_frame, "WARNING: CROSSING", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                        if alert_cooldown == 0:
                            winsound.Beep(1000, 250) 
                            alert_cooldown = 10

                cv2.rectangle(display_frame, (x1, y1), (x2, y2), box_color, 2)

    # Reduce alert cooldown
    if alert_cooldown > 0:
        alert_cooldown -= 1

    # ---------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------
    cv2.imshow("Railway Platform Monitor", display_frame)

    key = cv2.waitKey(1)
    if key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()