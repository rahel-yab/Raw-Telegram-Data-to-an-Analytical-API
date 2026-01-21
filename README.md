# 🏥 Medical Telegram Warehouse — ELT Pipeline 

## Project Overview

An end-to-end ELT pipeline that ingests public Telegram messages from Ethiopian medical channels, enriches images with YOLOv8 object detection, transforms data with dbt into a dimensional star schema, and exposes analytics via a FastAPI service. The project is reproducible locally with Docker Compose and orchestrated with Dagster.

## What the system provides

- A partitioned data lake of raw Telegram messages and downloaded media (images).
- Image enrichment using YOLOv8 (object detections + categories).
- A PostgreSQL data warehouse with dbt models producing dimensions and facts optimized for analytics.
- Data quality enforced via dbt tests (including custom business tests).
- An analytical API (FastAPI) exposing endpoints for reports and searches.
- Dagster orchestration for scheduled and observable runs.

## Architecture overview

1. Extract — `src/scraper.py` (Telethon) scrapes public channels and writes JSON + images to `data/raw/`.
2. Load — `scripts/load_to_postgres.py` loads raw JSON into Postgres `raw.telegram_messages`.
3. Transform — `medical_warehouse/` (dbt) builds staging models and marts (star schema).
4. Enrich — `src/yolo_detect.py` runs YOLOv8 on images and records detections.
5. Serve — `api/main.py` (FastAPI) exposes analytical endpoints.
6. Orchestrate — `pipeline.py` (Dagster) composes ops and schedules runs.

## Repository layout

```
.
├── data/                   # Data lake (raw JSON, images, detections)
├── logs/                   # Scraper and pipeline logs
├── src/                    # Scraper and enrichment scripts
├── scripts/                # Loaders and utility scripts
├── medical_warehouse/      # dbt project (models, tests, docs)
├── api/                    # FastAPI application
├── pipeline.py             # Dagster job definition
├── docker-compose.yml      # Local Postgres for development
├── .env.example            # Placeholder env vars
└── requirements.txt
```

## Quickstart (local)

Prerequisites: Docker, Docker Compose, Python 3.10+, virtualenv.

1. Copy `.env.example` to `.env` and fill secrets (do not commit `.env`).

```bash
cp .env.example .env
# edit .env to set DB_USER, DB_PASSWORD, DB_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH
```

2. Start Postgres:

```bash
docker-compose up -d
```

3. Prepare Python environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install dbt-postgres
```

4. Scrape Telegram channels (example):

```bash
python src/scraper.py --channels lobelia4cosmetics tikvahpharma --limit 100
```

5. Load raw JSON into Postgres:

```bash
export POSTGRES_DSN=postgresql://$DB_USER:$DB_PASSWORD@localhost:55432/$DB_NAME
python scripts/load_to_postgres.py --data-dir data/raw/telegram_messages
```

6. Run dbt transformations and tests:

```bash
cd medical_warehouse
dbt deps
dbt seed   # if seeds exist
dbt run
dbt test
dbt docs generate
dbt docs serve
```

7. Run YOLO enrichment:

```bash
python src/yolo_detect.py --images-dir data/raw/images --output data/processed/detections.csv
```

8. Start the FastAPI analytical API:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

9. Orchestrate with Dagster (local dev):

```bash
dagster dev -f pipeline.py
# open Dagster UI to trigger/schedule jobs
```

## dbt models & tests

- Staging models: `medical_warehouse/models/staging/stg_telegram_messages.sql` (casts, cleans, adds helper columns).
- Marts: `medical_warehouse/models/marts/` (`dim_channels`, `dim_dates`, `fct_messages`, `fct_image_detections`).
- Tests: uniqueness, not_null, relationships, and custom tests (`assert_no_future_messages.sql`, `assert_positive_views.sql`).

## API endpoints (examples)

- `GET /api/reports/top-products?limit=10` — most frequently mentioned products/terms
- `GET /api/channels/{channel_name}/activity` — posting and view trends
- `GET /api/search/messages?query=paracetamol&limit=20` — message search
- `GET /api/reports/visual-content` — image usage and categories per channel

Responses use Pydantic schemas for validation and include pagination and filtering options.

## Observability & testing

- Logs: `logs/` captures scraper and pipeline logs.
- Dagster UI: run history, logs, and retries.
- dbt docs: model lineage and documentation.
- CI: unit tests and dbt tests run on pull requests.

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository and create a branch (`feat/your-feature`).
2. Open an issue describing the change if it is non-trivial.
3. Add tests for new functionality (unit tests or dbt tests as appropriate).
4. Submit a pull request with a clear description and any migration or run instructions.

