#!/usr/bin/env python3
import os
import json
import asyncio
import logging
import argparse
from datetime import datetime
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION = os.getenv("TELEGRAM_SESSION", "telegram_session")
DATA_DIR = os.getenv("DATA_DIR", "data/raw/telegram_messages")
IMAGES_DIR = os.getenv("IMAGES_DIR", "data/raw/images")
LOG_PATH = os.getenv("LOG_PATH", "logs/scraper.log")

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_CHANNELS = ["lobelia4cosmetics", "tikvahpharma"]

async def fetch_channel(client, channel, limit=None):
    messages_by_date = {}
    try:
        async for message in client.iter_messages(channel, limit=limit):
            if message is None:
                continue
            msg_id = getattr(message, "id", None)
            msg_date = getattr(message, "date", None)
            if msg_date is None:
                continue
            date_key = msg_date.strftime("%Y-%m-%d")
            msg = {
                "message_id": msg_id,
                "channel_name": str(channel),
                "message_date": msg_date.isoformat(),
                "message_text": message.message or "",
                "views": getattr(message, "views", 0) or 0,
                "forwards": getattr(message, "forwards", 0) or 0,
                "has_media": bool(message.media is not None),
                "image_path": None,
            }
            if hasattr(message, "photo") and message.photo:
                img_dir = os.path.join(IMAGES_DIR, str(channel))
                os.makedirs(img_dir, exist_ok=True)
                image_path = os.path.join(img_dir, f"{msg_id}.jpg")
                try:
                    await client.download_media(message.photo, file=image_path)
                    msg["image_path"] = image_path
                except Exception as e:
                    logger.exception(f"Failed downloading image for {channel}@{msg_id}: {e}")
                    msg["image_path"] = None
            messages_by_date.setdefault(date_key, []).append(msg)
        for date_key, msgs in messages_by_date.items():
            out_dir = os.path.join(DATA_DIR, date_key)
            os.makedirs(out_dir, exist_ok=True)
            out_file = os.path.join(out_dir, f"{channel}.json")
            if os.path.exists(out_file):
                try:
                    with open(out_file, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                except Exception:
                    existing = []
                existing.extend(msgs)
                msgs_to_write = existing
            else:
                msgs_to_write = msgs
            with open(out_file, "w", encoding='utf-8') as f:
                json.dump(msgs_to_write, f, ensure_ascii=False, default=str, indent=2)
        logger.info(f"Scraped channel {channel}, dates={list(messages_by_date.keys())}")
    except Exception as e:
        logger.exception(f"Error scraping channel {channel}: {e}")

async def main(channels, limit):
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start()
    for channel in channels:
        await fetch_channel(client, channel, limit=limit)
    await client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channels", nargs="+", help="Channel usernames or URLs", default=DEFAULT_CHANNELS)
    parser.add_argument("--limit", type=int, help="Max messages per channel (default all)", default=None)
    args = parser.parse_args()
    asyncio.run(main(args.channels, args.limit))
