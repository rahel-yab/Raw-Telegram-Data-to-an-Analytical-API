import os
import cv2
from ultralytics import YOLO

# Load a pre-trained YOLOv8 nano model (lightweight and fast)
model = YOLO('yolov8n.pt') 

def run_detection():
    image_dir = 'data/raw/images'
    output_dir = 'data/processed/detections'
    os.makedirs(output_dir, exist_ok=True)

    for channel in os.listdir(image_dir):
        channel_path = os.path.join(image_dir, channel)
        if not os.path.isdir(channel_path): continue

        for img_name in os.listdir(channel_path):
            img_path = os.path.join(channel_path, img_name)
            
            # Run inference
            results = model(img_path)

            # Save results (this saves a copy of the image with boxes drawn on it)
            for result in results:
                result.save(filename=os.path.join(output_dir, f"det_{img_name}"))
                
                # Print what was found (e.g., "bottle: 0.85")
                for box in result.boxes:
                    print(f"Channel: {channel} | Found: {model.names[int(box.cls[0])]} with {box.conf[0]:.2f} confidence")

if __name__ == "__main__":
    run_detection()