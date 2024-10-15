from ultralytics import YOLO
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
# Load a YOLOv8 model (you can also load yolov8m.pt for the medium model, yolov8l.pt for large, etc.)
model = YOLO("yolov8s.pt")  # YOLOv8 small model pre-trained on COCO dataset

# Train the model
model.train(
    data=r"D:\OneDrive - Middlesex University\Middlesex University\Final dissertation\ATS_codes\Husky_lens_code\Auto_train\test.yaml",  # Path to the .yaml file defining your dataset
    epochs=50,                # Number of training epochs
    imgsz=640,                # Image size for training (YOLOv8 uses 640 by default)
    batch=16,                 # Batch size for training
    name="yolov8_custom"      # The name of the model or experiment
)
