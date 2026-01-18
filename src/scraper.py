import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient

# Load credentials
load_dotenv()
API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')

# Target channels
CHANNELS = [
    'chemed_telegram', 
    'lobelia4cosmetics', 
    'tikvahpharma'
]

# Set up logging
logging.basicConfig(
    filename='logs/scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def scrape_channel(client, channel_username):
    try:
        logging.info(f"Scraping channel: {channel_username}")
        entity = await client.get_entity(channel_username)
        
        # Partitioned JSON directory
        date_str = datetime.now().strftime('%Y-%m-%d')
        json_dir = f'data/raw/telegram_messages/{date_str}'
        os.makedirs(json_dir, exist_ok=True)
        
        messages_data = []

        async for message in client.iter_messages(entity, limit=100):
            # Extract basic data
            msg_id = message.id
            payload = {
                "message_id": msg_id,
                "channel_name": channel_username,
                "message_date": str(message.date),
                "message_text": message.text,
                "has_media": bool(message.media),
                "views": message.views,
                "forwards": message.forwards,
            }

            # Handle Image Download
            if message.photo:
                img_path = f'data/raw/images/{channel_username}'
                os.makedirs(img_path, exist_ok=True)
                filename = f"{img_path}/{msg_id}.jpg"
                await client.download_media(message, file=filename)
                payload["image_path"] = filename
            
            messages_data.append(payload)

        # Save partitioned JSON
        with open(f"{json_dir}/{channel_username}.json", 'w', encoding='utf-8') as f:
            json.dump(messages_data, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        logging.error(f"Error in {channel_username}: {str(e)}")

async def main():
    async with TelegramClient('scraping_session', API_ID, API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())