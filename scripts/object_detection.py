import os
import argparse
import pandas as pd
from ultralytics import YOLO
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DEFAULT_DSN = os.getenv(
    "POSTGRES_DSN",
    f"postgresql://{os.getenv('DB_USER', 'admin')}:{os.getenv('DB_PASSWORD', 'password123')}@localhost:5433/{os.getenv('DB_NAME', 'medical_data')}",
)


def detect_and_store(
    images_dir: str,
    output_dir: str,
    database_url: str,
    model_name: str,
    confidence: float,
    write_db: bool,
) -> pd.DataFrame:
    model = YOLO(model_name)
    os.makedirs(output_dir, exist_ok=True)

    detection_results = []

    for channel in sorted(os.listdir(images_dir)):
        channel_path = os.path.join(images_dir, channel)
        if not os.path.isdir(channel_path):
            continue

        for img_name in sorted(os.listdir(channel_path)):
            img_path = os.path.join(channel_path, img_name)
            if not img_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue

            results = model(img_path, conf=confidence)

            for result in results:
                result.save(filename=os.path.join(output_dir, f"det_{img_name}"))

                for box in result.boxes:
                    detection_results.append({
                        'message_id': int(os.path.splitext(img_name)[0]),
                        'channel_name': channel,
                        'object_label': model.names[int(box.cls[0])],
                        'confidence': float(box.conf[0]),
                        'x_min': float(box.xyxy[0][0]),
                        'y_min': float(box.xyxy[0][1]),
                        'x_max': float(box.xyxy[0][2]),
                        'y_max': float(box.xyxy[0][3])
                    })

    df = pd.DataFrame(detection_results)
    csv_path = os.path.join(output_dir, "detections.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ Wrote {len(df)} detections to {csv_path}")

    if write_db and not df.empty:
        engine = create_engine(database_url)
        df.to_sql('image_detections', engine, schema='raw', if_exists='replace', index=False)
        print("✅ Updated raw.image_detections")

    return df


def parse_args():
    parser = argparse.ArgumentParser(description="Run YOLOv8 object detection on scraped images.")
    parser.add_argument("--images-dir", default="data/raw/images")
    parser.add_argument("--output-dir", default="data/processed/detections")
    parser.add_argument("--database-url", default=DEFAULT_DSN)
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--confidence", type=float, default=0.5)
    parser.add_argument("--write-db", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    detect_and_store(
        images_dir=args.images_dir,
        output_dir=args.output_dir,
        database_url=args.database_url,
        model_name=args.model,
        confidence=args.confidence,
        write_db=args.write_db,
    )
