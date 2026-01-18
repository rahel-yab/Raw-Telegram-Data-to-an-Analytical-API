# Medical Data Warehouse: Telegram ELT Pipeline

This project is a modern Data Engineering pipeline designed to extract, load, and transform data from Ethiopian medical Telegram channels. It follows an ELT (Extract, Load, Transform) architecture, moving from raw unstructured data to a structured, analytical star schema.

🛠 Progress Overview

Task 1: Data Scraping and Collection (Extract & Load)
We have successfully built a "Data Lake" of raw information from three major Telegram channels: chemed_telegram, lobelia4cosmetics, and tikvahpharma.

Scraper Engine: Built using Telethon (Python) to interact with the Telegram API.

Data Lake Structure:

Raw Messages: Stored as partitioned JSON files (data/raw/telegram_messages/YYYY-MM-DD/channel.json).

Raw Images: Downloaded and organized by channel for future YOLO enrichment.

Logging: Implemented a robust logging system in logs/scraping.log to track successful runs and API rate limits.

Task 2: Data Modeling and Transformation (Transform)
We have initiated the transformation layer using dbt and PostgreSQL.

Infrastructure: Spun up a PostgreSQL 15 database using Docker Compose.

Orchestration: Configured profiles.yml and dbt_project.yml to securely connect our project to the data warehouse.

Environment: Set up a virtual environment and a .env file to manage secrets like API credentials and database passwords.

📂 Current Project Structure

```text
medical-telegram-warehouse/
├── data/
│   └── raw/
│       ├── images/            # Downloaded product photos
│       └── telegram_messages/ # Partitioned JSON messages
├── logs/                      # Scraping history and error logs
├── src/
│   └── scraper.py             # Main Telethon scraper script
├── medical_warehouse/         # dbt project folder
│   ├── models/
│   │   ├── staging/           # Raw data cleaning logic (Next Step)
│   │   └── marts/             # Final analytical tables (Next Step)
│   └── dbt_project.yml        # dbt configuration
├── docker-compose.yml         # Postgres container setup
├── .env                       # Secrets (API_ID, API_HASH, DB_PASS)
└── requirements.txt           # Python dependencies
```


🚀 How to Run
Start the Database:

```bash
docker-compose up -d
```
Run the Scraper:

```bash
python src/scraper.py
```
Verify dbt Connection:

```bash
cd medical_warehouse
dbt debug
```
📈 Next Milestones
[ ] Load: Execute the Python script to push raw JSON data into the Postgres raw schema.

[ ] Staging: Write SQL models to cast data types (dates, views) and clean text.

[ ] Star Schema: Build dim_channels and fct_messages tables for the business report.

Author: Rahel Status: Task 1 Complete | Task 2 In-Progress

