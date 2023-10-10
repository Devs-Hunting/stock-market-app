from django.test import TestCase
from django.urls import reverse
from factories.factories import ChatFactory, ChatParticipantFactory


class ChatViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.chat = ChatFactory()
        cls.chat_participant = ChatParticipantFactory(chat=cls.chat)
        cls.other_chat_participant = ChatParticipantFactory()

    def test_should_return_200_when_chat_participant_access_chat(self):
        """
        Test checks if chat participant can access chat
        """
        self.client.login(username=self.chat_participant.user.username, password="secret")
        response = self.client.get(reverse("chat", kwargs={"pk": self.chat.id}))
        self.assertEqual(response.status_code, 200)

    def test_should_return_403_when_non_chat_participant_access_chat(self):
        """
        Test checks if participant from other chat can access chat he is not participant of
        """
        self.client.login(username=self.other_chat_participant.user.username, password="secret")
        response = self.client.get(reverse("chat", kwargs={"pk": self.chat.id}))
        self.assertEqual(response.status_code, 403)
