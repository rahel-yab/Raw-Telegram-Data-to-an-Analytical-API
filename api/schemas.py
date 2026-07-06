from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class TopProduct(BaseModel):
    term: str
    mention_count: int


class ChannelActivity(BaseModel):
    activity_date: date
    post_count: int
    total_views: int
    total_forwards: int


class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_date: datetime
    message_text: Optional[str] = None
    view_count: int


class VisualContentSummary(BaseModel):
    channel_name: str
    image_posts: int
    detected_objects: int
    object_categories: int
