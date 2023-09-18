from django.db import models


class MessageManager(models.Manager):
    def get_chat_message_history(self, *, chat_id, max_datetime, visible_messages):
        upper = visible_messages
        lower = visible_messages - 10
        messages = self.filter(chat=chat_id, timestamp__lte=max_datetime)[lower:upper]
        return messages
