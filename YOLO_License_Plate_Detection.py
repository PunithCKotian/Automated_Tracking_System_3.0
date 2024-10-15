import cv2
from ultralytics import YOLO

# Load the YOLOv8 model with custom weights (replace 'path_to_weights' with the actual path to your trained weights)
model = YOLO(r"c:\Users\Punit\runs\detect\yolov8_custom9\weights\best.pt")  # Example: "runs/detect/exp/weights/best.pt"

# Open the webcam (use 0 for default webcam, or change to the index of your camera)
cap = cv2.VideoCapture(1)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Start video capture and detection
while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame.")
        break

    # Perform detection on the frame
    results = model(frame)

    # Draw the bounding boxes and labels on the frame
    annotated_frame = results[0].plot()  # Plot the detection on the frame

    # Display the resulting frame
    cv2.imshow('YOLOv8 Real-time Detection', annotated_frame)

    # Press 'q' to quit the video stream
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
