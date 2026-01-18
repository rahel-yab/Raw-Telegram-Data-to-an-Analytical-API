import os
import json
import pandas as pd
from sqlalchemy import create_engine, text

# Database connection string
# format: postgresql://user:password@host:port/dbname
engine = create_engine('postgresql://admin:password123@localhost:5432/medical_data')

def load_json_to_postgres():
    # Path to your data lake
    base_path = 'data/raw/telegram_messages'
    
    if not os.path.exists(base_path):
        print(f"Error: The path {base_path} does not exist.")
        return

    # 1. Create the 'raw' schema if it doesn't exist
    # SQLAlchemy 2.0 requires strings to be wrapped in text()
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.commit()  # Explicitly commit the schema creation
        print("✅ Schema 'raw' verified/created.")
    
    # 2. Loop through partitioned folders (YYYY-MM-DD)
    for date_folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, date_folder)
        
        # Skip if not a directory
        if not os.path.isdir(folder_path):
            continue
            
        for json_file in os.listdir(folder_path):
            if json_file.endswith('.json'):
                file_full_path = os.path.join(folder_path, json_file)
                
                with open(file_full_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if not data:
                            print(f"⚠️ Skipping {json_file}: File is empty.")
                            continue
                            
                        df = pd.DataFrame(data)
                        
                        # 3. Load into PostgreSQL raw table
                        # index=False prevents pandas from creating an extra column for row numbers
                        df.to_sql(
                            'telegram_messages', 
                            engine, 
                            schema='raw', 
                            if_exists='append', 
                            index=False
                        )
                        print(f"🚀 Loaded {len(df)} rows from {json_file}")
                        
                    except Exception as e:
                        print(f"❌ Failed to load {json_file}: {str(e)}")

if __name__ == "__main__":
    load_json_to_postgres()