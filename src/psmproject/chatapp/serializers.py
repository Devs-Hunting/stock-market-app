from typing import Dict, List

from channels.db import database_sync_to_async
from chatapp.models import Message
from chatapp.utils.timestamp_to_string import timestamp_to_str
from django.db.models import QuerySet


async def messages_to_json(messages: QuerySet) -> List[Dict]:
    return [await message_to_json(message) async for message in messages]


async def message_to_json(message: Message) -> Dict:
    return {
        "author": await database_sync_to_async(lambda: message.author_username)(),
        "content": message.content,
        "picture": await database_sync_to_async(lambda: message.author_profile_picture_url)(),
        "timestamp": timestamp_to_str(message.timestamp),
    }
