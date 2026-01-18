import os
import json
import pandas as pd
from sqlalchemy import create_engine

# Database connection string
# format: postgresql://user:password@host:port/dbname
engine = create_engine('postgresql://admin:password123@localhost:5432/medical_data')

def load_json_to_postgres():
    base_path = 'data/raw/telegram_messages'
    
    # Create the 'raw' schema if it doesn't exist
    with engine.connect() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    
    # Loop through partitioned folders
    for date_folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, date_folder)
        
        for json_file in os.listdir(folder_path):
            with open(os.path.join(folder_path, json_file), 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                
                # Load into PostgreSQL raw table
                df.to_sql('telegram_messages', engine, schema='raw', if_exists='append', index=False)
                print(f"Loaded {len(df)} rows from {json_file}")

if __name__ == "__main__":
    load_json_to_postgres()