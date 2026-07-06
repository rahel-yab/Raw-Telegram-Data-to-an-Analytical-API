from fastapi import Depends, FastAPI, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.database import MARTS_SCHEMA, get_db
from api.schemas import (
    ChannelActivity,
    MessageSearchResult,
    TopProduct,
    VisualContentSummary,
)

app = FastAPI(title="Medical Telegram Analytical API", version="1.0.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/reports/top-products", response_model=list[TopProduct])
def top_products(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = text(
        f"""
        WITH terms AS (
            SELECT lower(match[1]) AS term
            FROM {MARTS_SCHEMA}.fct_messages,
            regexp_matches(message_text, '([[:alpha:]][[:alpha:]-]{{3,}})', 'g') AS match
            WHERE message_text IS NOT NULL
        )
        SELECT term, COUNT(*)::INT AS mention_count
        FROM terms
        GROUP BY term
        ORDER BY mention_count DESC, term
        LIMIT :limit
        """
    )
    return db.execute(query, {"limit": limit}).mappings().all()


@app.get("/api/channels/{channel_name}/activity", response_model=list[ChannelActivity])
def channel_activity(
    channel_name: str,
    limit: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    query = text(
        f"""
        SELECT
            CAST(message_date AS DATE) AS activity_date,
            COUNT(*)::INT AS post_count,
            COALESCE(SUM(view_count), 0)::INT AS total_views,
            COALESCE(SUM(forward_count), 0)::INT AS total_forwards
        FROM {MARTS_SCHEMA}.fct_messages messages
        JOIN {MARTS_SCHEMA}.dim_channels channels
            ON messages.channel_key = channels.channel_key
        WHERE channels.channel_name = :channel_name
        GROUP BY 1
        ORDER BY 1 DESC
        LIMIT :limit
        """
    )
    return db.execute(query, {"channel_name": channel_name, "limit": limit}).mappings().all()


@app.get("/api/search/messages", response_model=list[MessageSearchResult])
def search_messages(
    query: str = Query(min_length=2),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    statement = text(
        f"""
        SELECT
            messages.message_id,
            channels.channel_name,
            messages.message_date,
            messages.message_text,
            messages.view_count
        FROM {MARTS_SCHEMA}.fct_messages messages
        JOIN {MARTS_SCHEMA}.dim_channels channels
            ON messages.channel_key = channels.channel_key
        WHERE messages.message_text ILIKE :query
        ORDER BY messages.message_date DESC
        LIMIT :limit
        """
    )
    return db.execute(statement, {"query": f"%{query}%", "limit": limit}).mappings().all()


@app.get("/api/reports/visual-content", response_model=list[VisualContentSummary])
def visual_content(db: Session = Depends(get_db)):
    query = text(
        f"""
        SELECT
            channels.channel_name,
            COUNT(DISTINCT messages.message_key)::INT AS image_posts,
            COUNT(detections.detection_key)::INT AS detected_objects,
            COUNT(DISTINCT detections.object_label)::INT AS object_categories
        FROM {MARTS_SCHEMA}.fct_messages messages
        JOIN {MARTS_SCHEMA}.dim_channels channels
            ON messages.channel_key = channels.channel_key
        LEFT JOIN {MARTS_SCHEMA}.fct_image_detections detections
            ON messages.message_key = detections.message_key
        WHERE messages.has_image = TRUE
        GROUP BY channels.channel_name
        ORDER BY image_posts DESC
        """
    )
    return db.execute(query).mappings().all()
