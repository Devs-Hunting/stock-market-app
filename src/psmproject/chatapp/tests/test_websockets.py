from datetime import datetime as dt
from datetime import timezone as tz

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from chatapp.consumers import ChatConsumer
from chatapp.models import Message
from chatapp.serializers import message_to_json
from django.test import TestCase, override_settings
from django.utils import timezone
from factories.factories import ChatFactory, ChatParticipantFactory, MessageFactory
from factory.fuzzy import FuzzyText
from mock import patch

TEST_CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


class WebsocketContextManager:
    def __init__(self, chat_id: int, participant: str):
        self.chat_id = chat_id
        self.participant = participant
        self.communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/testws/")

    async def __aenter__(self):
        self.communicator.scope["url_route"] = {"kwargs": {"pk": self.chat_id, "username": self.participant}}
        await self.communicator.connect()
        return self.communicator

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.communicator.disconnect()


@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
class ChatWebSocketTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.chat = ChatFactory()
        cls.chat_participant_1 = ChatParticipantFactory(chat=cls.chat)
        cls.chat_participant_2 = ChatParticipantFactory(chat=cls.chat)
        cls.other_chat = ChatFactory()
        cls.other_chat_participant = ChatParticipantFactory(chat=cls.other_chat)
        with patch.object(timezone, "now", return_value=dt(2023, 10, 8, 11, tzinfo=tz.utc)):
            cls.messages = MessageFactory.create_batch(10, chat=cls.chat)

    async def test_chat_consumer_connection(self):
        """
        Test checks if websocket connects correctly
        """
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/testws/")
        communicator.scope["url_route"] = {
            "kwargs": {"pk": self.chat.id, "username": self.chat_participant_1.user.username}
        }
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_should_return_sent_message_to_all_users_in_same_chat(self):
        """
        Test checks if the message sent to chat:
         - is received by all participants connected to this chat
         - is not received by participants of other chats
         - is saved in database
        """
        chat_id = self.chat.id
        other_chat_id = self.other_chat.id
        participant_1_username = self.chat_participant_1.user.username
        participant_2_username = self.chat_participant_2.user.username
        other_participant_username = self.other_chat_participant.user.username
        async with WebsocketContextManager(chat_id, participant_1_username) as c1, WebsocketContextManager(
            chat_id, participant_2_username
        ) as c2, WebsocketContextManager(other_chat_id, other_participant_username) as c3:
            message = {"action": "send_new_message", "author": participant_1_username, "content": "this is a test"}
            await c1.send_json_to(message)
            res1 = await c1.receive_json_from()
            res2 = await c2.receive_json_from()
            self.assertTrue(await c3.receive_nothing())
        self.assertEqual(message["action"], res1["action"])
        self.assertEqual(message["author"], res1["message"]["author"])
        self.assertEqual(message["content"], res1["message"]["content"])
        self.assertEqual(res1, res2)
        message_in_db = await Message.objects.filter(
            author=self.chat_participant_1.user.id, content=message["content"]
        ).afirst()
        self.assertTrue(message_in_db)

    async def test_should_return_error_when_message_content_longer_than_500(self):
        """
        Test checks if error is returned when message content is longer than that 500 characters
        """
        chat_id = self.chat.id
        participant_1_username = self.chat_participant_1.user.username
        async with WebsocketContextManager(chat_id, participant_1_username) as c1:
            content = FuzzyText(length=501).fuzz()
            message = {"action": "send_new_message", "author": participant_1_username, "content": content}
            await c1.send_json_to(message)
            res1 = await c1.receive_json_from()
        self.assertEqual(res1["action"], "throw_error")
        self.assertIn("error", res1.keys())

    async def test_should_return_message_history_only_to_user_that_requested_it(self):
        """
        Test checks when loading message history if:
         - 10 messages is returned
         - message that was sent after websocket connexion is not among the last 10 messages loaded from history
            (as it should be already displayed on chat)
         - other chat participants do not get chat history that was requested by one user
        """
        chat_id = self.chat.id
        participant_1_username = self.chat_participant_1.user.username
        participant_2_username = self.chat_participant_2.user.username
        async with WebsocketContextManager(chat_id, participant_1_username) as c1, WebsocketContextManager(
            chat_id, participant_2_username
        ) as c2:
            with patch.object(timezone, "now", return_value=dt(2023, 10, 10, 11, tzinfo=tz.utc)):
                new_message = await database_sync_to_async(MessageFactory.create)(chat=self.chat)
            with patch.object(timezone, "now", return_value=dt(2023, 10, 10, 10, tzinfo=tz.utc)) as mock_now:
                fetch_message = {
                    "action": "fetch_messages",
                    "chat_connection_timestamp": str(mock_now.return_value),
                    "visible_messages": 10,
                }
                await c1.send_json_to(fetch_message)
            result = await c1.receive_json_from()
            self.assertEqual(len(result["messages"]), 10)
            self.assertNotIn(await message_to_json(new_message), result["messages"])
            self.assertTrue(await c2.receive_nothing())
