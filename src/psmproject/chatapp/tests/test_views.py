from math import ceil

from chatapp.models import Chat, ComplaintChat, PrivateChat, RoleChoices, TaskChat
from django.test import TestCase
from django.urls import reverse
from factories.factories import (
    ChatFactory,
    ChatParticipantFactory,
    ComplaintChatFactory,
    ComplaintChatParticipantFactory,
    MessageFactory,
    TaskChatFactory,
    TaskChatParticipantFactory,
    UserFactory,
)


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
        """
        Test checks if view returns correct URL when private chat already exists between users.
        """
        self.client.login(username=self.participant_1.user.username, password="secret")
        response = self.client.get(reverse("open-chat", kwargs={"user_id": self.participant_2.user.id}))
        self.assertRedirects(response, reverse("chat", kwargs={"pk": self.private_chat.id}))

    def test_should_create_new_private_chat_and_return_correct_url_when_private_chat_does_exist(self):
        """
        Test checks if view returns correct URL when private chat does not exist yet between users and confirms that a
        new  chat was created.
        """
        self.client.login(username=self.participant_1.user.username, password="secret")
        response = self.client.get(reverse("open-chat", kwargs={"user_id": self.participant_3.user.id}))
        chat_after_request = (
            PrivateChat.objects.filter(participants__user=self.participant_1.user)
            .filter(participants__user=self.participant_3.user)
            .first()
        )
        self.assertIsNotNone(chat_after_request)
        self.assertRedirects(response, reverse("chat", kwargs={"pk": chat_after_request.id}))

    def test_should_return_404_when_contact_does_not_exist_and_does_not_create_new_chat(self):
        """
        Test checks if view returns 404 when user contacted does not exist and confirms that no new chat is created.
        """
        new_user = UserFactory()
        self.client.login(username=new_user.username, password="secret")
        nb_of_chats_before_request = len(PrivateChat.objects.all())
        response = self.client.get(reverse("open-chat", kwargs={"user_id": 99}))
        self.assertEqual(response.status_code, 404)
        nb_of_chats_after_request = len(PrivateChat.objects.all())
        self.assertEqual(nb_of_chats_before_request, nb_of_chats_after_request)

    def test_should_return_404_when_private_chat_exists_in_duplicate(self):
        """
        Test checks if view returns 404 when several chats were found for the same users.
        """
        self.client.login(username=self.participant_1.user.username, password="secret")
        duplicate_private_chat = ChatFactory()
        ChatParticipantFactory(chat=duplicate_private_chat, user=self.participant_1.user)
        other_participant_2 = ChatParticipantFactory(chat=duplicate_private_chat, user=self.participant_2.user)
        response = self.client.get(reverse("open-chat", kwargs={"user_id": other_participant_2.user.id}))
        self.assertEqual(response.status_code, 404)


class ChatListViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.private_chats = ChatFactory.create_batch(8)
        cls.user_1 = UserFactory.create()
        cls.empty_chat = cls.private_chats[0]
        for chat in cls.private_chats:
            cls.private_chat_participant_1 = ChatParticipantFactory(user=cls.user_1, chat=chat)
            ChatParticipantFactory(chat=chat)
            if chat is not cls.empty_chat:
                MessageFactory(chat=chat, author=cls.user_1)
        cls.task_chat = TaskChatFactory()
        cls.task_chat_participant_1 = TaskChatParticipantFactory(
            user=cls.user_1, chat=cls.task_chat, role=RoleChoices.CLIENT
        )
        cls.task_chat_participant_2 = TaskChatParticipantFactory(chat=cls.task_chat, role=RoleChoices.CONTRACTOR)
        MessageFactory(chat=cls.task_chat, author=cls.user_1)
        cls.complaint_chat = ComplaintChatFactory()
        cls.complaint_chat_participant_1 = ComplaintChatParticipantFactory(
            user=cls.user_1, chat=cls.complaint_chat, role=RoleChoices.CLIENT
        )
        cls.complaint_chat_participant_2 = ComplaintChatParticipantFactory(chat=chat, role=RoleChoices.CONTRACTOR)
        cls.complaint_chat_arbiter = ComplaintChatParticipantFactory(chat=chat, role=RoleChoices.ARBITER)
        cls.complaint_chat_moderator = ComplaintChatParticipantFactory(chat=chat, role=RoleChoices.MODERATOR)
        MessageFactory(chat=cls.complaint_chat, author=cls.user_1)

    def test_should_return_200_when_accessing_all_chats_view(self):
        """
        Test checks if all chats view returns status code 200
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("all-chats"))
        self.assertEqual(response.status_code, 200)

    def test_should_return_200_when_accessing_private_chats_view(self):
        """
        Test checks if private chats view returns status code 200
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("private-chats"))
        self.assertEqual(response.status_code, 200)

    def test_should_return_200_when_accessing_task_chats_view(self):
        """
        Test checks if task chats view returns status code 200
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("task-chats"))
        self.assertEqual(response.status_code, 200)

    def test_should_return_200_when_accessing_complaint_chats_view(self):
        """
        Test checks if complaint chats view returns status code 200
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("complaint-chats"))
        self.assertEqual(response.status_code, 200)

    def test_should_return_correct_list_title_when_accessing_all_chats_view(self):
        """
        Test checks if all chats view returns correct list title
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("all-chats"))
        self.assertEqual(response.context["list_title"], "All chats")

    def test_should_return_correct_list_title_when_accessing_private_chats_view(self):
        """
        Test checks if private chats view returns correct list title
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("private-chats"))
        self.assertEqual(response.context["list_title"], "Private chats")

    def test_should_return_correct_list_title_when_accessing_task_chats_view(self):
        """
        Test checks if task chats view returns correct list title
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("task-chats"))
        self.assertEqual(response.context["list_title"], "Task chats")

    def test_should_return_correct_list_title_when_accessing_complaint_chats_view(self):
        """
        Test checks if complaint chats view returns correct list title
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("complaint-chats"))
        self.assertEqual(response.context["list_title"], "Complaint chats")

    def test_should_return_all_chats_with_messages_only_when_accessing_all_chats_view(self):
        """
        Test checks if all chats view returns correct chat list, that means: logged user is participant to chat and
        chat has at least one message
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("all-chats"))
        all_chats = Chat.objects.filter(participants__user=self.user_1, messages__isnull=False).order_by("-pk")
        chat_list_from_view = response.context["page_obj"].paginator.object_list
        self.assertQuerysetEqual(chat_list_from_view, all_chats)
        self.assertNotIn(self.empty_chat, chat_list_from_view)

    def test_should_return_private_chats_with_messages_only_when_accessing_private_chats_view(self):
        """
        Test checks if private chats view returns correct chat list, that means: logged user is participant to chat and
        chat has at least one message
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("private-chats"))
        private_chats = PrivateChat.objects.filter(participants__user=self.user_1, messages__isnull=False).order_by(
            "-pk"
        )
        chat_list_from_view = response.context["page_obj"].paginator.object_list
        self.assertQuerysetEqual(chat_list_from_view, private_chats)
        self.assertNotIn(self.empty_chat, chat_list_from_view)

    def test_should_return_task_chats_with_messages_only_when_accessing_task_chats_view(self):
        """
        Test checks if task chats view returns correct chat list, that means: logged user is participant to chat and
        chat has at least one message
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("task-chats"))
        task_chats = TaskChat.objects.filter(participants__user=self.user_1, messages__isnull=False).order_by("-pk")
        chat_list_from_view = response.context["page_obj"].paginator.object_list
        self.assertQuerysetEqual(chat_list_from_view, task_chats)

    def test_should_return_complaint_chats_with_messages_only_when_accessing_complaint_chats_view(self):
        """
        Test checks if complaint chats view returns correct chat list, that means: logged user is participant to chat and
        chat has at least one message
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("complaint-chats"))
        complaint_chats = ComplaintChat.objects.filter(participants__user=self.user_1, messages__isnull=False).order_by(
            "-pk"
        )
        chat_list_from_view = response.context["page_obj"].paginator.object_list
        self.assertQuerysetEqual(chat_list_from_view, complaint_chats)

    def test_should_return_correct_number_of_page_when_paginated(self):
        """
        Test checks that view is paginated when it has more than 5 chats in view and returns correct number of pages
        """
        self.client.login(username=self.user_1.username, password="secret")
        response = self.client.get(reverse("all-chats"))
        self.assertTrue(response.context["is_paginated"])
        nb_of_chats = response.context["page_obj"].paginator.count
        nb_of_pages = response.context["page_obj"].paginator.num_pages
        self.assertEqual(ceil(nb_of_chats / 5), nb_of_pages)

    def test_should_return_no_chat_when_querying_user_that_does_not_exist(self):
        """
        Test checks if queryset is empty when searching user that does not exist among chat participants
        """
        self.client.login(username=self.user_1.username, password="secret")
        contact_name = "userdoesnotexist"
        response = self.client.get(f"{reverse('all-chats')}?contact_name={contact_name}")
        chat_list_from_view = response.context["chats"]
        self.assertFalse(chat_list_from_view)

    def test_should_return_correct_chat_when_querying_user_that_exists(self):
        """
        Test checks if view returns correct chat in which user that is in search query is participant
        """
        self.client.login(username=self.user_1.username, password="secret")
        contact_name = self.task_chat_participant_2.user.username
        response = self.client.get(f"{reverse('all-chats')}?contact_name={contact_name}")
        chat_returned = response.context["chats"][0]
        self.assertEqual(chat_returned, self.task_chat)

    def test_should_return_no_chat_when_querying_self_as_contact_name(self):
        """
        Test checks if queryset is empty when logged user searches himself among chat participants
        """
        self.client.login(username=self.user_1.username, password="secret")
        contact_name = self.user_1.username
        response = self.client.get(f"{reverse('all-chats')}?contact_name={contact_name}")
        chat_list_from_view = response.context["chats"]
        self.assertFalse(chat_list_from_view)

    def test_should_return_no_chat_when_querying_arbiter_as_contact_name(self):
        """
        Test checks if queryset is empty when searching arbiter among chat participants
        """
        self.client.login(username=self.user_1.username, password="secret")
        contact_name = self.complaint_chat_arbiter.user.username
        response = self.client.get(f"{reverse('all-chats')}?contact_name={contact_name}")
        chat_list_from_view = response.context["chats"]
        self.assertFalse(chat_list_from_view)

    def test_should_return_no_chat_when_querying_moderator_as_contact_name(self):
        """
        Test checks if queryset is empty when searching moderator among chat participants
        """
        self.client.login(username=self.user_1.username, password="secret")
        contact_name = self.complaint_chat_moderator.user.username
        response = self.client.get(f"{reverse('all-chats')}?contact_name={contact_name}")
        chat_list_from_view = response.context["chats"]
        self.assertFalse(chat_list_from_view)
