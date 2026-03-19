from ultralytics import YOLO
import cv2
import numpy as np
import winsound

# Load YOLO model
model = YOLO("yolov8n.pt")

# Open video
cap = cv2.VideoCapture("assets/platform_video.mp4")

alert_played = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Copy frame for processing
    display_frame = frame.copy()

    # ----------------------------
    # Detect yellow line using color mask
    # ----------------------------
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([35, 255, 255])

    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    edges = cv2.Canny(mask, 50, 150)

    lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength=100,maxLineGap=10)

    yellow_line_y = None

    if lines is not None:
        for line in lines:
            x1,y1,x2,y2 = line[0]
            cv2.line(display_frame,(x1,y1),(x2,y2),(0,255,255),3)
            yellow_line_y = y1
            break

    # ----------------------------
    # YOLO Object Detection
    # ----------------------------
    results = model(frame)

    train_detected = False

    for r in results:
        for box in r.boxes:

            cls = int(box.cls[0])
            label = model.names[cls]

            x1,y1,x2,y2 = map(int, box.xyxy[0])

            # Detect train
            if label == "train":
                train_detected = True
                cv2.rectangle(display_frame,(x1,y1),(x2,y2),(255,0,0),2)
                cv2.putText(display_frame,"Train",(x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0),2)

            # Detect person
            if label == "person":

                cv2.rectangle(display_frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.putText(display_frame,"Person",(x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

                if yellow_line_y is not None:

                    # Check if crossing yellow line
                    if y2 > yellow_line_y and not train_detected:

                        cv2.putText(display_frame,
                                    "WARNING: DO NOT CROSS YELLOW LINE",
                                    (50,50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1,
                                    (0,0,255),
                                    3)

                        if not alert_played:
                            winsound.Beep(1500,700)
                            alert_played = True

                    else:
                        alert_played = False

    cv2.imshow("Railway Platform Safety System", display_frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()