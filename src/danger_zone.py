import cv2

# Load a single frame image instead of video
image_path = r"C:\Users\Sakshi\Documents\RailwaySafety\assets\boundary_railway.png"   # <-- save one frame from your video and put the path here
frame = cv2.imread(image_path)

clicked_points = []

def mouse_callback(event, x, y, flags, param):
    global clicked_points
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        print(f"Point selected: {x}, {y}")
        # Draw a marker where you clicked
        frame_copy = param.copy()
        cv2.circle(frame_copy, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Calibration", frame_copy)

cv2.namedWindow("Calibration")
cv2.setMouseCallback("Calibration", mouse_callback, frame)

print("Click on the yellow safety line (top edge). Press 'q' when done.")

while True:
    cv2.imshow("Calibration", frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cv2.destroyAllWindows()

# Save the line position
if clicked_points:
    SAFETY_LINE_Y = clicked_points[0][1]  # y coordinate of first click
    print(f"Configured safety line at Y = {SAFETY_LINE_Y}")
else:
    print("No point selected.")