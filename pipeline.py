import subprocess

from dagster import Definitions, job, op


def run_command(command: list[str], cwd: str | None = None):
    subprocess.run(command, cwd=cwd, check=True)


@op
def scrape_telegram():
    run_command(["python3", "src/scraper.py"])
    return "scraped"


@op
def load_raw_messages(_start: str):
    run_command(["python3", "scripts/load_to_postgres.py"])
    return "loaded"


@op
def transform_warehouse(_loaded: str):
    run_command(["dbt", "run"], cwd="medical_warehouse")
    run_command(["dbt", "test"], cwd="medical_warehouse")
    return "transformed"


@op
def enrich_images(_transformed: str):
    run_command(["python3", "scripts/object_detection.py", "--write-db"])
    return "enriched"


@job
def telegram_elt_job():
    loaded = load_raw_messages(scrape_telegram())
    transformed = transform_warehouse(loaded)
    enrich_images(transformed)


defs = Definitions(jobs=[telegram_elt_job])
