from chatapp.models import PrivateChat
from django.test import TestCase
from django.urls import reverse
from factories.factories import ChatFactory, ChatParticipantFactory, UserFactory


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
        Test checks that participant from other chat get access forbidden when accessing chat he is not participant of
        """
        self.client.login(username=self.other_chat_participant.user.username, password="secret")
        response = self.client.get(reverse("chat", kwargs={"pk": self.chat.id}))
        self.assertEqual(response.status_code, 403)


class OpenPrivateChatViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.private_chat = ChatFactory()
        cls.participant_1 = ChatParticipantFactory(chat=cls.private_chat)
        cls.participant_2 = ChatParticipantFactory(chat=cls.private_chat)
        cls.participant_3 = ChatParticipantFactory()

    def test_should_return_correct_url_when_opening_existing_private_chat(self):
        self.client.login(username=self.participant_1.user.username, password="secret")
        response = self.client.get(reverse("open-chat", kwargs={"user_id": self.participant_2.user.id}))
        self.assertRedirects(response, reverse("chat", kwargs={"pk": self.private_chat.id}))

    def test_should_create_new_private_chat_and_return_correct_url_when_private_chat_does_exist(self):
        self.client.login(username=self.participant_1.user.username, password="secret")
        chat_before_request = (
            PrivateChat.objects.filter(participants__user=self.participant_1.user)
            .filter(participants__user=self.participant_3.user)
            .first()
        )
        self.assertIsNone(chat_before_request)
        response = self.client.get(reverse("open-chat", kwargs={"user_id": self.participant_3.user.id}))
        chat_after_request = (
            PrivateChat.objects.filter(participants__user=self.participant_1.user)
            .filter(participants__user=self.participant_3.user)
            .first()
        )
        self.assertRedirects(response, reverse("chat", kwargs={"pk": chat_after_request.id}))

    def test_should_return_404_when_one_participant_does_not_exist_and_does_not_create_new_chat(self):
        new_user = UserFactory()
        self.client.login(username=new_user.username, password="secret")
        response = self.client.get(reverse("open-chat", kwargs={"user_id": 99}))
        self.assertEqual(response.status_code, 404)
        chat = PrivateChat.objects.filter(participants__user=new_user).first()
        self.assertIsNone(chat)

    def test_should_return_error_when_private_chat_exists_in_duplicate(self):
        self.client.login(username=self.participant_1.user.username, password="secret")
        duplicate_private_chat = ChatFactory()
        ChatParticipantFactory(chat=duplicate_private_chat, user=self.participant_1.user)
        other_participant_2 = ChatParticipantFactory(chat=duplicate_private_chat, user=self.participant_2.user)
        response = self.client.get(reverse("open-chat", kwargs={"user_id": other_participant_2.user.id}))
        self.assertEqual(response.status_code, 404)
