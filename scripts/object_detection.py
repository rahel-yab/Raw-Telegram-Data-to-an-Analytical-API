import os
import pandas as pd
from ultralytics import YOLO
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
engine = create_engine(f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}")
model = YOLO('yolov8n.pt') 

def detect_and_store():
    image_base_path = 'data/raw/images'
    output_dir = 'data/processed/detections' # To save visual results
    os.makedirs(output_dir, exist_ok=True)
    
    detection_results = []

    # 2. Process Images
    for channel in os.listdir(image_base_path):
        channel_path = os.path.join(image_base_path, channel)
        if not os.path.isdir(channel_path): continue

        for img_name in os.listdir(channel_path):
            img_path = os.path.join(channel_path, img_name)
            
            # Run YOLOv8 inference
            results = model(img_path, conf=0.5)

            for result in results:
                # Save the visual image with boxes (Useful for your report!)
                result.save(filename=os.path.join(output_dir, f"det_{img_name}"))
                
                for box in result.boxes:
                    detection_results.append({
                        'message_id': img_name.split('.')[0], 
                        'channel_name': channel,
                        'object_label': model.names[int(box.cls[0])],
                        'confidence': float(box.conf[0]),
                        # Add coordinates for extra detail
                        'x_min': float(box.xyxy[0][0]),
                        'y_min': float(box.xyxy[0][1]),
                        'x_max': float(box.xyxy[0][2]),
                        'y_max': float(box.xyxy[0][3])
                    })

    # 3. Load to Postgres
    if detection_results:
        df = pd.DataFrame(detection_results)
        df.to_sql('image_detections', engine, schema='raw', if_exists='replace', index=False)
        print(f"✅ Successfully processed images and updated 'raw.image_detections'")

if __name__ == "__main__":
    detect_and_store()