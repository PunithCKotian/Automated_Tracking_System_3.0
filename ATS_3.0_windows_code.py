#This is the final windows code for object reckognition, and is been renamed aas final windows code
#This file is where the weights have been saved model = YOLO(r"c:\Users\Punit\runs\detect\yolov8_custom9\weights\best.pt")
#
import socket
import cv2
from ultralytics import YOLO
import pyrealsense2 as rs
import numpy as np

# Raspberry Pi connection details
raspberry_pi_ip = '172.20.10.2'  # Replace with your Pi's IP
port = 5005  # Port number

# Create a socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Load the YOLOv8 model with custom weights
model = YOLO(r"c:\Users\Punit\runs\detect\yolov8_custom9\weights\best.pt")

# Configure RealSense camera
pipeline = rs.pipeline()
config = rs.config()

# Enable the camera streams (color and depth)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Start the pipeline
pipeline.start(config)

# Align depth frames to color frames
align_to = rs.stream.color
align = rs.align(align_to)

try:
    while True:
        # Wait for frames
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # Make a copy of the color image to annotate
        annotated_frame = color_image.copy()

        # Perform detection
        results = model(color_image)

        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            if 0 <= center_x < depth_image.shape[1] and 0 <= center_y < depth_image.shape[0]:
                distance = depth_frame.get_distance(center_x, center_y)

                # Send coordinates and distance to Raspberry Pi
                data = f"{center_x},{center_y},{distance:.2f}"
                sock.sendto(data.encode(), (raspberry_pi_ip, port))

                # Draw bounding box and text
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"({center_x},{center_y}) {distance:.2f}m"
                cv2.putText(annotated_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Show the annotated frame
        cv2.imshow('YOLOv8 Real-time Detection with RealSense', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipeline.stop()
    sock.close()

cv2.destroyAllWindows()
